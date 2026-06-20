# Mercury Agent Guide

## Purpose

Mercury is a small FastAPI backend boilerplate centered on JWT auth, PostgreSQL persistence, Redis initialization, and optional Google OIDC login. The project is intentionally simple: routes call thin controllers, controllers talk directly to SQLAlchemy sessions, and Flyway SQL files own the database schema.

This file is a working analysis for future agents so they can navigate the repository quickly and avoid common mistakes.

**Current release line:** latest tag is `v0.4.0` (Flyway migrations, community standards; `solar.manifest.yaml` included for sun scaffolds).

## Stack Summary

| Layer | Choice |
|-------|--------|
| API | FastAPI `0.128.0` (`fastapi[standard]`) |
| Server | Uvicorn (via `src/app.py`) |
| ORM | SQLAlchemy **2.0** (`DeclarativeBase`, `sessionmaker`) |
| Validation | Pydantic **v2** (`ConfigDict`, `model_dump`) |
| Database | PostgreSQL 16 (Docker), driver `psycopg2-binary` |
| Cache | Redis 7 (initialized at startup; not used in route logic yet) |
| Auth | JWT (`python-jose`) + OAuth2 password flow + Google OIDC |
| Passwords | Passlib (`sha256_crypt` when `JWT_ALGORITHM=HS256`, else `bcrypt`) |
| Migrations | Flyway 10 (flat SQL files under `src/migrations/`) |
| Tests | `unittest` (unit), `pytest` + `TestClient` (integration) |
| Tooling | Docker Compose, Ruff, Bandit, Renovate, GitHub Actions |

## Repository Shape

Top-level areas:

| Path | Role |
|------|------|
| `src/app.py` | **Uvicorn entrypoint** (`python src/app.py` in Docker); loads `main:app` |
| `src/main.py` | **FastAPI application** — `app` object, CORS, `create_all`, Redis init, routers |
| `src/restful_ressources.py` | Central router mounting under `/{API_VERSION}` |
| `src/routes/` | HTTP route definitions (thin; delegate to controllers) |
| `src/controllers/` | Request logic and DB mutation/query logic |
| `src/models/` | SQLAlchemy models (`User` only) |
| `src/schemas/` | Pydantic request/response schemas |
| `src/database/` | PostgreSQL engine/session (`postgres_db.py`), Redis bootstrap (`redis_db.py`) |
| `src/middleware/auth_guard.py` | JWT decoding and auth dependencies |
| `src/utils/` | Password hashing, JWT, OIDC helpers, response filtering, env parsing |
| `src/migrations/` | Flyway SQL: `V1__`, `V2__`, `V3__` |
| `src/integration_tests/` | API-level tests |
| `src/unit_tests/` | Minimal direct-function coverage |
| `ci/` | Shell wrappers for Docker-based lint/test/security |
| `.github/workflows/` | CI: test, lint, scan, build, release-on-tag |

Do not confuse `app.py` and `main.py`: Docker and local runs start **`src/app.py`**; the ASGI app lives in **`src/main.py`**.

## Runtime Flow

1. `src/app.py` starts Uvicorn with `main:app`, host/port/workers from environment.
2. Importing `main` triggers side effects in `src/main.py`:
   - `Base.metadata.create_all(bind=dbEngine)` — creates tables if missing
   - `redis.init()` — global Redis client
   - FastAPI app construction and router registration
3. `constants/environment_variables.py` validates required env vars **at import time** (raises `RuntimeError` if missing).
4. Routes delegate to controllers; controllers use `get_db()` sessions.
5. Protected routes use JWT dependencies in `middleware/auth_guard.py`.

**Implication:** importing the app is not side-effect free. PostgreSQL and Redis must be reachable for a normal boot. Prefer Docker Compose for full-stack validation.

## API Surface

Mounted under `/{API_VERSION}` (default `v1`):

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| `GET` | `/health` | — | `{"alive": true, "status": "ok"}` |
| `POST` | `/token` | — | OAuth2 password grant; `username` = email **or** username |
| `POST` | `/user/register` | — | Email/password registration |
| `POST` | `/user/login` | — | JSON login; returns user + nested `token` object |
| `GET` | `/user` | Bearer | Current user |
| `PATCH` | `/user` | Bearer | Update current user |
| `GET` | `/oidc/google/login` | — | Google authorization URL |
| `GET` | `/oidc/google` | — | OAuth `code` or `credential` → JWT |
| `GET` | `/oidc/google/token` | — | Decode provided JWT |
| `GET` | `/admin/user/all` | Admin | List users (passwords stripped) |
| `GET` | `/admin/user/{user_id}` | Admin | Single user |
| `POST` | `/admin/user/register` | Admin | Create user |
| `PATCH` | `/admin/user/{user_id}` | Admin | Update user |
| `DELETE` | `/admin/user/{user_id}` | Admin | Delete user (204) |

