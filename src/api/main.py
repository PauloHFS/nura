import src.patch_socketpair
from contextlib import asynccontextmanager
from typing import AsyncGenerator, List, Optional
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from src.adapters.database import create_db_and_tables, get_session
from src.domain.models import (
    PatientProfile,
    MealPlanRecord,
    NutritionPlanRecord,
    AuditLogRecord,
    NutritionistFeedbackRecord,
)
from src.services.meal_optimizer import MealOptimizerService, OptimizationRequest, OptimizationResult
from src.adapters.chroma_adapter import ChromaNutritionalRepository
from src.adapters.grocy_adapter import GrocyAdapter
from src.adapters.repositories import NutritionPlanRepository, AuditLogRepository
from src.adapters.telegram_adapter import parse_telegram_update, TelegramClient
from src.adapters.hermes_adapter import (
    HermesAdapter,
    HermesRequestPayload,
    HermesResponsePayload,
    HermesOutboundSubscriptionPayload,
)
from src.domain.ports.coach_channel_port import ChannelMessageRequest
from src.graph.orchestrator import NuraOrchestrator

_chroma_repo_instance: Optional[ChromaNutritionalRepository] = None
_telegram_client_instance: Optional[TelegramClient] = None
_orchestrator_instance: Optional[NuraOrchestrator] = None
_hermes_adapter_instance: Optional[HermesAdapter] = None
_grocy_adapter_instance: Optional[GrocyAdapter] = None

def get_grocy_adapter() -> GrocyAdapter:
    global _grocy_adapter_instance
    if _grocy_adapter_instance is None:
        _grocy_adapter_instance = GrocyAdapter()
    return _grocy_adapter_instance

def get_chroma_repo() -> ChromaNutritionalRepository:
    global _chroma_repo_instance
    if _chroma_repo_instance is None:
        _chroma_repo_instance = ChromaNutritionalRepository()
    return _chroma_repo_instance
def get_telegram_client() -> TelegramClient:
    global _telegram_client_instance
    if _telegram_client_instance is None:
        _telegram_client_instance = TelegramClient(bot_token="NURA_BOT_TOKEN")
    return _telegram_client_instance

def get_orchestrator() -> NuraOrchestrator:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = NuraOrchestrator()
    return _orchestrator_instance
def get_hermes_adapter(orchestrator: NuraOrchestrator = Depends(get_orchestrator)) -> HermesAdapter:
    global _hermes_adapter_instance
    if _hermes_adapter_instance is None:
        _hermes_adapter_instance = HermesAdapter(orchestrator=orchestrator)
    return _hermes_adapter_instance

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_db_and_tables()
    yield

app = FastAPI(
    title="Nura (PIHD) API",
    description="Protocolo de Inteligência Artificial Híbrida Direcionado",
    version="0.1.0",
    lifespan=lifespan,
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "nura-api",
        "architecture": "hexagonal",
        "version": "0.1.0",
    }

@app.post("/api/meal/optimize", response_model=OptimizationResult)
def optimize_meal(
    request: OptimizationRequest,
    repo: ChromaNutritionalRepository = Depends(get_chroma_repo),
    grocy_adapter: GrocyAdapter = Depends(get_grocy_adapter),
    session: Session = Depends(get_session),
):
    optimizer = MealOptimizerService(repo=repo, grocy_adapter=grocy_adapter)
    result = optimizer.solve(request)

    audit_repo = AuditLogRepository(session)
    patient_id = request.patient_id or "default_patient"

    if result.success:
        plan_repo = NutritionPlanRepository(session)
        plan_repo.save_plan(
            patient_id=patient_id,
            target_calories=request.target_calories,
            target_protein_g=request.target_protein_g,
            target_carbs_g=request.target_carbs_g,
            target_fat_g=request.target_fat_g,
            mape_error=result.mape_error_percent,
            ingredients=result.ingredients,
        )

    audit_repo.log_action(
        action="meal_optimized" if result.success else "meal_optimization_failed",
        session_id=request.session_id,
        user_id=patient_id,
        patient_id=patient_id,
        payload={
            "target_calories": request.target_calories,
            "total_calories": result.total_calories,
            "mape_error": result.mape_error_percent,
            "fallback_stage_used": result.fallback_stage_used,
            "success": result.success,
            "message": result.message,
        },
    )

    return result
