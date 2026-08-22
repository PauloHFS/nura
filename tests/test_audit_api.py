import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.api.main import app
from src.adapters.database import engine, create_db_and_tables
from src.domain.models import PatientProfile, MealPlanRecord, AuditLogRecord, NutritionistFeedbackRecord

client = TestClient(app)

from sqlmodel import select

@pytest.fixture(autouse=True)
def setup_test_data():
    create_db_and_tables()
    with Session(engine) as session:
        existing = session.exec(select(PatientProfile).where(PatientProfile.patient_id == "p-aud-1")).first()
        if not existing:
            profile = PatientProfile(
                patient_id="p-aud-1",
                name="Paciente Teste Auditoria",
                weight_kg=85.0,
                target_weight_kg=75.0,
                daily_calories_target=2100.0,
                protein_target_g=160.0,
                carbs_target_g=210.0,
                fat_target_g=60.0,
            )
            session.add(profile)
            session.commit()
        # Seed meal plan record
        plan = MealPlanRecord(
            patient_id="p-aud-1",
            week_number=1,
            plan_json='{"ingredients": [{"name": "Frango", "weight_g": 200}]}',
            mape_error_percent=1.2,
        )
        session.add(plan)
        session.commit()
        session.refresh(plan)

        # Seed audit log
        log = AuditLogRecord(
            patient_id="p-aud-1",
            action="meal_consumed",
            details_json='{"meal": "Frango com arroz", "status": "confirmed"}',
        )
        session.add(log)
        session.commit()

def test_get_audit_plans():
    res = client.get("/api/audit/plans?patient_id=p-aud-1")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["patient_id"] == "p-aud-1"
    assert data[0]["mape_error_percent"] == 1.2

def test_get_audit_logs():
    res = client.get("/api/audit/logs?patient_id=p-aud-1")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["action"] == "meal_consumed"

def test_get_patient_audit_summary():
    res = client.get("/api/audit/patients/p-aud-1")
    assert res.status_code == 200
    data = res.json()
    assert data["patient_id"] == "p-aud-1"
    assert "profile" in data
    assert "plans" in data
    assert "logs" in data
    assert "feedback" in data

def test_post_nutritionist_feedback():
    payload = {
        "patient_id": "p-aud-1",
        "meal_plan_id": 1,
        "nutritionist_name": "Dra. Ana Nutricionista",
        "notes": "Cardápio excelente, boa distribuição de macronutrientes.",
        "status": "approved",
    }
    res = client.post("/api/audit/feedback", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["feedback_id"] is not None

def test_get_audit_dashboard_html():
    res = client.get("/api/audit/dashboard")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "Auditoria Nutricional" in res.text
