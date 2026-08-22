from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from fastapi import FastAPI, Depends, Request
from src.adapters.database import create_db_and_tables
from src.services.meal_optimizer import MealOptimizerService, OptimizationRequest, OptimizationResult
from src.adapters.chroma_adapter import ChromaNutritionalRepository
from src.adapters.telegram_adapter import parse_telegram_update, TelegramClient
from src.graph.orchestrator import NuraOrchestrator

_chroma_repo_instance: Optional[ChromaNutritionalRepository] = None
_telegram_client_instance: Optional[TelegramClient] = None
_orchestrator_instance: Optional[NuraOrchestrator] = None

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
    repo: ChromaNutritionalRepository = Depends(get_chroma_repo)
):
    optimizer = MealOptimizerService(repo=repo)
    return optimizer.solve(request)

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
