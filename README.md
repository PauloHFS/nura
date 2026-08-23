# 🌿 Nura (PIHD) — Protocolo de Inteligência Artificial Híbrida Direcionado

> **Ecossistema de telenutrição automatizado e hiperpersonalizado (Versão Paciente Zero)**  
> Combina interface conversacional empática baseada no protocolo de Entrevista Motivacional (OARS), orquestração agêntica via **Hermes Agent** / **Telegram Bot**, motor nutricional determinístico exato (Programação Linear via SciPy/OR-Tools) e gestão de infraestrutura doméstica com **Grocy**.

---

## 🎯 Sobre o Projeto

O **Nura (PIHD)** resolve o problema de dietas estocásticas geradas por LLMs puras (que frequentemente subestimam calorias ou alucinam macronutrientes) e elimina a alta fricção manual do acompanhamento nutricional tradicional.

### Destaques da Arquitetura:
- **🧮 Motor Nutricional Determinístico**: Cálculo exato de gramagens de alimentos satisfazendo metas calóricas/macros com erro $MAPE < 5\%$ via **Programação Linear (SciPy / OR-Tools)**.
- **🛡️ Guardrail Léxico ($O(n)$)**: Autômato de **Aho-Corasick** em memória local para interceptar e rejeitar prescrições danosas (ex: jejum restritivo) em menos de **$5\text{ms}$** (*fail-closed*).
- **🤖 Interface Agêntica Primária (Hermes Agent / Telegram Bot)**: Comunicação agêntica desacoplada com protocolo **OARS** (Perguntas abertas, Afirmações, Escuta reflexiva, Resumos) e checkpoints de estado via **LangGraph**.
- **📦 Integração com Grocy**: Consulta de estoque doméstico e validade de alimentos como *soft priors*, executando deduções estritamente após **Confirmação Conversacional**.
- **🩺 Painel Assíncrono de Auditoria Nutricional**: Dashboard HTML/REST (`/api/audit/dashboard`) para inspeção assíncrona por profissionais de nutrição com registro de pareceres clínicos no SQLite.
- **🏛️ Arquitetura Hexagonal (Ports & Adapters)**: Domínio nutricional e solver completamente isolados de I/O (Chroma DB, Grocy, Telegram, Hermes, SQLite).

---

## 📐 Estrutura do Projeto

```text
nura/
├── .agentic-qa/              # Suíte de Agentic QA (Personas, Stories e SLAs de teste)
├── docs/
│   └── adr/                  # Architectural Decision Records (0001 até 0014)
├── src/
│   ├── adapters/             # Adaptadores de I/O (Hermes, Telegram, Grocy, Chroma DB)
│   ├── api/                  # Endpoints REST FastAPI (`main.py`)
│   ├── domain/               # Modelos de domínio (SQLModel, Pydantic) e Portas Hexagonais
│   ├── graph/                # Orquestrador LangGraph (StateGraph, Checkpoints SQLite)
│   └── services/             # Motor de Otimização Nutricional e Ingestão de Dados
├── tests/                    # Suíte completa de testes automatizados (Pytest)
├── CONTEXT.md                # Glossário e Linguagem Ubíqua do Domínio
├── Dockerfile                # Multistage Build otimizado para produção Python 3.10
├── docker-compose.yml        # Orquestração do backend + volumes de persistência
└── pyproject.toml            # Dependências do projeto
```

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.10+
- `uv` (recomendado) ou `pip`
- Docker & Docker Compose (para execução em container)

### 1. Clonar o Repositório e Configurar Ambiente
```bash
git clone https://github.com/PauloHFS/nura.git
cd nura

# Copiar arquivo de ambiente
cp .env.example .env
```

### 2. Criar Ambiente Virtual e Instalar Dependências
```bash
# Usando uv (recomendado para alta velocidade)
uv venv
source .env/bin/activate
uv pip install -e .

# Ou usando venv/pip tradicional
python3 -m venv .venv
source .venv/bin/activate
pip install -r pyproject.toml
```

### 3. Semear a Base Vetorial Nutricional (Chroma DB Local)
Alimenta o Chroma DB embutido (`./data/chroma_data`) com a tabela de alimentos USDA/TBCA:
```bash
python -m src.services.seed_nutrition_db
```