@app.post("/webhook/telegram")
async def telegram_webhook(
    request: Request,
    orchestrator: NuraOrchestrator = Depends(get_orchestrator),
    tg_client: TelegramClient = Depends(get_telegram_client),
):
    payload = await request.json()
    update = parse_telegram_update(payload)
    if update.message and update.message.chat_id:
        chat_id = update.message.chat_id
        user_text = update.message.text
        config = {"configurable": {"thread_id": str(chat_id)}}
        state = {
            "patient_id": str(chat_id),
            "messages": [{"role": "user", "content": user_text}],
            "step": "onboarding",
            "meal_plan_pending": "cardápio" in user_text.lower() or "gerar" in user_text.lower(),
            "last_meal_suggested": None,
            "inventory_confirmed": "sim" in user_text.lower() or "consumi" in user_text.lower(),
            "guardrail_blocked": False,
            "response_text": None,
        }
        final_state = orchestrator.graph.invoke(state, config=config)
        reply = final_state.get("response_text", "Mensagem processada.")
        tg_client.send_message(chat_id=chat_id, text=reply)

    return {"status": "ok", "update_id": update.update_id}
@app.post("/api/v1/hermes/message", response_model=HermesResponsePayload)
def hermes_message_endpoint(
    payload: HermesRequestPayload,
    adapter: HermesAdapter = Depends(get_hermes_adapter),
):
    req = ChannelMessageRequest(
        session_id=payload.session_id,
        user_id=payload.user_id,
        text=payload.text,
        metadata=payload.metadata,
    )
    res = adapter.process_message(req)
    return HermesResponsePayload(
        session_id=res.session_id,
        response_text=res.response_text,
        step=res.step,
        guardrail_blocked=res.guardrail_blocked,
        suggested_actions=res.suggested_actions,
    )

@app.post("/api/v1/hermes/outbound")
def hermes_outbound_subscription(
    payload: HermesOutboundSubscriptionPayload,
    adapter: HermesAdapter = Depends(get_hermes_adapter),
):
    adapter.register_outbound_webhook(payload.session_id, payload.callback_url)
    return {"status": "subscribed", "session_id": payload.session_id}
@app.get("/api/audit/plans")
def list_audit_plans(patient_id: Optional[str] = None, session: Session = Depends(get_session)):
    query = select(NutritionPlanRecord)
    if patient_id:
        query = query.where(NutritionPlanRecord.patient_id == patient_id)
    plans = list(session.exec(query).all())

    query_legacy = select(MealPlanRecord)
    if patient_id:
        query_legacy = query_legacy.where(MealPlanRecord.patient_id == patient_id)
    legacy_plans = session.exec(query_legacy).all()

    plans.extend(legacy_plans)
    return plans

@app.get("/api/audit/logs")
def list_audit_logs(patient_id: Optional[str] = None, session: Session = Depends(get_session)):
    repo = AuditLogRepository(session)
    return repo.list_logs(patient_id=patient_id)

@app.get("/api/audit/patients/{patient_id}")
def get_patient_audit_summary(patient_id: str, session: Session = Depends(get_session)):
    profile = session.exec(select(PatientProfile).where(PatientProfile.patient_id == patient_id)).first()
    plans = list(session.exec(select(NutritionPlanRecord).where(NutritionPlanRecord.patient_id == patient_id)).all())
    legacy_plans = session.exec(select(MealPlanRecord).where(MealPlanRecord.patient_id == patient_id)).all()
    plans.extend(legacy_plans)
    logs = session.exec(select(AuditLogRecord).where(
        (AuditLogRecord.patient_id == patient_id) | (AuditLogRecord.user_id == patient_id)
    )).all()
    feedback = session.exec(select(NutritionistFeedbackRecord).where(NutritionistFeedbackRecord.patient_id == patient_id)).all()
    return {
        "patient_id": patient_id,
        "profile": profile,
        "plans": plans,
        "logs": logs,
        "feedback": feedback,
    }
@app.post("/api/audit/feedback")
def submit_nutritionist_feedback(feedback_data: dict, session: Session = Depends(get_session)):
    rec = NutritionistFeedbackRecord(
        patient_id=feedback_data.get("patient_id", ""),
        meal_plan_id=feedback_data.get("meal_plan_id"),
        nutritionist_name=feedback_data.get("nutritionist_name", "Nutricionista"),
        notes=feedback_data.get("notes", ""),
        status=feedback_data.get("status", "reviewed"),
    )
    session.add(rec)
    session.commit()
    session.refresh(rec)
    return {"status": "ok", "feedback_id": rec.id}

@app.get("/api/audit/dashboard", response_class=HTMLResponse)
def audit_dashboard():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nura - Painel Assíncrono de Auditoria Nutricional</title>
        <style>
            body { font-family: sans-serif; margin: 40px; background: #f4f6f8; }
            h1 { color: #2c3e50; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Painel Assíncrono de Auditoria Nutricional (Nura)</h1>
            <p>Plataforma de inspeção pós-geração e feedback especializado por nutricionistas humanos.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
