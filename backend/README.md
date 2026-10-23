# Backend

FastAPI + SQLAlchemy 2 (async) + Alembic + PostgreSQL.

## Tests

Unit tests need nothing but dependencies:

```bash
uv run pytest tests --ignore=tests/integration
```

Integration tests (repositories) run against a real PostgreSQL. Create a separate
database whose name ends with `_test` (the tests refuse to run otherwise):

```sql
CREATE DATABASE pastry_test;
```

Then run:

```bash
TEST_DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@localhost:5432/pastry_test uv run pytest
```

The schema is created from the ORM metadata. Every test runs inside a transaction
that is rolled back, so tests do not affect each other. Without `TEST_DATABASE_URL`
the integration tests are skipped.
