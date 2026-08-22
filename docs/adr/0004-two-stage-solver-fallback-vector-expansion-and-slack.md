# Expansão vetorial e variáveis de folga como fallback no Solucionador Linear

## Contexto & Decisão

Quando os alimentos selecionados não conseguem satisfazer as restrições calóricas e de macros (ex: tentar atingir alta proteína com alimentos de baixa densidade proteica), o solucionador linear falharia. Decidimos implementar um fallback em duas etapas: 1) expandir dinamicamente a busca no Chroma DB por alimentos de suporte nutricional (ex: ovos, frango, proteína concentrada); 2) se ainda inviável, aplicar variáveis de folga com penalidade severa na função objetivo para permitir pequenas flexibilizações controladas informando o usuário.

## Consequências

- Elimina falhas de geração de refeições mantendo a previsibilidade numérica.
- Requer rotinas de busca secundária no Chroma DB e configuração de penalidades no solucionador.
