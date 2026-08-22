from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class GuardrailResult:
    is_safe: bool
    intercepted_term: Optional[str] = None
    latency_ms: float = 0.0

class GuardrailPort(ABC):
    @abstractmethod
    def scan(self, content: str) -> GuardrailResult:
        """
        Invariantes:
        - Execução em tempo linear O(n) com overhead < 5ms.
        - Retornar is_safe=False e o termo violador interceptado ao detectar padrão proibido.
        """
        pass
