from typing import Any, Dict, List, Optional, TypedDict
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.graph.prompts import OARS_SYSTEM_PROMPT

class PatientState(TypedDict):
    patient_id: str
    messages: List[Dict[str, str]]
    step: str
    meal_plan_pending: bool
    last_meal_suggested: Optional[str]
    inventory_confirmed: bool
    guardrail_blocked: bool
    response_text: Optional[str]

def onboarding_node(state: PatientState) -> Dict[str, Any]:
    messages = state.get("messages", [])
    last_msg = messages[-1]["content"] if messages else ""
    
    response = (
        f"Olá! Seja muito bem-vindo ao Nura. {OARS_SYSTEM_PROMPT[:100]}...\n"
        f"Recebi sua mensagem: '{last_msg}'. O que te motiva a alcançar seu objetivo nutricional hoje?"
    )
    return {
        "step": "oars_coaching",
        "response_text": response,
    }

def oars_coach_node(state: PatientState) -> Dict[str, Any]:
    messages = state.get("messages", [])
    last_msg = messages[-1]["content"] if messages else ""
    
    response = (
        f"Compreendo perfeitamente. Em relação ao seu relato ('{last_msg}'), "
        "como você se sente sobre manter suas metas nutricionais esta semana?"
    )
    return {
        "step": "oars_coaching",
        "response_text": response,
    }

def route_step(state: PatientState) -> str:
    step = state.get("step", "onboarding")
    if step == "onboarding":
        return "onboarding"
    return "oars_coach"

class NuraOrchestrator:
    """Orquestrador de fluxo agêntico baseado no LangGraph StateGraph com suporte a checkpoints."""

    def __init__(self, checkpointer: Optional[BaseCheckpointSaver] = None):
        self.checkpointer = checkpointer or MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(PatientState)
        
        builder.add_node("onboarding", onboarding_node)
        builder.add_node("oars_coach", oars_coach_node)

        builder.add_conditional_edges(
            START,
            route_step,
            {
                "onboarding": "onboarding",
                "oars_coach": "oars_coach",
            }
        )

        builder.add_edge("onboarding", END)
        builder.add_edge("oars_coach", END)

        return builder.compile(checkpointer=self.checkpointer)
