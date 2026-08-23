# Roteiro de Teste: Fluxo Conversacional Telegram & Grocy

## Fluxo de Execução

1. **Onboarding & OARS Coaching**:
   - Enviar mensagem inicial `"Olá Nura"` no `/webhook/telegram`.
   - Verificar acolhimento no protocolo OARS.

2. **Geração de Cardápio Semanal**:
   - Enviar mensagem `"Quero gerar meu cardápio"` no `/webhook/telegram`.
   - Verificar acionamento do nó do Solucionador Linear e retorno da sugestão alimentar.

3. **Confirmação de Consumo e Baixa no Grocy**:
   - Enviar mensagem `"Sim, consumi o almoço de frango"`.
   - Verificar acionamento da baixa de estoque no Grocy e resposta de confirmação.
