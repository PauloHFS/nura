# Utilizar autômato Aho-Corasick para o Guardrail Léxico inline

## Contexto & Decisão

Para satisfazer a restrição não-funcional de resposta em menos de 3 segundos no pipeline RAG, verificações semânticas síncronas via LLM/Llama Guard são inviáveis. Decidimos utilizar um autômato de busca de padrões múltiplos Aho-Corasick rodando em memória local no middleware. O autômato executa em tempo linear $O(n)$ em relação ao tamanho da resposta com overhead $< 5\text{ms}$.

## Consequências

- Latência insignificante na validação de segurança fail-closed.
- Requer manutenção de uma lista explícita de padrões e termos restritos.
