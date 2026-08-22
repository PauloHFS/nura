import requests
from typing import Any, List, Optional
from src.domain.ports.pantry_port import (
    GrocyAppliance,
    GrocyItem,
    PantryPort,
    PantrySnapshot,
)

class GrocyHttpClient:
    """Cliente HTTP padrão para a API REST do Grocy."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "GROCY-API-KEY": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def get_stock(self) -> List[dict]:
        res = requests.get(f"{self.base_url}/api/stock", headers=self.headers, timeout=10)
        res.raise_for_status()
        return res.json()

    def get_appliances(self) -> List[dict]:
        res = requests.get(f"{self.base_url}/api/objects/equipment", headers=self.headers, timeout=10)
        res.raise_for_status()
        return res.json()

    def consume_product(self, product_id: str, amount: float) -> dict:
        url = f"{self.base_url}/api/stock/products/{product_id}/consume"
        payload = {"amount": amount, "transaction_type": "consume"}
        res = requests.post(url, json=payload, headers=self.headers, timeout=10)
        res.raise_for_status()
        return res.json()

class GrocyAdapter(PantryPort):
    """Adaptador de integração Hexagonal para a API REST do Grocy."""

    def __init__(self, base_url: str, api_key: str, http_client: Optional[Any] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.http_client = http_client or GrocyHttpClient(base_url, api_key)

    def get_inventory_snapshot(self) -> PantrySnapshot:
        raw_stock = self.http_client.get_stock()
        raw_appliances = self.http_client.get_appliances()

        items = []
        for stock_entry in raw_stock:
            item = GrocyItem(
                id=str(stock_entry.get("product_id", stock_entry.get("id", ""))),
                name=stock_entry.get("name", stock_entry.get("product_name", "Desconhecido")),
                amount=float(stock_entry.get("amount", 0.0)),
                unit=stock_entry.get("qu_unit", stock_entry.get("unit", "un")),
                best_before_date=stock_entry.get("best_before_date"),
            )
            items.append(item)

        appliances = []
        for eq in raw_appliances:
            appliance = GrocyAppliance(
                id=str(eq.get("id", "")),
                name=eq.get("name", "Equipamento"),
                in_service=bool(eq.get("in_service", True)),
            )
            appliances.append(appliance)

        snapshot = PantrySnapshot(items=items, appliances=appliances)
        # Ordena itens por data de vencimento
        snapshot.items = snapshot.get_prioritized_items()
        return snapshot

    def deduct_item(self, item_id: str, quantity: float, confirmed: bool = False) -> bool:
        if not confirmed:
            raise ValueError("Conversational confirmation required before inventory deduction.")

        res = self.http_client.consume_product(item_id, quantity)
        return bool(res and res.get("success", True))
