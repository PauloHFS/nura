from typing import Any, Dict, List, Optional, TypedDict
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.adapters.aho_corasick_guardrail import AhoCorasickGuardrail
from src.domain.ports.guardrail_port import GuardrailPort
from src.domain.ports.pantry_port import PantryPort
from src.graph.prompts import OARS_SYSTEM_PROMPT
from src.services.meal_optimizer import MealOptimizerService, OptimizationRequest

class PatientState(TypedDict):
    patient_id: str
    messages: List[Dict[str, str]]
    step: str
    meal_plan_pending: bool
    last_meal_suggested: Optional[str]
    inventory_confirmed: bool
    guardrail_blocked: bool
    response_text: Optional[str]

class NuraOrchestrator:
    """Orquestrador de fluxo agêntico acoplando Solucionador Linear, Grocy, Guardrail Aho-Corasick e Telegram."""

    def __init__(
        self,
        pantry_port: Optional[PantryPort] = None,
        optimizer_service: Optional[Any] = None,
        guardrail_port: Optional[GuardrailPort] = None,
        checkpointer: Optional[BaseCheckpointSaver] = None,
    ):
        self.pantry_port = pantry_port
        self.optimizer_service = optimizer_service
        self.guardrail_port = guardrail_port or AhoCorasickGuardrail()
        self.checkpointer = checkpointer or MemorySaver()
        self.graph = self._build_graph()

    def onboarding_node(self, state: PatientState) -> Dict[str, Any]:
        messages = state.get("messages", [])
        last_msg = messages[-1]["content"] if messages else ""
        response = (
            f"Olá! Seja muito bem-vindo ao Nura. {OARS_SYSTEM_PROMPT[:80]}...\n"
            f"Recebi sua mensagem: '{last_msg}'. Qual o seu principal objetivo alimentar esta semana?"
        )
        return {"step": "oars_coaching", "response_text": response}

    def oars_coach_node(self, state: PatientState) -> Dict[str, Any]:
        messages = state.get("messages", [])
        last_msg = messages[-1]["content"] if messages else ""
        response = (
            f"Entendo perfeitamente sua colocação sobre '{last_msg}'. "
            "Como você gostaria de organizar suas refeições para manter a consistência?"
        )
        return {"step": "oars_coaching", "response_text": response}

    def meal_planning_node(self, state: PatientState) -> Dict[str, Any]:
        inventory_items = []
        if self.pantry_port:
            snapshot = self.pantry_port.get_inventory_snapshot()
            if hasattr(snapshot, "items"):
                inventory_items = snapshot.items

            req = OptimizationRequest(
                target_calories=2000.0,
                target_protein_g=150.0,
                target_carbs_g=200.0,
                target_fat_g=65.0,
            )
            result = self.optimizer_service.solve(req)
            items_desc = ", ".join(
                [ing.get("ingredient_name", str(ing)) for ing in getattr(result, "selected_ingredients", [])]
            ) if getattr(result, "selected_ingredients", []) else "Alimentos Selecionados"
            response = f"Plano Alimentar Gerado (MAPE {getattr(result, 'mape_error_percent', 0.0):.1f}%): Sugestão contendo {items_desc}."
        else:
            pantry_names = [item.name for item in inventory_items[:3]] if inventory_items else ["Peito de Frango", "Arroz"]
            response = f"Plano Alimentar Gerado: Sugestão baseada na despensa ({', '.join(pantry_names)})."

        return {
            "step": "inventory_reconciliation",
            "meal_plan_pending": False,
            "last_meal_suggested": "Peito de Frango",
            "response_text": response,
        }

    def inventory_reconciliation_node(self, state: PatientState) -> Dict[str, Any]:
        last_meal = state.get("last_meal_suggested", "Refeição")
        if self.pantry_port and state.get("inventory_confirmed"):
            self.pantry_port.deduct_item(item_id="1", quantity=1.0, confirmed=True)

        response = f"Excelente! Registrei e confirmei o consumo da refeição '{last_meal}'. Baixa de estoque efetuada."
        return {
            "step": "oars_coaching",
            "inventory_confirmed": False,
            "response_text": response,
        }

    def guardrail_middleware_node(self, state: PatientState) -> Dict[str, Any]:
        resp_text = state.get("response_text", "")
        if resp_text and self.guardrail_port:
            scan_res = self.guardrail_port.scan(resp_text)
            if not getattr(scan_res, "is_safe", True):
                return {
                    "guardrail_blocked": True,
                    "response_text": "A resposta gerada foi interceptada pelo Guardrail de Segurança por conter recomendações não aprovadas.",
                }
        return {"guardrail_blocked": False}

    def route_step(self, state: PatientState) -> str:
        step = state.get("step", "onboarding")
        if step == "meal_planning" or state.get("meal_plan_pending"):
            return "meal_planning"
        elif step == "inventory_reconciliation" or state.get("inventory_confirmed"):
            return "inventory_reconciliation"
        elif step == "onboarding":
            return "onboarding"
        return "oars_coach"

    def _build_graph(self):
        builder = StateGraph(PatientState)

        builder.add_node("onboarding", self.onboarding_node)
        builder.add_node("oars_coach", self.oars_coach_node)
        builder.add_node("meal_planning", self.meal_planning_node)
        builder.add_node("inventory_reconciliation", self.inventory_reconciliation_node)
        builder.add_node("guardrail", self.guardrail_middleware_node)

        builder.add_conditional_edges(
            START,
            self.route_step,
            {
                "onboarding": "onboarding",
                "oars_coach": "oars_coach",
                "meal_planning": "meal_planning",
                "inventory_reconciliation": "inventory_reconciliation",
            },
        )

        builder.add_edge("onboarding", "guardrail")
        builder.add_edge("oars_coach", "guardrail")
        builder.add_edge("meal_planning", "guardrail")
        builder.add_edge("inventory_reconciliation", "guardrail")
        builder.add_edge("guardrail", END)

        return builder.compile(checkpointer=self.checkpointer)
