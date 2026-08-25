import logging
import requests
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional
from src.domain.ports.pantry_port import (
    GrocyAppliance,
    GrocyItem,
    PantryPort,
    PantrySnapshot,
)

logger = logging.getLogger(__name__)

def _get_val(item: dict, product_info: dict, userfields: dict, *keys: str, default: float = 0.0) -> float:
    for k in keys:
        for source in (product_info, userfields, item):
            if source and source.get(k) is not None:
                try:
                    return float(source[k])
                except (ValueError, TypeError):
                    pass
    return default
class GrocyHttpClient:
    """Cliente HTTP padrão para a API REST do Grocy."""
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.headers = {
            "GROCY-API-KEY": api_key or "",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _url(self, endpoint: str) -> str:
        endpoint = endpoint.lstrip("/")
        base = self.base_url.rstrip("/")
        parsed_path = urlparse(base).path.rstrip("/")
        if parsed_path.endswith("/api") or parsed_path == "/api":
            return f"{base}/{endpoint}"
        return f"{base}/api/{endpoint}"
    def get_stock(self) -> List[dict]:
        res = requests.get(self._url("stock"), headers=self.headers, timeout=10)
        res.raise_for_status()
        return res.json()

    def get_products(self) -> List[dict]:
        res = requests.get(self._url("objects/products"), headers=self.headers, timeout=10)
        res.raise_for_status()
        return res.json()

    def get_appliances(self) -> List[dict]:
        res = requests.get(self._url("objects/equipment"), headers=self.headers, timeout=10)
        res.raise_for_status()
        return res.json()

    def consume_product(self, product_id: str, amount: float) -> dict:
        url = self._url(f"stock/products/{product_id}/consume")
        payload = {"amount": amount, "transaction_type": "consume"}
        res = requests.post(url, json=payload, headers=self.headers, timeout=10)
        res.raise_for_status()
        return res.json()

class GrocyAdapter(PantryPort):
    """Adaptador de integração Hexagonal para a API REST do Grocy."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        http_client: Optional[Any] = None,
    ):
        from src.config import GROCY_API_URL, GROCY_API_KEY
        self.base_url = base_url or GROCY_API_URL
        self.api_key = api_key or GROCY_API_KEY
        self.http_client = http_client or GrocyHttpClient(self.base_url, self.api_key)

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
        snapshot.items = snapshot.get_prioritized_items()
        return snapshot

    def get_candidate_foods(self) -> List[dict]:
        """
        Busca estoque em GET /stock e produtos em GET /objects/products.
        Filtra apenas itens onde amount > 0 e mapeia para a estrutura de candidate_foods do SciPy solver.
        """
        try:
            raw_stock = self.http_client.get_stock()
        except Exception as e:
            logger.error("Grocy get_stock failed: %s", e, exc_info=True)
            raise

        try:
            raw_products = self.http_client.get_products()
        except Exception as e:
            logger.error("Grocy get_products failed: %s", e, exc_info=True)
            raise

        products_map = {}
        for p in raw_products:
            p_id = str(p.get("id") or p.get("product_id") or "")
            if p_id:
                products_map[p_id] = p

        candidates_map: Dict[str, dict] = {}
        for item in raw_stock:
            amount = float(item.get("amount", 0.0))
            if amount <= 0:
                continue

            product_id = str(item.get("product_id") or "")
            if not product_id:
                continue

            if product_id in candidates_map:
                candidates_map[product_id]["amount"] += amount
                continue

            product_info = products_map.get(product_id, {})
            userfields = product_info.get("userfields", {}) or {}

            name = product_info.get("name") or item.get("name") or item.get("product_name") or f"Produto {product_id}"
            calories_100g = _get_val(item, product_info, userfields, "calories_100g", "calories", "calorias", "energy_kcal", "energy")
            protein_100g = _get_val(item, product_info, userfields, "protein_100g", "protein", "proteina", "protein_g")
            carbs_100g = _get_val(item, product_info, userfields, "carbs_100g", "carbohydrates", "carbs", "carboidratos", "carbs_g")
            fat_100g = _get_val(item, product_info, userfields, "fat_100g", "fat", "gordura", "fat_g")
            category = product_info.get("category") or userfields.get("category") or "grocy"

            candidates_map[product_id] = {
                "food_id": f"grocy-{product_id}",
                "name": str(name),
                "category": str(category),
                "calories_100g": calories_100g,
                "protein_100g": protein_100g,
                "carbs_100g": carbs_100g,
                "fat_100g": fat_100g,
                "amount": amount,
            }

        return list(candidates_map.values())
    def deduct_item(self, item_id: str, quantity: float, confirmed: bool = False) -> bool:
        if not confirmed:
            raise ValueError("Conversational confirmation required before inventory deduction.")

        res = self.http_client.consume_product(item_id, quantity)
        return bool(res and res.get("success", True))
