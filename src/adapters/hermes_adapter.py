from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.domain.ports.coach_channel_port import (
    ChannelMessageRequest,
    ChannelMessageResponse,
    CoachChannelPort,
)
from src.graph.orchestrator import NuraOrchestrator

class HermesRequestPayload(BaseModel):
    session_id: str = Field(description="Identificador único da sessão no Hermes Agent")
    user_id: str = Field(description="Identificador único do Paciente-Fundador")
    text: str = Field(description="Conteúdo da mensagem enviada pelo usuário")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados adicionais da sessão")

class HermesResponsePayload(BaseModel):
    session_id: str
    response_text: str
    step: str
    guardrail_blocked: bool
    suggested_actions: List[str]

class HermesOutboundSubscriptionPayload(BaseModel):
    session_id: str
    callback_url: str

class HermesAdapter(CoachChannelPort):
    """Adaptador de Integração Hexagonal para o Hermes Agent."""

    def __init__(self, orchestrator: Optional[NuraOrchestrator] = None):
        self.orchestrator = orchestrator or NuraOrchestrator()
        self.outbound_webhooks: Dict[str, str] = {}

    def process_message(self, request: ChannelMessageRequest) -> ChannelMessageResponse:
        config = {"configurable": {"thread_id": request.session_id}}
        user_text = request.text
        lower_text = user_text.lower()

        state = {
            "patient_id": request.user_id,
            "messages": [{"role": "user", "content": user_text}],
            "step": "onboarding",
            "meal_plan_pending": "cardápio" in lower_text or "gerar" in lower_text or "dieta" in lower_text,
            "last_meal_suggested": None,
            "inventory_confirmed": "sim" in lower_text or "consumi" in lower_text or "confirmo" in lower_text,
            "guardrail_blocked": False,
            "response_text": None,
        }

        final_state = self.orchestrator.graph.invoke(state, config=config)
        step = final_state.get("step", "oars_coaching")
        guardrail_blocked = final_state.get("guardrail_blocked", False)
        resp_text = final_state.get("response_text", "Mensagem processada pelo Nura.")

        suggested_actions = []
        if step == "onboarding":
            suggested_actions = ["iniciar_acompanhamento", "informar_metas"]
        elif step == "oars_coaching":
            suggested_actions = ["gerar_cardapio_semanal", "relatar_refeicao"]
        elif step == "meal_planning":
            suggested_actions = ["confirmar_cardapio", "solicitar_substituicao"]
        elif step == "inventory_reconciliation":
            suggested_actions = ["confirmar_consumo", "atualizar_estoque_grocy"]

        return ChannelMessageResponse(
            session_id=request.session_id,
            response_text=resp_text,
            step=step,
            guardrail_blocked=guardrail_blocked,
            suggested_actions=suggested_actions,
        )

    def register_outbound_webhook(self, session_id: str, callback_url: str) -> bool:
        self.outbound_webhooks[session_id] = callback_url
        return True
