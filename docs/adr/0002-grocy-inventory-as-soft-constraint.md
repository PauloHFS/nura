# Tratar o inventário do Grocy como restrição flexível (Soft Constraint)

## Contexto & Decisão

A despensa física e a despensa virtual no Grocy frequentemente sofrem de desassincronia por esquecimento de bipes de entrada/saída pelo usuário. Decidimos tratar os itens do Grocy como prioridade flexível (*soft prior*) na recomendação de receitas, com reconciliação conversacional no chat, em vez de um bloqueio rígido (*hard constraint*) que impediria a geração de sugestões quando o estoque estivesse desatualizado.

## Consequências

- Redução drástica de fricção no uso diário do sistema.
- O sistema precisará de fluxos de atualização conversacional para sincronizar o saldo do Grocy via API quando o usuário confirmar o uso de itens não listados.
