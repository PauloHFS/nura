import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from src.domain.models import PatientProfile, InventoryItemRecord

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_patient_profile_crud(db_session: Session):
    patient = PatientProfile(
        patient_id="patient-zero",
        name="Paciente Zero",
        weight_kg=85.0,
        target_weight_kg=75.0,
        daily_calories_target=2000.0,
        protein_target_g=160.0,
        carbs_target_g=180.0,
        fat_target_g=60.0,
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)

    assert patient.id is not None

    statement = select(PatientProfile).where(PatientProfile.patient_id == "patient-zero")
    result = db_session.exec(statement).first()
    assert result is not None
    assert result.name == "Paciente Zero"
    assert result.weight_kg == 85.0

def test_inventory_item_crud(db_session: Session):
    item = InventoryItemRecord(
        item_id="egg-001",
        name="Ovos Caipiras",
        category="protein",
        quantity=12.0,
        unit="units",
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    assert item.id is not None
    assert item.item_id == "egg-001"
