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

        if not candidates:
            if self.repo:
                candidates = self.repo.search_items(query="alimento", limit=20)
            if not candidates:
                candidates = [item.to_metadata() for item in SEED_NUTRITIONAL_DATA]

        # Etapa 0: Solucionador estrito sem variáveis de folga
        res_strict = self._solve_lp(request, candidates, allow_slacks=False)
        if res_strict.success and res_strict.mape_error_percent < 5.0:
            res_strict.fallback_stage_used = "none"
            return res_strict

        # Fallback Estágio 1: Expansão vetorial por categorias no Chroma DB (Sem variáveis de folga)
        active_candidates = candidates
        if self.repo:
            active_candidates = self._expand_candidates_via_vector_search(candidates)
            res_expanded = self._solve_lp(request, active_candidates, allow_slacks=False)
            if res_expanded.success and res_expanded.mape_error_percent < 5.0:
                res_expanded.fallback_stage_used = "vector_expansion"
                return res_expanded

        # Fallback Estágio 2: Ativação dinâmica de variáveis de folga com penalidades suaves mantendo candidatos expandidos
        res_slack = self._solve_lp(request, active_candidates, allow_slacks=True)
        res_slack.fallback_stage_used = "slack_variables"
        return res_slack

    def _expand_candidates_via_vector_search(self, current_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        existing_ids = {c["food_id"] for c in current_candidates}
        expanded = list(current_candidates)

        category_queries = [
            ("protein", "proteina frango carne ovo"),
            ("carb", "carboidrato arroz batata aveia"),
            ("fat", "gordura azeite abacate castanha"),
            ("vegetable", "vegetal brócolis espinafre alface")
        ]
        for cat, query_text in category_queries:
            items = self.repo.search_items(query=query_text, category=cat, limit=5)
            for item in items:
                if item["food_id"] not in existing_ids:
                    expanded.append(item)
                    existing_ids.add(item["food_id"])

        return expanded

    def _solve_lp(
        self,
        request: OptimizationRequest,
        candidates: List[Dict[str, Any]],
        allow_slacks: bool = False
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

        b_targets = np.array([
            request.target_calories,
            request.target_protein_g,
            request.target_carbs_g,
            request.target_fat_g
        ])

        if not allow_slacks:
            # Estrito: 0.95 * b <= A @ x <= 1.05 * b (Sem variáveis de folga)
            c_obj = np.full(n_foods, 1.0)
            A_mat = np.vstack([cal, prot, carb, fat])

            A_ub = np.vstack([A_mat, -A_mat])
            b_ub = np.concatenate([b_targets * 1.05, -b_targets * 0.95])
            bounds = [(0.0, request.max_food_weight_g / 100.0) for _ in range(n_foods)]

            res = linprog(c_obj, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
            if res.success:
                return self._build_result(request, candidates, res.x, success=True)
            else:
                return OptimizationResult(
                    success=False,
                    mape_error_percent=100.0,
                    total_calories=0, total_protein_g=0, total_carbs_g=0, total_fat_g=0,
                    ingredients=[],
                    message="Sem convergência no solucionador estrito."
                )
        else:
            # Com variáveis de folga injetadas dinamicamente
            c_foods = np.full(n_foods, 0.0001)
            c_slacks = np.array([
                1000.0 / b_targets[0], 1000.0 / b_targets[0],
                1000.0 / b_targets[1], 1000.0 / b_targets[1],
                1000.0 / b_targets[2], 1000.0 / b_targets[2],
                1000.0 / b_targets[3], 1000.0 / b_targets[3],
            ])
            c_obj = np.concatenate([c_foods, c_slacks])

            A_eq = np.zeros((4, n_foods + 8))
            A_eq[0, :n_foods] = cal
            A_eq[1, :n_foods] = prot
            A_eq[2, :n_foods] = carb
            A_eq[3, :n_foods] = fat

            for i in range(4):
                A_eq[i, n_foods + 2 * i] = 1.0       # s-
                A_eq[i, n_foods + 2 * i + 1] = -1.0  # s+

            bounds = [(0.0, request.max_food_weight_g / 100.0) for _ in range(n_foods)] + [(0.0, None) for _ in range(8)]

            res = linprog(c_obj, A_eq=A_eq, b_eq=b_targets, bounds=bounds, method='highs')
            if res.success:
                x = res.x[:n_foods]
                return self._build_result(request, candidates, x, success=True)
            else:
                return OptimizationResult(
                    success=False,
                    mape_error_percent=100.0,
                    total_calories=0, total_protein_g=0, total_carbs_g=0, total_fat_g=0,
                    ingredients=[],
                    message="Falha total no solucionador com folgas."
                )

    def _build_result(
        self,
        request: OptimizationRequest,
        candidates: List[Dict[str, Any]],
        x: np.ndarray,
        success: bool
    ) -> OptimizationResult:
        selected: List[SelectedIngredient] = []
        raw_cal = 0.0
        raw_prot = 0.0
        raw_carb = 0.0
        raw_fat = 0.0

        for idx, units in enumerate(x):
            if units > 1e-5:  # Preservar acurácia sem truncar
                units_val = float(units)
                weight_g = units_val * 100.0
                c = candidates[idx]
                item_cal = float(c["calories_100g"]) * units_val
                item_prot = float(c["protein_100g"]) * units_val
                item_carb = float(c["carbs_100g"]) * units_val
                item_fat = float(c["fat_100g"]) * units_val

                raw_cal += item_cal
                raw_prot += item_prot
                raw_carb += item_carb
                raw_fat += item_fat

                selected.append(
                    SelectedIngredient(
                        food_id=c["food_id"],
                        name=c["name"],
                        category=c["category"],
                        weight_g=round(weight_g, 1),
                        calories=round(item_cal, 1),
                        protein_g=round(item_prot, 1),
                        carbs_g=round(item_carb, 1),
                        fat_g=round(item_fat, 1),
                    )
                )

        err_cal = abs(raw_cal - request.target_calories) / request.target_calories
        err_prot = abs(raw_prot - request.target_protein_g) / request.target_protein_g
        err_carb = abs(raw_carb - request.target_carbs_g) / request.target_carbs_g
        err_fat = abs(raw_fat - request.target_fat_g) / request.target_fat_g

        mape = round(float((err_cal + err_prot + err_carb + err_fat) / 4.0 * 100.0), 2)

        return OptimizationResult(
            success=success,
            mape_error_percent=mape,
            total_calories=round(raw_cal, 1),
            total_protein_g=round(raw_prot, 1),
            total_carbs_g=round(raw_carb, 1),
            total_fat_g=round(raw_fat, 1),
            ingredients=selected,
            message=f"Refeição gerada com sucesso. Erro MAPE: {mape}%"
        )
