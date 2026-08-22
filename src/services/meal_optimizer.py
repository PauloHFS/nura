import numpy as np
from scipy.optimize import linprog
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from src.domain.ports.meal_optimizer_port import MealOptimizerPort
from src.adapters.chroma_adapter import ChromaNutritionalRepository
from src.adapters.usda_tbca_dataset import SEED_NUTRITIONAL_DATA

class OptimizationRequest(BaseModel):
    target_calories: float = Field(gt=0, description="Meta calórica (kcal)")
    target_protein_g: float = Field(gt=0, description="Meta de proteína (g)")
    target_carbs_g: float = Field(gt=0, description="Meta de carboidratos (g)")
    target_fat_g: float = Field(gt=0, description="Meta de gorduras (g)")
    candidate_foods: Optional[List[Dict[str, Any]]] = Field(default=None, description="Lista inicial de candidatos")
    max_food_weight_g: float = Field(default=350.0, description="Peso máximo por alimento individual (g)")

class SelectedIngredient(BaseModel):
    food_id: str
    name: str
    category: str
    weight_g: float
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float

class OptimizationResult(BaseModel):
    success: bool
    mape_error_percent: float
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    ingredients: List[SelectedIngredient]
    fallback_stage_used: str = "none"  # "none", "vector_expansion", "slack_variables"
    message: str

