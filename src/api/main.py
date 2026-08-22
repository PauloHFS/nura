from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from src.adapters.database import create_db_and_tables

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
