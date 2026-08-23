# Framework de Execução Agentic QA - Nura (PIHD)

## Regras Globais de Teste e Asserção

1. **Latência de Interceptação do Guardrail Léxico**:
   - Todas as varreduras via Autômato Aho-Corasick DEVEM responder com latência < 5ms.
   - Qualquer instrução de alto risco (ex: "jejum de 48h", "0 carboidratos", "calorias negativas") DEVE resultar em `is_safe=False` e ser bloqueada *fail-closed*.

2. **Acurácia Nutricional do Solucionador Linear**:
   - As metas de calorias e macronutrientes GERADAS pelo solucionador linear DEVEM apresentar erro absoluto percentual médio (MAPE) inferior a 5%.

3. **Confirmação Conversacional de Estoque (Grocy)**:
   - Nenhuma baixa de estoque no Grocy DEVE ocorrer antes da confirmação conversacional explícita do usuário no Telegram ("sim", "consumi").

4. **Painel de Auditoria Assíncrona**:
   - O dashboard `/api/audit/dashboard` e endpoints REST `/api/audit/*` DEVEM responder com status 200 e estruturas JSON válidas para inspeção de nutricionistas humanos.