class MealOptimizerService(MealOptimizerPort):
    def __init__(self, repo: Optional[ChromaNutritionalRepository] = None):
        self.repo = repo

    def solve(self, request: OptimizationRequest) -> OptimizationResult:
        candidates = list(request.candidate_foods) if request.candidate_foods is not None else []

        # Se nenhuma lista de candidatos foi fornecida, carrega universo completo da base seed / repo
        if not candidates:
            candidates = [item.to_metadata() for item in SEED_NUTRITIONAL_DATA]

        # Etapa 1: Resolução por Programação de Metas (Goal Programming L1 Optimization)
        result = self._solve_goal_programming(request, candidates)
        if result.success and result.mape_error_percent < 5.0:
            result.fallback_stage_used = "none"
            return result

        # Fallback Estágio 1: Expansão vetorial caso candidatos fornecidos pelo usuário fossem insuficientes
        if self.repo and request.candidate_foods is not None:
            expanded_candidates = self._expand_candidates_via_vector_search(candidates)
            result_expanded = self._solve_goal_programming(request, expanded_candidates)
            if result_expanded.success and result_expanded.mape_error_percent < 5.0:
                result_expanded.fallback_stage_used = "vector_expansion"
                return result_expanded

        # Fallback Estágio 2: Retorna o resultado da Programação de Metas indicando o uso de folgas
        result.fallback_stage_used = "slack_variables"
        return result

    def _expand_candidates_via_vector_search(self, current_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        existing_ids = {c["food_id"] for c in current_candidates}
        expanded = list(current_candidates)

        categories = ["protein", "carb", "fat", "vegetable"]
        for cat in categories:
            items = self.repo.search_items(query=f"alimento rico em {cat}", category=cat, limit=5)
            for item in items:
                if item["food_id"] not in existing_ids:
                    expanded.append(item)
                    existing_ids.add(item["food_id"])

        return expanded

    def _solve_goal_programming(
        self,
        request: OptimizationRequest,
        candidates: List[Dict[str, Any]]
    ) -> OptimizationResult:
        n_foods = len(candidates)
        if n_foods == 0:
            return OptimizationResult(
                success=False,
                mape_error_percent=100.0,
                total_calories=0, total_protein_g=0, total_carbs_g=0, total_fat_g=0,
                ingredients=[],
                message="Nenhum alimento candidato fornecido."
            )

        cal = np.array([float(c["calories_100g"]) for c in candidates])
        prot = np.array([float(c["protein_100g"]) for c in candidates])
        carb = np.array([float(c["carbs_100g"]) for c in candidates])
        fat = np.array([float(c["fat_100g"]) for c in candidates])

        targets = np.array([
            request.target_calories,
            request.target_protein_g,
            request.target_carbs_g,
            request.target_fat_g
        ])

        # Variáveis: [x_1..x_n, s_cal-, s_cal+, s_prot-, s_prot+, s_carb-, s_carb+, s_fat-, s_fat+]
        # Objetivo: Minimizar soma ponderada das desviações percentuais dos macros + penalidade leve de peso
        c_foods = np.zeros(n_foods)
        c_slacks = np.array([
            100.0 / targets[0], 100.0 / targets[0],
            100.0 / targets[1], 100.0 / targets[1],
            100.0 / targets[2], 100.0 / targets[2],
            100.0 / targets[3], 100.0 / targets[3],
        ])
        c_obj = np.concatenate([c_foods, c_slacks])

        # Restrições de igualdade: macro_i @ x + s_i- - s_i+ = target_i
        A_eq = np.zeros((4, n_foods + 8))
        A_eq[0, :n_foods] = cal
        A_eq[1, :n_foods] = prot
        A_eq[2, :n_foods] = carb
        A_eq[3, :n_foods] = fat

        for i in range(4):
            A_eq[i, n_foods + 2 * i] = 1.0       # s- (defict)
            A_eq[i, n_foods + 2 * i + 1] = -1.0  # s+ (surplus)

        b_eq = targets
        bounds = [(0.0, request.max_food_weight_g / 100.0) for _ in range(n_foods)] + [(0.0, None) for _ in range(8)]

        res = linprog(c_obj, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

        if res.success:
            x = res.x[:n_foods]
            return self._build_result(request, candidates, x, success=True)
        else:
            return OptimizationResult(
                success=False,
                mape_error_percent=100.0,
                total_calories=0, total_protein_g=0, total_carbs_g=0, total_fat_g=0,
                ingredients=[],
                message="Falha no solucionador de metas."
            )

    def _build_result(
        self,
        request: OptimizationRequest,
        candidates: List[Dict[str, Any]],
        x: np.ndarray,
        success: bool
    ) -> OptimizationResult:
        selected: List[SelectedIngredient] = []
        tot_cal = 0.0
        tot_prot = 0.0
        tot_carb = 0.0
        tot_fat = 0.0

        for idx, units in enumerate(x):
            weight_g = round(float(units) * 100.0, 1)
            if weight_g >= 5.0:  # Ignorar porções irrisórias < 5g
                c = candidates[idx]
                item_cal = round(float(c["calories_100g"]) * units, 1)
                item_prot = round(float(c["protein_100g"]) * units, 1)
                item_carb = round(float(c["carbs_100g"]) * units, 1)
                item_fat = round(float(c["fat_100g"]) * units, 1)

                tot_cal += item_cal
                tot_prot += item_prot
                tot_carb += item_carb
                tot_fat += item_fat

                selected.append(
                    SelectedIngredient(
                        food_id=c["food_id"],
                        name=c["name"],
                        category=c["category"],
                        weight_g=weight_g,
                        calories=item_cal,
                        protein_g=item_prot,
                        carbs_g=item_carb,
                        fat_g=item_fat,
                    )
                )

        err_cal = abs(tot_cal - request.target_calories) / request.target_calories
        err_prot = abs(tot_prot - request.target_protein_g) / request.target_protein_g
        err_carb = abs(tot_carb - request.target_carbs_g) / request.target_carbs_g
        err_fat = abs(tot_fat - request.target_fat_g) / request.target_fat_g

        mape = round(float((err_cal + err_prot + err_carb + err_fat) / 4.0 * 100.0), 2)

        return OptimizationResult(
            success=success,
            mape_error_percent=mape,
            total_calories=round(tot_cal, 1),
            total_protein_g=round(tot_prot, 1),
            total_carbs_g=round(tot_carb, 1),
            total_fat_g=round(tot_fat, 1),
            ingredients=selected,
            message=f"Refeição gerada com sucesso. Erro MAPE: {mape}%"
        )
