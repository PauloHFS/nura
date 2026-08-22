# Testes numéricos parametrizados para validação estrita do MAPE < 5%

## Contexto & Decisão

A verificação do KPI principal de acurácia matemática (MAPE < 5%) não pode depender de testes E2E com LLMs devido à estocasticidade de geração. Decidimos criar uma suíte de testes numéricos parametrizados com Pytest que executa combinações do Solucionador Linear contra a base vetorial local, assegurando de forma determinística que o desvio calórico e de macronutrientes permaneça abaixo de 5%.

## Consequências

- Validação quantitativa e matemática automatizada no pipeline de CI/CD.
- Prevenção imediata de regressões na lógica de montagem de refeições.
