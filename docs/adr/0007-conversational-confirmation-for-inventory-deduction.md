# Baixa de estoque no Grocy orientada à Confirmação Conversacional

## Contexto & Decisão

Deduzir os mantimentos do Grocy no momento em que uma refeição é gerada corrompe a integridade da despensa quando o usuário altera ou não consome a refeição. Decidimos que a chamada de mutação de saldo na API do Grocy só será executada após a confirmação conversacional explícita do usuário no Telegram ("Sim, consumi").

## Consequências

- Integridade e acurácia do inventário no Grocy preservadas.
- O Coach precisa gerenciar o estado da refeição (Pendente -> Confirmada) entre os check-ins diários.
