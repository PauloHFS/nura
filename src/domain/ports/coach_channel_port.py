from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class ChannelMessageRequest:
    session_id: str
    user_id: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChannelMessageResponse:
    session_id: str
    response_text: str
    step: str = "oars_coaching"
    guardrail_blocked: bool = False
    suggested_actions: List[str] = field(default_factory=list)

class CoachChannelPort(ABC):
    @abstractmethod
    def process_message(self, request: ChannelMessageRequest) -> ChannelMessageResponse:
        """Processa a mensagem recebida de um canal (Hermes/Telegram) através do orquestrador do Nura."""
        pass

    @abstractmethod
    def register_outbound_webhook(self, session_id: str, callback_url: str) -> bool:
        """Registra URL de retorno para mensagens proativas de check-in."""
        pass
