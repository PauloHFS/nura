# ADR-0014: Adotar Hermes Agent como Canal Agêntico Primário via Porta Hexagonal

## Contexto & Decisão

A decisão anterior (ADR-0006) fixava o Telegram Bot como interface conversacional única do MVP. Com a evolução da arquitetura do Nura e a necessidade de integração com o ecossistema agêntico do Hermes Agent, decidimos abstrair a interface conversacional sob uma porta genérica de canal (`CoachChannelPort`) na Arquitetura Hexagonal, adotando o **Hermes Agent** como canal agêntico primário via adaptador REST (`HermesAdapter` / `/api/v1/hermes/message`).

## Consequências

- **Desacoplamento Total**: O orquestrador LangGraph, o solucionador linear, a persistência relacional e o Guardrail Aho-Corasick não possuem dependência de nenhum canal específico (Telegram ou Hermes).
- **Rastreabilidade de Sessão**: Cada interação transporta o `session_id` (`x-hermes-session-id`), preservando os checkpoints do `PatientState` no SQLite.
- **Notificações Proativas**: O sistema expõe contrato de despacho de mensagens proativas via webhook de saída (`POST /hermes/outbound`) para check-ins do protocolo OARS.
- **Retrocompatibilidade**: O adaptador do Telegram Bot continua existindo como uma porta secundária de acesso.
