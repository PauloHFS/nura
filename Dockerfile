# Multistage Dockerfile para o Nura (PIHD)
FROM python:3.10-slim AS builder

WORKDIR /app

# Instala ferramentas de compilação básicas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt-get/lists/*

# Instala uv para resolução rápida de dependências
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copia arquivos de requisitos / projeto
COPY . /app

# Cria ambiente virtual e instala dependências
RUN uv venv /app/.venv && . /app/.venv/bin/activate && uv pip install -r <(python3 -c "
import tomllib
try:
    with open('pyproject.toml', 'rb') as f:
        print('\n'.join(tomllib.load(f).get('project', {}).get('dependencies', [])))
except Exception:
    pass
" 2>/dev/null) || uv pip install fastapi uvicorn sqlmodel chromadb scipy OR-Tools requests langgraph langgraph-checkpoint pydantic

# Estágio final de execução
FROM python:3.10-slim AS runner

WORKDIR /app

# Instala dependências de runtime de C/C++ (para OR-Tools/SciPy)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt-get/lists/*

# Copia código e venv do estagio builder
COPY --from=builder /app/.venv /app/.venv
COPY . /app

# Garante diretório de dados persistentes
RUN mkdir -p /data/chroma_data

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL="sqlite:////data/nura.db" \
    CHROMA_PERSIST_PATH="/data/chroma_data"

EXPOSE 8000

# Script de inicialização (semente da base vetorial + uvicorn)
CMD ["sh", "-c", "python -m src.services.seed_nutrition_db && uvicorn src.api.main:app --host 0.0.0.0 --port 8000"]
