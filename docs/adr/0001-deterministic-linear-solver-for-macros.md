# Separar a geração conceitual (LLM) do cálculo de porções (Solucionador Linear)

## Contexto & Decisão

Modelos de linguagem (LLMs) são probabilísticos e falham ao resolver equações de restrição calórica e de macronutrientes com precisão estrita (meta de erro < 5%). Decidimos usar o LLM apenas para interpretar intenções do usuário e propor combinações de refeições, delegando a determinação das gramagens exatas dos ingredientes a um solucionador de programação linear determinístico (ex: OR-Tools/SciPy) consultando tabelas nutricionais (USDA/TBCA no Chroma DB).

## Consequências

- Erro calórico/macro garantido dentro do limite exato (MAPE < 5%).
- O pipeline de geração exige duas etapas: busca/proposta conceitual + resolução matemática.
