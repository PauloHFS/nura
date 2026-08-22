# Arquitetura Hexagonal (Ports & Adapters) para isolamento do motor determinístico

## Contexto & Decisão

Para permitir que o motor de otimização matemática (solucionador linear) e os guardrails de segurança sejam testados de forma puramente unitária e determinística em milissegundos sem depender de chamadas de rede ou I/O, decidimos organizar o codebase em Arquitetura Hexagonal (`domain`, `services`, `adapters`, `graph`, `api`).

## Consequências

- Desacoplamento completo das bibliotecas de I/O (Grocy API, Telegram Bot API, Chroma DB SDK).
- Facilidade para mockar ou substituir adaptadores de infraestrutura durante o ciclo de desenvolvimento.
