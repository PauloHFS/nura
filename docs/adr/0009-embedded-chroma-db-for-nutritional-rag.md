# Chroma DB embutido local para o RAG Nutricional (USDA/TBCA)

## Contexto & Decisão

Para evitar dependências de serviços de nuvem externos e minimizar a latência nas consultas com restrições de metadados nutricionais, decidimos utilizar a biblioteca Chroma DB rodando em modo local embutido (*embedded*) persistida em disco.

## Consequências

- Latência ultrabaixa em consultas RAG (< 50ms).
- Sem custos de infraestrutura de bancos vetoriais gerenciados em nuvem.
