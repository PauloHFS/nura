from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Depends
from src.adapters.database import create_db_and_tables
from src.services.meal_optimizer import MealOptimizerService, OptimizationRequest, OptimizationResult
from src.adapters.chroma_adapter import ChromaNutritionalRepository

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

def get_chroma_repo() -> ChromaNutritionalRepository:
    return ChromaNutritionalRepository()

@app.post("/api/meal/optimize", response_model=OptimizationResult)
def optimize_meal(
    request: OptimizationRequest,
    repo: ChromaNutritionalRepository = Depends(get_chroma_repo)
):
    optimizer = MealOptimizerService(repo=repo)
    return optimizer.solve(request)
