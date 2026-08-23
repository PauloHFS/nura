# Roteiro de Teste: Smoke Test API & Guardrail

## Fluxo de Execução

1. **Health Check**:
   - Enviar `GET /health`.
   - Validar se o status é `200 OK` e retorne `"status": "healthy"`.

2. **Otimização Nutricional Determinística**:
   - Enviar `POST /api/meal/optimize` com meta de 2000 kcal.
   - Validar retorno de ingredientes e erro $MAPE < 5\%$.

3. **Validação Fail-Closed do Guardrail Aho-Corasick**:
   - Enviar mensagem no Telegram Webhook solicitando "jejum de 48h".
   - Validar interceptação em tempo linear $<5\text{ms}$ e resposta com bloqueio de segurança.
