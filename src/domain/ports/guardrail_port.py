from abc import ABC, abstractmethod
from typing import Any

class GuardrailPort(ABC):
    @abstractmethod
    def scan(self, content: str) -> Any:
        """
        Invariantes:
        - Execução em tempo linear O(n) com overhead < 5ms.
        - Retornar is_safe=False e o termo violador interceptado ao detectar padrão proibido.
        """
        pass
