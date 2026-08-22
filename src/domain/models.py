from datetime import datetime
from typing import Optional
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
    week_number: int
    plan_json: str
    mape_error_percent: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

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
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: str = Field(index=True)
    action: str
    details_json: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
