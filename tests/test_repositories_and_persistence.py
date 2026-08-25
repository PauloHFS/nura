import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from src.api.main import app, get_grocy_adapter
from src.adapters.database import engine, create_db_and_tables
from src.domain.models import NutritionPlanRecord, AuditLogRecord
from src.adapters.repositories import NutritionPlanRepository, AuditLogRepository

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    create_db_and_tables()

def test_repositories_save_and_list():
    with Session(engine) as session:
        plan_repo = NutritionPlanRepository(session)
        audit_repo = AuditLogRepository(session)

        plan = plan_repo.save_plan(
            patient_id="p-test-repo-1",
            target_calories=500.0,
            target_protein_g=40.0,
            target_carbs_g=50.0,
            target_fat_g=15.0,
            mape_error=2.1,
            ingredients=[{"name": "Frango", "weight_g": 150}],
        )
        assert plan.id is not None
        assert plan.patient_id == "p-test-repo-1"

        plans = plan_repo.list_plans(patient_id="p-test-repo-1")
        assert len(plans) >= 1
        assert plans[0].mape_error == 2.1

        log = audit_repo.log_action(
            action="test_action",
            session_id="sess-123",
            user_id="p-test-repo-1",
            patient_id="p-test-repo-1",
            payload={"info": "ok"},
        )
        assert log.id is not None

        logs = audit_repo.list_logs(patient_id="p-test-repo-1")
        assert len(logs) >= 1
        assert logs[0].action == "test_action"

def test_optimize_meal_saves_to_database_and_fetches_audit():
    payload = {
        "patient_id": "p-opt-db-1",
        "target_calories": 600.0,
        "target_protein_g": 45.0,
        "target_carbs_g": 65.0,
        "target_fat_g": 20.0,
    }
    response = client.post("/api/meal/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify audit plans endpoint
    res_plans = client.get("/api/audit/plans?patient_id=p-opt-db-1")
    assert res_plans.status_code == 200
    plans = res_plans.json()
    assert len(plans) >= 1
    assert plans[0]["patient_id"] == "p-opt-db-1"

    # Verify audit logs endpoint
    res_logs = client.get("/api/audit/logs?patient_id=p-opt-db-1")
    assert res_logs.status_code == 200
    logs = res_logs.json()
    assert len(logs) >= 1
    assert logs[0]["action"] == "meal_optimized"

def test_optimize_meal_auto_fetches_from_grocy_when_candidate_foods_empty():
    mock_grocy_adapter = MagicMock()
    mock_grocy_adapter.get_candidate_foods.return_value = [
        {"food_id": "grocy-101", "name": "Peito de Frango", "category": "protein", "calories_100g": 165.0, "protein_100g": 31.0, "carbs_100g": 0.0, "fat_100g": 3.6},
        {"food_id": "grocy-102", "name": "Arroz Cozido", "category": "carb", "calories_100g": 130.0, "protein_100g": 2.7, "carbs_100g": 28.0, "fat_100g": 0.3},
        {"food_id": "grocy-103", "name": "Azeite de Oliva", "category": "fat", "calories_100g": 884.0, "protein_100g": 0.0, "carbs_100g": 0.0, "fat_100g": 100.0},
    ]

    app.dependency_overrides[get_grocy_adapter] = lambda: mock_grocy_adapter

    try:
        payload = {
            "patient_id": "p-grocy-auto-1",
            "target_calories": 500.0,
            "target_protein_g": 40.0,
            "target_carbs_g": 50.0,
            "target_fat_g": 15.0,
            "candidate_foods": None,  # Candidate foods empty
        }
        res = client.post("/api/meal/optimize", json=payload)
        assert res.status_code == 200
        assert mock_grocy_adapter.get_candidate_foods.call_count >= 1
        data = res.json()
        assert data["success"] is True
    finally:
        app.dependency_overrides.clear()
