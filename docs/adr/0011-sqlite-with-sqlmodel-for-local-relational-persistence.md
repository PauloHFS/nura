# SQLite com SQLModel para persistência relacional local no MVP

## Contexto & Decisão

No estagio MVP (Paciente Zero), o banco de dados relacional precisa de infraestrutura zero mantendo facilidade de backup. Decidimos utilizar SQLite com a camada ORM/Schema SQLModel (Pydantic + SQLAlchemy), garantindo que futuras migrações para PostgreSQL ocorram sem alteração do código de domínio.

## Consequências

- Nenhuma dependência de container ou servidor de banco de dados no ambiente MVP.
- Transição simplificada para PostgreSQL via alteração de connection string da SQLAlchemy quando necessário.
