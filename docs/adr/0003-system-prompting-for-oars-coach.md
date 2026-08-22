# Utilizar System Prompt e RAG para o protocolo OARS no MVP em vez de Fine-Tuning LoRA

## Contexto & Decisão

Embora o Fine-Tuning LoRA permita adaptar o tom e protocolo comportamental de um modelo local, ele exige um conjunto de dados rotulado e validado que ainda não existe no MVP. Decidimos implementar o protocolo de Entrevista Motivacional (OARS) via Engenharia de Prompt Estruturada e Few-Shot/RAG, diferindo o Fine-Tuning para fases posteriores após coleta de histórico real do Paciente-Fundador.

## Consequências

- Implementação imediata no MVP sem custo de treinamento de pesos.
- Facilidade para ajustar as diretrizes do Coach apenas alterando arquivos de prompt/contexto.
