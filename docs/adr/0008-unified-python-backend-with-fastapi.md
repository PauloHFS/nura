# Backend unificado em Python com FastAPI

## Contexto & Decisão

Devido à dependência central de bibliotecas matemáticas e científicas de otimização (OR-Tools / SciPy), armazenamento vetorial (Chroma DB) e orquestração de IA (LangGraph), decidimos unificar todo o backend do Nura em Python com FastAPI.

## Consequências

- Evita custos de serialização inter-processos e latência de rede que ocorreriam com arquitetura poliglota.
- Simplifica o deployment e a manutenção do ecossistema em um único ambiente virtual Python.
