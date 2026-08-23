# Nura / PIHD (Protocolo de Inteligência Artificial Híbrida Direcionado)

Ecossistema de telenutrição automatizado e hiperpersonalizado que une inteligência artificial generativa, motores determinísticos exatos e gestão de infraestrutura doméstica.

## Domain Language

**Paciente-Fundador**:
O usuário único e desenvolvedor no estágio MVP, utilizando o sistema em si mesmo para validar o ciclo de aderência e automação.
_Avoid_: Usuário genérico, cliente, consumidor.

**Motor Nutricional Determinístico**:
Componente algorítmico numérico (solucionador linear) responsável pelo cálculo de gramagens e cumprimento estrito de metas calóricas e de macronutrientes.
_Avoid_: Gerador de dieta por LLM, calculadora estocástica.

**Inventário**:
O registro virtual de alimentos, validade e equipamentos domésticos mantido no Grocy, utilizado como prioridade flexível pelo motor de sugestões.
_Avoid_: Despensa estática, estoque rígido.

**Entrevista Motivacional (OARS)**:
Protocolo comportamental de comunicação (Perguntas abertas, Afirmações, Escuta reflexiva, Resumos) adotado pelo Coach de IA para acompanhamento passivo e engajamento sem registro manual de calorias.
_Avoid_: Bot de comandos, log manual.

**Guardrail Léxico**:
Filtro de segurança determinístico local (autômato Aho-Corasick em $O(n)$) que intercepta e invalida respostas da IA que contenham prescrições danosas ou extremas antes do envio ao cliente.
_Avoid_: Moderador genérico, prompt de segurança embutido no LLM.

**Auditoria Nutricional**:
Interface de revisão assíncrona pós-geração para inspeção e ajustes por profissional humano de nutrição.
_Avoid_: Aprovação síncrona, gatekeeper.

**Busca de Suporte Nutricional**:
Expansão automática da consulta vetorial no Chroma DB para incluir alimentos complementares quando uma combinação inicial não atinge viabilidade matemática.
_Avoid_: Busca genérica, fallback estático.

**Variável de Folga (Slack Variable)**:
Parâmetro de penalidade controlada no solucionador linear que permite relaxar suavemente metas secundárias caso o sistema exato não convirja.
_Avoid_: Violação de meta, aproximação livre.

**Confirmação Conversacional**:
Ação no chat onde o usuário valida que consumiu a refeição proposta, servindo como gatilho único para atualização de saldo no Grocy.
_Avoid_: Baixa automática, dedução otimista.

**Canal do Coach (Hermes Agent / Telegram Bot)**:
Interface conversacional agêntica desacoplada (via adaptadores REST / Webhook) para interação ativa com o Paciente-Fundador, notificações proativas de check-in OARS e coleta de confirmações de consumo.
_Avoid_: Interface Web UI acoplada, PWA, interface de chat monolítica.

**Orquestrador de Grafo de Estados (StateGraph)**:
Estrutura determinística do LangGraph que intercala nós de linguagem (LLM), nós de resolução matemática (OR-Tools) e checagens de segurança (Aho-Corasick) mantendo a persistência da conversa.
_Avoid_: Agente autônomo livre, loop de prompts.

**Base Nutricional Vetorial**:
Instância local do Chroma DB indexando ingredientes das tabelas USDA e TBCA enriquecidos com metadados para busca híbrida semântica e paramétrica.
_Avoid_: Tabela relacional simples, banco de receitas estático.

**Estado do Paciente (Checkpoint)**:
Persistência relacional do histórico, peso, metas calóricas ativas e estágio da conversação do Paciente-Fundador.
_Avoid_: Variável de memória, estado volátil.

**Arquitetura Hexagonal (Ports & Adapters)**:
Organização modular em `src/` que isola completamente o domínio nutricional e o solucionador determinístico das dependências externas de I/O (Grocy, Telegram, Chroma, SQLite).
_Avoid_: Arquitetura em camadas acoplada, código monolítico sem interfaces.

**Teste de Integração Numérica**:
Validação determinística parametrizada (Pytest) executando o solucionador contra a base vetorial sem chamadas ao LLM para comprovar que o erro calórico/macro satisfaz o limite $MAPE < 5\%$.
_Avoid_: Teste E2E estocástico, teste visual manual.
