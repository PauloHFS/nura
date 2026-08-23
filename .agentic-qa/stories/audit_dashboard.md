# Roteiro de Teste: Dashboard e Endpoints de Auditoria Nutricional

## Fluxo de Execução

1. **Navegação no Dashboard HTML**:
   - Requisitar `GET /api/audit/dashboard`.
   - Verificar retorno `200 OK` com conteúdo HTML contendo título de auditoria.

2. **Inspeção de Planos Alimentares**:
   - Requisitar `GET /api/audit/plans`.
   - Validar lista JSON contendo registros de planos e métricas de MAPE.

3. **Submissão de Parecer de Nutricionista**:
   - Enviar `POST /api/audit/feedback` com nota e status `approved`.
   - Validar gravação da auditoria no SQLite e retorno de `feedback_id`.
