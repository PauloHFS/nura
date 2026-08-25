import pytest
from unittest.mock import MagicMock
from src.adapters.grocy_adapter import GrocyAdapter, GrocyHttpClient

def test_grocy_http_client_url_formatting():
    client1 = GrocyHttpClient(base_url="https://grocy.example.com/api", api_key="testkey")
    assert client1._url("stock") == "https://grocy.example.com/api/stock"
    assert client1._url("objects/products") == "https://grocy.example.com/api/objects/products"

    client2 = GrocyHttpClient(base_url="https://grocy.example.com", api_key="testkey")
    assert client2._url("stock") == "https://grocy.example.com/api/stock"
    assert client2._url("objects/products") == "https://grocy.example.com/api/objects/products"

def test_grocy_adapter_get_candidate_foods():
    mock_http_client = MagicMock()
    mock_http_client.get_stock.return_value = [
        {"product_id": "1", "name": "Peito de Frango", "amount": 2.5},
        {"product_id": "2", "name": "Arroz Integral", "amount": 0.0},  # Amount 0 should be filtered out
        {"product_id": "3", "name": "Ovos", "amount": 12.0},
    ]
    mock_http_client.get_products.return_value = [
        {
            "id": "1",
            "name": "Peito de Frango",
            "calories": 165.0,
            "protein": 31.0,
            "carbohydrates": 0.0,
            "fat": 3.6,
            "category": "protein",
        },
        {
            "id": "3",
            "name": "Ovos",
            "calories_100g": 155.0,
            "protein_100g": 13.0,
            "carbs_100g": 1.1,
            "fat_100g": 11.0,
            "userfields": {"category": "dairy"},
        },
    ]

    adapter = GrocyAdapter(base_url="http://grocy.test", api_key="key", http_client=mock_http_client)
    candidates = adapter.get_candidate_foods()

    # Arroz (amount=0) must be excluded
    assert len(candidates) == 2
    c1 = next(c for c in candidates if c["food_id"] == "grocy-1")
    assert c1["name"] == "Peito de Frango"
    assert c1["calories_100g"] == 165.0
    assert c1["protein_100g"] == 31.0
    assert c1["carbs_100g"] == 0.0
    assert c1["fat_100g"] == 3.6
    assert c1["amount"] == 2.5

    c3 = next(c for c in candidates if c["food_id"] == "grocy-3")
    assert c3["name"] == "Ovos"
    assert c3["calories_100g"] == 155.0
    assert c3["protein_100g"] == 13.0
    assert c3["amount"] == 12.0
