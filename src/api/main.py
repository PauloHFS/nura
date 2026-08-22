from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from fastapi import FastAPI, Depends, Request
from src.adapters.database import create_db_and_tables
from src.services.meal_optimizer import MealOptimizerService, OptimizationRequest, OptimizationResult
from src.adapters.chroma_adapter import ChromaNutritionalRepository
from src.adapters.telegram_adapter import parse_telegram_update

_chroma_repo_instance: Optional[ChromaNutritionalRepository] = None

def get_chroma_repo() -> ChromaNutritionalRepository:
    global _chroma_repo_instance
    if _chroma_repo_instance is None:
        _chroma_repo_instance = ChromaNutritionalRepository()
    return _chroma_repo_instance

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
async def telegram_webhook(request: Request):
    payload = await request.json()
    update = parse_telegram_update(payload)
    return {"status": "ok", "update_id": update.update_id}
