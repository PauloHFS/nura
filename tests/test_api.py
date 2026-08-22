from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "nura-api"
    assert data["architecture"] == "hexagonal"
def test_optimize_meal_endpoint():
    payload = {
        "target_calories": 600.0,
        "target_protein_g": 45.0,
        "target_carbs_g": 65.0,
        "target_fat_g": 20.0
    }
    response = client.post("/api/meal/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["mape_error_percent"] < 5.0
    assert len(data["ingredients"]) > 0
