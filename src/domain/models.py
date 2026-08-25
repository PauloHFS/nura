import json
from datetime import datetime
from typing import Optional
from pydantic import computed_field
from sqlmodel import Field, SQLModel

class PatientProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: str = Field(index=True, unique=True)
    name: str
    weight_kg: float
    target_weight_kg: float
    daily_calories_target: float
    protein_target_g: float
    carbs_target_g: float
    fat_target_g: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MealPlanRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: str = Field(index=True)
    week_number: int = Field(default=1)
    plan_json: str
    mape_error_percent: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NutritionPlanRecord(SQLModel, table=True):
    """Represents a nutrition plan record. Target columns are persisted at row level to enable efficient SQL filtering and target analytics without parsing JSON blobs."""
    __tablename__ = "nutrition_plans"
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: str = Field(default="default_patient", index=True)
    target_calories: float = Field(default=0.0)
    target_protein_g: float = Field(default=0.0)
    target_carbs_g: float = Field(default=0.0)
    target_fat_g: float = Field(default=0.0)
    mape_error: float = Field(default=0.0)
    ingredients_json: str = Field(default="[]")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def mape_error_percent(self) -> float:
        return self.mape_error

    @computed_field
    @property
    def plan_json(self) -> str:
        return self.ingredients_json

class InventoryItemRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: str = Field(index=True, unique=True)
    name: str
    category: str
    quantity: float
    unit: str
    expiration_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AuditLogRecord(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: Optional[str] = Field(default=None, index=True)
    user_id: Optional[str] = Field(default=None, index=True)
    patient_id: Optional[str] = Field(default=None, index=True)
    action: str
    payload_json: str = Field(default="{}")
    details_json: Optional[str] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @property
    def payload(self) -> dict:
        try:
            return json.loads(self.payload_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    @payload.setter
    def payload(self, value: dict) -> None:
        self.payload_json = json.dumps(value)

    @property
    def details(self) -> Optional[dict]:
        if self.details_json is None:
            return None
        try:
            return json.loads(self.details_json)
        except (json.JSONDecodeError, TypeError):
            return None

    @details.setter
    def details(self, value: Optional[dict]) -> None:
        self.details_json = json.dumps(value) if value is not None else None
class NutritionistFeedbackRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: str = Field(index=True)
    meal_plan_id: Optional[int] = Field(default=None)
    nutritionist_name: str
    notes: str
    status: str = Field(default="reviewed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
