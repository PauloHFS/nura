from abc import ABC, abstractmethod
from typing import Any

class PantryPort(ABC):
    @abstractmethod
    def get_inventory_snapshot(self) -> Any:
        """Retorna a foto da despensa com priorização por vencimento e eletrodomésticos."""
        pass

    @abstractmethod
    def deduct_item(self, item_id: str, quantity: float) -> Any:
        """Executa a mutação de baixa no estoque após confirmação conversacional."""
        pass
