from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class GrocyItem:
    id: str
    name: str
    amount: float
    unit: str = "un"
    best_before_date: Optional[str] = None

@dataclass
class GrocyAppliance:
    id: str
    name: str
    in_service: bool = True

@dataclass
class PantrySnapshot:
    items: List[GrocyItem] = field(default_factory=list)
    appliances: List[GrocyAppliance] = field(default_factory=list)

    def get_prioritized_items(self) -> List[GrocyItem]:
        """Retorna os itens ordenados por data de vencimento (os que vencem primeiro entram no topo)."""
        def sort_key(item: GrocyItem):
            if not item.best_before_date:
                return "9999-12-31"
            return item.best_before_date

        return sorted(self.items, key=sort_key)

class PantryPort(ABC):
    @abstractmethod
    def get_inventory_snapshot(self) -> PantrySnapshot:
        """Retorna a foto da despensa com priorização por vencimento e eletrodomésticos."""
        pass

    @abstractmethod
    def deduct_item(self, item_id: str, quantity: float, confirmed: bool = False) -> bool:
        """Executa a mutação de baixa no estoque após confirmação conversacional."""
        pass
