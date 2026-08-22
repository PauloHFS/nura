from abc import ABC, abstractmethod
from typing import Any

class MealOptimizerPort(ABC):
    @abstractmethod
    def solve(self, request: Any) -> Any:
        """
        Invariantes:
        - Garantir erro calórico/macro < 5% em caso de convergência estrita.
        - Aplicar fallback de expansão vetorial se os ingredientes candidatos forem insuficientes.
        - Retornar variáveis de folga com penalidades se a restrição estrita for matematicamente inviável.
        """
        pass
