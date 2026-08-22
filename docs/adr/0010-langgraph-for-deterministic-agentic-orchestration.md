# LangGraph para orquestração agêntica baseada em Grafo de Estados

## Contexto & Decisão

O ecossistema Nura requer intercalação estrita entre etapas de IA generativa (OARS/Coach) e componentes determinísticos imperativos (Solucionador Linear, Guardrails Aho-Corasick, Chamadas REST do Grocy). Decidimos adotar o LangGraph para controlar o fluxo via grafos de estado explícitos (*StateGraph*) com gerenciamento nativo de checkpoints de sessão.

## Consequências

- Controle determinístico do fluxo de conversação e transições de estado.
- Resiliência com persistência de estado (*checkpointers*) para retomar interações interrompidas no Telegram.