### 4. Iniciar o Servidor FastAPI
```bash
uvicorn src.api.main:app --reload --port 8000
```
- **Documentação Swagger/OpenAPI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Painel de Auditoria Nutricional**: [http://localhost:8000/api/audit/dashboard](http://localhost:8000/api/audit/dashboard)
- **Health Check**: `GET http://localhost:8000/health`

---

## 🤖 Conectando os Canais Conversacionais

### 🌐 A. Hermes Agent (Recomendado / ADR-0014)
O Nura expõe uma API REST estruturada para integração agêntica:
- **Enviar Mensagem**: `POST http://localhost:8000/api/v1/hermes/message`
  ```json
  {
    "session_id": "hermes-sess-001",
    "user_id": "paciente-01",
    "text": "Olá Nura, quero gerar meu cardápio de hoje",
    "metadata": {}
  }
  ```
- **Registrar Outbound Webhook**: `POST http://localhost:8000/api/v1/hermes/outbound`

### 📱 B. Telegram Bot (ADR-0006)
1. Crie um bot no Telegram via [@BotFather](https://t.me/BotFather) e obtenha o `TELEGRAM_BOT_TOKEN`.
2. Adicione o token no `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyZ
   ```
3. Registre o webhook do seu servidor no Telegram:
   ```bash
   curl -X POST "https://api.telegram.org/bot<SEU_TOKEN>/setWebhook?url=https://seu-dominio.com/webhook/telegram"
   ```

---

## 🐳 Guia de Deploy e Produção

### 📦 Opção 1: Deploy com Docker Compose (VPS / Servidor Próprio)
A forma mais simples e robusta para rodar o Nura com persistência automática de volumes:

```bash
# 1. Configurar variáveis de ambiente no servidor
cp .env.example .env
nano .env

# 2. Subir a aplicação em segundo plano
docker compose up -d --build

# 3. Verificar logs e status da aplicação
docker compose logs -f
curl http://localhost:8000/health
```

### ☁️ Opção 2: Deploy em PaaS (Railway / Render / Fly.io)
1. **Conecte o repositório GitHub** à plataforma.
2. A plataforma detectará automaticamente o `Dockerfile` multistage.
3. **Configure as Variáveis de Ambiente** no painel da plataforma:
   - `TELEGRAM_BOT_TOKEN`: Token do Telegram Bot
   - `GROCY_BASE_URL`: URL da sua instância do Grocy
   - `GROCY_API_KEY`: Chave de API do Grocy
   - `DATABASE_URL`: `sqlite:////data/nura.db`
   - `CHROMA_PERSIST_PATH`: `/data/chroma_data`
4. **Monte um Volume Persistente** no caminho `/data` para preservar a base vetorial do Chroma DB e o banco SQLite entre atualizações de código.

---

## 🧪 Testes Automatizados & Agentic QA

O projeto conta com suíte de testes com **100% de aprovação**:

### Executar Suíte de Testes (Pytest)
```bash
pytest --verbose
```

### Estrutura de Agentic QA (`.agentic-qa/`)
O Nura inclui uma especificação completa de **Agentic QA** para emulação automatizada de personas e verificação de SLAs:
- **`framework.md`**: SLAs de desempenho ($<5\text{ms}$ Guardrail, $MAPE < 5\%$ Solver).
- **`personas/`**: Profiles YAML (`paciente_fundador.yaml`, `nutricionista_auditora.yaml`).
- **`stories/`**: Roteiros declarativos (`smoke.md`, `conversational_coaching.md`, `audit_dashboard.md`).

---

## 📑 Documentação e Decisões de Arquitetura (ADRs)

Toda a evolução do sistema está documentada em **`docs/adr/`**:
- `0001-deterministic-linear-solver-for-macros.md`
- `0002-grocy-inventory-as-soft-constraint.md`
- `0003-system-prompting-for-oars-coach.md`
- `0005-aho-corasick-automaton-for-lexical-guardrails.md`
- `0006-telegram-bot-as-primary-conversational-interface.md`
- `0007-conversational-confirmation-for-inventory-deduction.md`
- `0010-langgraph-for-deterministic-agentic-orchestration.md`
- `0014-hermes-agent-as-primary-conversational-channel.md`

---

## 📄 Licença

Desenvolvido para o ecossistema Nura / PIHD. Todos os direitos reservados.
