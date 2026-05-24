# Mercury Agent Guide

## Purpose

Mercury is a small FastAPI backend boilerplate centered on JWT auth, PostgreSQL persistence, Redis initialization, and optional Google OIDC login. The project is intentionally simple: routes call thin controllers, controllers talk directly to SQLAlchemy sessions, and Flyway SQL files own the database schema.

This file is a working analysis for future agents so they can navigate the repository quickly and avoid common mistakes.

## Stack Summary

- API framework: FastAPI
- App server: Uvicorn
- Database: PostgreSQL via SQLAlchemy 1.4
- Cache/bootstrap dependency: Redis
- Auth: JWT + OAuth2 password flow, plus Google OIDC
- Migrations: Flyway SQL files
- Tests: `unittest` for a trivial unit test, `pytest` for integration tests
- Tooling: Docker Compose, Ruff, Bandit, GitHub Actions

## Repository Shape

Top-level areas:

- `src/main.py`: Uvicorn entrypoint
- `src/app.py`: FastAPI app construction, DB metadata creation, Redis init, router registration
- `src/restful_ressources.py`: central router mounting
- `src/routes/`: HTTP route definitions
- `src/controllers/`: request logic and DB mutation/query logic
- `src/models/`: SQLAlchemy model definitions
- `src/schemas/`: Pydantic request/response schemas
- `src/database/`: PostgreSQL engine/session and Redis bootstrap
- `src/middleware/auth_guard.py`: JWT decoding and auth dependencies
- `src/utils/`: password hashing, JWT creation, OIDC helpers, response filtering, env parsing
- `src/migrations/`: Flyway SQL migrations
- `src/integration_tests/`: API-level tests using `TestClient`
- `src/unit_tests/`: very small direct-function test coverage
- `ci/` and `.github/workflows/`: local and CI automation wrappers

## Runtime Flow

1. `src/main.py` starts Uvicorn with host/port/worker values from environment variables.
2. Uvicorn imports `main:app`, which comes from `src/app.py`.
3. `src/app.py` does three things at import time:
   - creates SQLAlchemy tables with `Base.metadata.create_all(bind=dbEngine)`
   - initializes the Redis client
   - builds the FastAPI app and mounts routers
4. Routes delegate into controllers.
5. Controllers use `Session` instances from `database.postgres_db.get_db`.
6. Protected routes use JWT decoding in `middleware/auth_guard.py`.

Important implication: importing the app is not cheap or side-effect free. It expects environment variables to exist and, in normal operation, assumes PostgreSQL and Redis are reachable.

## API Surface

Mounted under `/{API_VERSION}`:

- `GET /health`: basic health response
- `POST /token`: OAuth2 password grant endpoint returning `access_token`
- `POST /user/register`: create normal user
- `POST /user/login`: email/password login returning user payload + nested token object
- `GET /user`: current authenticated user
- `PATCH /user`: update current authenticated user
- `GET /oidc/google/login`: returns Google authorization URL
- `GET /oidc/google`: handles Google `code` or `credential`, creates/links user, returns JWT
- `GET /oidc/google/token`: decodes a provided JWT
- `GET /admin/user/all`: list all users
- `GET /admin/user/{user_id}`: fetch one user
- `POST /admin/user/register`: create user as admin
- `PATCH /admin/user/{user_id}`: update user as admin
- `DELETE /admin/user/{user_id}`: delete user

## Data Model

There is one application model: `User`.

Fields:

- `id`: UUID primary key
- `username`: optional string
- `email`: unique string
- `password`: nullable string
- `is_admin`: boolean
- `disabled`: boolean
- `oidc_configs`: JSONB array storing provider mappings

Google OIDC users can be created with `password=None`.

## Auth Model

There are two login paths:

- `/token`: OAuth2-compatible login using `username` form field, but it accepts either username or email
- `/user/login`: JSON login using email only

JWTs store the user email in `sub`. Current-user resolution always re-queries by email.

Role enforcement:

- `get_current_active_user` blocks disabled users
- `get_current_admin_user` checks `is_admin`, but does not also enforce `disabled`

## Environment Model

The settings module validates several required variables at import time. At minimum, local execution needs values for:

- `LISTEN_ADDR`
- `LISTEN_PORT`
- `APP_VERSION`
- `APP_TITLE`
- `APP_DESCRIPTION`
- `API_VERSION`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_PORT`
- `POSTGRES_HOST`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`

Additional variables used by optional paths:

- `REDIS_HOST`, `REDIS_PORT`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `API_URL`
- `HTTP_REQUEST_TIMEOUT`
- Google OIDC client and endpoint values

Use `.env.dist` as the baseline. Normal project usage assumes `.env` plus `docker compose`.

## Docker and CI

Primary services in `docker-compose.yml`:

- `mercury_api`
- `mercury_db`
- `mercury_cache`
- `mercury_migrate`
- `mercury_integration_tests`
- `mercury_unit_tests`
- `mercury_linter`
- `mercury_security`

Normal commands:

- Run app: `docker compose up --build --force-recreate`
- Unit tests: `./ci/unit-test.sh`
- Integration tests: `./ci/integration-test.sh`
- Lint: `./ci/lint.sh`
- Security scan: `./ci/security.sh`

GitHub Actions cover:

- unit + integration tests
- lint
- security scan
- Docker image build on `main`
- release creation on pushed `v*` tags

## Test Reality

Current test coverage is shallow.

- Unit coverage is a single health test that imports `routes.health` directly.
- Integration coverage exercises health plus part of the admin user flow.
- Integration tests are not hermetic; they depend on app import, environment bootstrap, and database access.

Practical note: local non-Docker test execution is brittle. From the repository root, the unit test needs `PYTHONPATH=src`, and the local machine must already have the Python dependencies installed.

## Architectural Strengths

- The project is small and easy to trace end-to-end.
- Route/controller separation is consistent.
- SQL migrations are explicit and readable.
- Docker Compose provides a straightforward full-stack dev loop.
- Auth, admin routes, and OIDC are already scaffolded for extension.

## Main Risks and Sharp Edges

1. Startup side effects are heavy.
   `src/app.py` creates DB tables and initializes Redis during import. This makes testing and partial module reuse harder.

2. Two schema-management approaches coexist.
   SQLAlchemy `create_all()` runs at startup even though Flyway migrations are the intended schema source. Those can drift.

3. Auth behavior is inconsistent.
   `/token` accepts username or email, while `/user/login` accepts email only and returns a different token shape.

4. Error handling is uneven.
   Some auth failures return `401`, others return `404`; that leaks distinction between missing user and bad password.

5. Some route paths can raise server errors instead of clean API errors.
   Admin get-by-id sanitizes the returned object without guarding for `None`, so a missing user can become a `500`.

6. Password hashing is coupled to JWT algorithm selection.
   `utils/security.py` chooses `sha256_crypt` when `JWT_ALGORITHM == "HS256"` and `bcrypt` otherwise. Those concerns should be independent.

7. Environment validation is partial.
   Some values are required early, but others used at runtime are optional in validation, so misconfiguration can slip through.

8. Redis is initialized but not meaningfully integrated in request logic.
   At the moment it is mostly bootstrap overhead.

9. Test execution assumptions are under-documented.
   Local direct execution currently fails without path setup and installed dependencies.

## Recommendations For Future Agents

- Prefer Docker Compose for any validation that imports `src/app.py`.
- Assume Flyway migrations, not SQLAlchemy metadata creation, are the source of truth for production schema changes.
- Preserve the route/controller/module layout; the codebase is organized around that shape.
- When adding auth-sensitive features, keep JWT payload semantics aligned with `sub=email` unless you refactor all dependent code.
- Add tests whenever changing auth, admin routes, or OIDC, because the current coverage will not catch much.
- Be careful with response filtering helpers in `utils/filter.py`; they mutate ORM `__dict__` views directly.
- Do not assume the repo is in a clean git state before working; inspect changes first.

## Local Validation Performed For This Analysis

What succeeded:

- source inventory and architecture review
- static syntax compilation via `python3 -m compileall src`
- Ruff check via `python3 -m ruff check src`

What did not fully run in the current shell:

- `python3 -m unittest discover -s src/unit_tests -p 'test_*.py' -v` failed from repo root because the test assumes `PYTHONPATH=src`
- `PYTHONPATH=src python3 -m unittest ...` then failed because local dependencies like `fastapi` are not installed in this shell
- `pytest` is not installed in this shell, so integration tests were not run outside Docker

## Suggested Improvement Order

1. Remove `create_all()` from startup and rely on Flyway only.
2. Normalize auth responses and status codes across `/token` and `/user/login`.
3. Fix `None` handling and response shaping for admin/user fetch endpoints.
4. Decouple password hashing configuration from JWT algorithm choice.
5. Strengthen tests so they can run locally and cover negative auth/admin cases.
