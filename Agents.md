# Mercury Agent Guide

## Purpose and stack

Mercury is a FastAPI starter with JWT authentication, PostgreSQL persistence, Redis, Flyway migrations, and optional Google OIDC. Phase 0 adds an opt-in Celery worker and LangGraph run API while keeping the default Compose experience focused on the API and its core dependencies.

| Layer | Choice |
|---|---|
| API/server | FastAPI and Uvicorn (`src/app.py` → `src/main.py`) |
| Configuration | Pydantic v2 and `pydantic-settings`; `*_FILE` secrets override plain environment values |
| Database | PostgreSQL, SQLAlchemy 2, Flyway SQL migrations |
| Cache/queue | Redis DB 0 for cache and DB 1 for Celery broker/results |
| Worker/agent | Celery, LangGraph, OpenAI-compatible LLM endpoint |
| Tests/tooling | pytest, unittest, Ruff, Bandit, Trivy image scans |

## Runtime and service layout

- `src/routes/` defines HTTP routes; controllers and repositories hold business/database operations.
- `src/database/postgres_db.py` creates SQLAlchemy sessions. Flyway owns schema creation; do not use `Base.metadata.create_all()`.
- `src/main.py` uses FastAPI lifespan for configuration validation, Redis initialization, and cleanup.
- `/v1/health/live` checks process liveness; `/v1/health/ready` checks Postgres and Redis; `/v1/health` aliases liveness.
- `/metrics` exposes Prometheus metrics. Request middleware emits JSON completion logs and an `X-Request-ID`; OTLP traces require `OTEL_ENABLED=true`.
- When `MERCURY_AGENT_ENABLED=true`, `POST /v1/runs` enqueues a run and `GET /v1/runs/{id}` returns its state. `src/worker/tasks.py` owns execution and retries; `src/agent/graph.py` invokes the configured LLM.

## Configuration and local seed

Copy `.env.dist` to `.env` for local Compose. The default JWT secret is accepted only with `APP_ENV=local`. For mounted secrets, provide e.g. `JWT_SECRET_KEY_FILE=/run/secrets/jwt_secret`; supported secret fields are JWT, Postgres, Google OIDC, and LLM API keys.

Flyway migrations are flat `V{n}__description.sql` files in `src/migrations/` and are immutable once applied. V3 is historical. V4 removes only the unchanged default admin hash, preserving an account whose password was changed. `src/seed_local_admin.py` creates the default admin only when `APP_ENV=local`; Compose runs it after migrations.

## Compose and CI

- `docker compose up --build` runs the implicit core stack.
- `docker compose --profile worker up --build` adds the worker.
- `MERCURY_AGENT_ENABLED=true docker compose --profile worker --profile agent up --build` enables run routes, worker, and local mock LLM. Set `LLM_BASE_URL` and `LLM_API_KEY` for another OpenAI-compatible endpoint.
- Test and tool containers are under the separate `test` profile. Use the `ci/*.sh` wrappers or documented README commands.
- GitHub Actions and GitLab CI should remain aligned for unit/integration tests, lint, Bandit, Trivy image scans, and main-branch publishing to Docker Hub and GHCR. GitLab publishing requires `DOCKER_HUB_USERNAME`, `DOCKER_HUB_ACCESS_TOKEN`, `GHCR_USERNAME`, and `GHCR_TOKEN` variables.

## Validation

Run the focused Phase 0 tests, unit and integration suites, lint and Bandit checks. For local end-to-end verification use an isolated Compose project and disposable volume; do not remove a user's existing `.env` or database volume. Verify core health/readiness, the opt-in run lifecycle using the local mock, and that flushing Redis DB 0 leaves broker work in DB 1.