Swagger UI is at `/` (`docs_url="/"`).

## Data Model

Single application model: `User` (`public.user` table).

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | PK, `uuid_generate_v4()` |
| `username` | string | optional |
| `email` | string | unique |
| `password` | string | nullable (OIDC-only users) |
| `is_admin` | bool | |
| `disabled` | bool | |
| `oidc_configs` | JSONB | provider mappings array |

Google OIDC users are created with `password=None`.

## Flyway Migrations

Flat layout in `src/migrations/` (not versioned subfolders):

| File | Purpose |
|------|---------|
| `V1__init_db.sql` | `uuid-ossp` extension |
| `V2__create_user_table.sql` | `user` table |
| `V3__seed_admin_user.sql` | Dev admin `test@admin.com` / `Cloud.456` (sha256_crypt hash) |

`flyway.conf` sets `validateOnMigrate=true`, `outOfOrder=false`. Compose service `mercury_migrate` runs before `mercury_api`.

**Migration rename (since v0.3.1):** old paths like `V1/V1.1__*` were flattened to `V1__`, `V2__`, `V3__`. Existing DBs that already ran old Flyway versions need a manual Flyway/history plan before upgrading — do not assume a clean rename on production data.

## Auth Model

Two login paths:

- **`POST /token`**: OAuth2 form; `username` accepts email or username; returns `{ access_token, token_type }`; failures → **401**
- **`POST /user/login`**: JSON email + password; returns `{ id, email, token: { ... } }`; failures → **404** (via `authenticate_user`)

JWT payload uses `sub` = user **email**. User resolution always re-queries by email.

Dependencies:

- `get_current_user` — valid JWT + user exists
- `get_current_active_user` — not `disabled` (400 if inactive)
- `get_current_admin_user` — `is_admin` (400 if not admin); **does not** check `disabled`

Default seeded admin (README): `test@admin.com` / `Cloud.456`.

## Environment Model

Required at import (`validate_required_env()`):

`LISTEN_ADDR`, `LISTEN_PORT`, `APP_VERSION`, `APP_TITLE`, `APP_DESCRIPTION`, `API_VERSION`, `POSTGRES_*` (db, user, password, port, host), `JWT_SECRET_KEY`, `JWT_ALGORITHM`.

Commonly set but not validated as required:

`APP_ENV`, `API_URL`, `REDIS_HOST`, `REDIS_PORT`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `HTTP_REQUEST_TIMEOUT`, Google OIDC vars.

`OIDC_GOOGLE_REDIRECT_URI` is derived: `{API_URL}/{API_VERSION}/oidc/google`.

Baseline: copy `.env.dist` → `.env`. Docker Compose loads `.env` for all services.

Pool tuning (optional): `POSTGRES_SIZE_POOL`, `POSTGRES_MAX_OVERFLOW`, `POSTGRES_POOL_TIMEOUT`, `POSTGRES_POOL_RECYCLE` (defaults in `postgres_db.py`).

Uvicorn tuning (optional): `UVICORN_WORKERS`, `UVICORN_TIMEOUT_KEEP_ALIVE`, `UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN`.

## Docker and CI

Compose services:

| Service | Role |
|---------|------|
| `mercury_api` | API (non-root `app` user, healthcheck on `/v1/health`) |
| `mercury_db` | PostgreSQL 16 |
| `mercury_cache` | Redis 7 |
| `mercury_migrate` | Flyway (`FLYWAYDB_VERSION` default `10-alpine`) |
| `mercury_integration_tests` | `pytest -v` |
| `mercury_unit_tests` | `unittest discover` |
| `mercury_linter` | `ruff check` |
| `mercury_security` | `bandit` |

Commands:

```bash
docker compose up --build --force-recreate          # full stack
./ci/unit-test.sh
./ci/integration-test.sh
./ci/lint.sh
./ci/security.sh
```

GitHub Actions (`main` / `develop` / PRs):

