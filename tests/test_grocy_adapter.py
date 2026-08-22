import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from src.domain.ports.pantry_port import GrocyItem, GrocyAppliance, PantrySnapshot
from src.adapters.grocy_adapter import GrocyAdapter

def test_pantry_snapshot_expiration_sorting():
    today = datetime.now()
    item_expiring_soon = GrocyItem(
        id="1", name="Leite", amount=1.0, unit="L",
        best_before_date=(today + timedelta(days=1)).strftime("%Y-%m-%d")
    )
    item_expiring_later = GrocyItem(
        id="2", name="Arroz", amount=5.0, unit="kg",
        best_before_date=(today + timedelta(days=30)).strftime("%Y-%m-%d")
    )
    item_no_date = GrocyItem(
        id="3", name="Sal", amount=1.0, unit="kg",
        best_before_date=None
    )

    snapshot = PantrySnapshot(
        items=[item_expiring_later, item_no_date, item_expiring_soon],
        appliances=[GrocyAppliance(id="a1", name="Air Fryer", in_service=True)]
    )

    prioritized = snapshot.get_prioritized_items()
    assert prioritized[0].id == "1"  # Leite expires first
    assert prioritized[1].id == "2"  # Arroz expires later
    assert prioritized[2].id == "3"  # Sal has no expiration date

def test_grocy_adapter_get_inventory_snapshot_mocked_http():
    mock_http_client = MagicMock()
    mock_http_client.get_stock.return_value = [
        {"product_id": "10", "name": "Ovos", "amount": 12, "qu_unit": "un", "best_before_date": "2026-08-25"},
        {"product_id": "11", "name": "Peito de Frango", "amount": 1.5, "qu_unit": "kg", "best_before_date": "2026-08-23"},
    ]
    mock_http_client.get_appliances.return_value = [
        {"id": "eq1", "name": "Forno Elétrico", "in_service": True}
    ]

    adapter = GrocyAdapter(base_url="http://grocy.local", api_key="secret", http_client=mock_http_client)
    snapshot = adapter.get_inventory_snapshot()

    assert len(snapshot.items) == 2
    assert snapshot.items[0].name == "Peito de Frango"  # Expiring soonest
    assert len(snapshot.appliances) == 1
    assert snapshot.appliances[0].name == "Forno Elétrico"

def test_grocy_adapter_deduct_item_requires_conversational_confirmation():
    mock_http_client = MagicMock()
    adapter = GrocyAdapter(base_url="http://grocy.local", api_key="secret", http_client=mock_http_client)

    # Without confirmation, deduction must fail/refuse (ADR-0007)
    with pytest.raises(ValueError, match="Conversational confirmation required"):
        adapter.deduct_item(item_id="10", quantity=2.0, confirmed=False)

    assert mock_http_client.consume_product.call_count == 0

    # With confirmation, deduction calls API
    mock_http_client.consume_product.return_value = {"success": True}
    result = adapter.deduct_item(item_id="10", quantity=2.0, confirmed=True)
    assert result is True
    mock_http_client.consume_product.assert_called_once_with("10", 2.0)
