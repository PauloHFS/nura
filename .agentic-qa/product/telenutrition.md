# Regras de Negócio e Contexto de Produto: Telenutrição Nura (PIHD)

## 1. Telegram Bot & Orquestrador LangGraph
- O bot conversa via protocolo de Entrevista Motivacional (OARS) com o Paciente-Fundador.
- Transições de estado: `onboarding` -> `oars_coaching` -> `meal_planning` -> `inventory_reconciliation`.
- Respostas do Coach são envelopadas pelo middleware Guardrail Aho-Corasick.

## 2. Motor Nutricional (SciPy / OR-Tools)
- Calcula proporção exata de gramagens de alimentos para atingir metas de Calorias, Proteínas, Carboidratos e Gorduras.
- Prioriza itens em estoque no Grocy com data de vencimento mais próxima (*soft prior*).

## 3. Painel de Auditoria Assíncrona
- Disponibiliza visualização web (`/api/audit/dashboard`) para nutricionistas acompanharem cardápios e logs.
- Registra feedback com notas, autor e status (`approved`, `flagged`, `adjusted`).