- **test.yml** — unit + integration via `ci/*.sh`
- **lint.yml** — Ruff
- **scan.yml** — Bandit
- **build.yml** — Docker image on `main`
- **release.yml** — GitHub Release on push of tag matching `v*`

Renovate (`renovate.json`) groups pip minor/patch with automerge; majors and core frameworks (FastAPI, SQLAlchemy, Pydantic) need manual review.

## Test Reality

Coverage is shallow but integration tests improved since v0.3.1:

- **Unit:** single health test (`routes.health`); runs from `src/` in Docker.
- **Integration:** health + admin CRUD flow; `admin_headers` fixture logs in via `/token`; `_ensure_admin_user_exists()` makes tests resilient if seed migration order differs.
- Tests import the real app (`main:app`) — need DB, Redis, migrations, and full `.env`.

Local non-Docker runs need `PYTHONPATH=src` and installed deps from `requirements.txt`.

## Release History (Mercury)

Mercury is the original FastAPI boilerplate in the Solar Stack. Mars is the Alembic variant forked from this repo.

- **Flyway** flat SQL migrations in `src/migrations/` (`V1__`, `V2__`, …)
- Compose service `mercury_migrate` runs Flyway before `mercury_api`
- **`solar.manifest.yaml`** at repo root for [sun](https://github.com/ayoub3bidi/sun) scaffolds

## Architectural Strengths

- Small, traceable codebase with consistent route → controller layout.
- Explicit Flyway SQL migrations; readable seed for local dev.
- Full Docker dev loop (migrate → api → tests).
- Auth, admin, and OIDC scaffolding ready to extend.
- CI covers test, lint, security, build, and tag releases.
- SQLAlchemy 2 + Pydantic v2 align with current ecosystem defaults.

## Main Risks and Sharp Edges

1. **Startup side effects** — `create_all()` + Redis init on `main` import complicates testing and duplicates Flyway.
2. **Dual schema management** — Flyway is source of truth for production; `create_all()` can drift or mask migration gaps.
3. **Inconsistent auth responses** — `/token` (401) vs `/user/login` (404); different response shapes.
4. **Admin GET by id** — `remove_password_from_user(user)` when `user is None` → **500** instead of 404.
5. **Password scheme tied to JWT algorithm** — `sha256_crypt` iff `HS256`; should be independent config.
6. **Admin auth** — `get_current_admin_user` does not enforce `disabled`.
7. **Redis** — connected but unused in business logic (bootstrap only).
8. **Response filters** — `utils/filter.py` mutates ORM `__dict__` in place; risky if objects are reused.
9. **Flyway migration rename** — upgrading from pre-v0.3.2 Flyway history may need `flyway repair` / baseline strategy.
10. **Seeded admin** — fine for dev; must be removed/changed in production.

## Recommendations For Future Agents

- Prefer **Docker Compose** for anything that imports `src/main.py`.
- Treat **Flyway SQL** as the schema source of truth; consider removing `create_all()` in a follow-up.
- Preserve route/controller/module layout.
- Keep JWT `sub=email` unless refactoring all auth paths together.
- Add tests for auth failures, OIDC edge cases, and admin 404 paths — current coverage will not catch regressions.
- When adding migrations, use next `V{n}__description.sql` in `src/migrations/`.
- Inspect git state before large edits; `main` may be ahead of latest tag.

## Suggested Improvement Order

1. Remove `create_all()` from startup; rely on Flyway only.
2. Normalize auth status codes and response shapes across `/token` and `/user/login`.
3. Guard `GET /admin/user/{id}` for missing users (404 before filter).
4. Decouple password hashing from `JWT_ALGORITHM`.
5. Enforce `disabled` on admin dependencies (or document intentional bypass).
6. Use Redis for sessions/rate-limit/cache when extending the boilerplate.
7. Expand integration tests (user login, register, negative auth, OIDC mocks).

## Local Validation (analysis run)

Succeeded:

- Source inventory and architecture review
- `python3 -m compileall -q src`
- `python3 -m ruff check src` — all checks passed

Not run in this shell (use Docker instead):

- Unit/integration tests (need Compose stack and `.env`)
- Bandit security scan

## Release Tagging

Tags in this repo use a **`v` prefix** (`v0.4.0`, not `0.4.0`). Pushing `v*` triggers `.github/workflows/release.yml` to create a GitHub Release with generated notes.
