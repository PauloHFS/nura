import json
from typing import List, Optional, Any, Dict
from sqlmodel import Session, select
from src.domain.models import NutritionPlanRecord, AuditLogRecord

class NutritionPlanRepository:
    """Repositório para persistência de planos nutricionais."""

    def __init__(self, session: Session):
        self.session = session

    def save_plan(
        self,
        patient_id: str,
        target_calories: float,
        target_protein_g: float,
        target_carbs_g: float,
        target_fat_g: float,
        mape_error: float,
        ingredients: List[Any],
        commit: bool = True,
    ) -> NutritionPlanRecord:
        ingredients_data = []
        for item in ingredients:
            if hasattr(item, "model_dump"):
                ingredients_data.append(item.model_dump())
            elif hasattr(item, "dict"):
                ingredients_data.append(item.dict())
            elif isinstance(item, dict):
                ingredients_data.append(item)
            else:
                ingredients_data.append(dict(item) if hasattr(item, "keys") else {"value": str(item)})

        record = NutritionPlanRecord(
            patient_id=patient_id or "default_patient",
            target_calories=target_calories,
            target_protein_g=target_protein_g,
            target_carbs_g=target_carbs_g,
            target_fat_g=target_fat_g,
            mape_error=mape_error,
            ingredients_json=json.dumps(ingredients_data, default=str),
        )
        self.session.add(record)
        if commit:
            self.session.commit()
            self.session.refresh(record)
        return record

    def list_plans(self, patient_id: Optional[str] = None) -> List[NutritionPlanRecord]:
        query = select(NutritionPlanRecord)
        if patient_id:
            query = query.where(NutritionPlanRecord.patient_id == patient_id)
        return self.session.exec(query).all()

class AuditLogRepository:
    """Repositório para persistência de logs de auditoria."""

    def __init__(self, session: Session):
        self.session = session

    def log_action(
        self,
        action: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        commit: bool = True,
    ) -> AuditLogRecord:
        payload_str = json.dumps(payload or {}, default=str)
        record = AuditLogRecord(
            session_id=session_id,
            user_id=user_id or patient_id or "system",
            patient_id=patient_id or user_id or "default_patient",
            action=action,
            payload_json=payload_str,
        )
        self.session.add(record)
        if commit:
            self.session.commit()
            self.session.refresh(record)
        return record

    def list_logs(self, patient_id: Optional[str] = None, user_id: Optional[str] = None) -> List[AuditLogRecord]:
        query = select(AuditLogRecord)
        if patient_id and user_id:
            query = query.where(
                (AuditLogRecord.patient_id == patient_id) | (AuditLogRecord.user_id == user_id)
            )
        elif patient_id:
            query = query.where(
                (AuditLogRecord.patient_id == patient_id) | (AuditLogRecord.user_id == patient_id)
            )
        elif user_id:
            query = query.where(
                (AuditLogRecord.user_id == user_id) | (AuditLogRecord.patient_id == user_id)
            )
        return self.session.exec(query).all()
