# Changelog

All notable changes to Mercury are documented here.

## [v0.4.2] - 2026-11-11

### Added

- Optional asynchronous agent runs through `POST /v1/runs` and `GET /v1/runs/{id}`, with idempotency keys, configurable token budgets, and a local mock LLM for development.
- An opt-in Celery worker and agent service profile, plus request IDs, structured request logging, Prometheus metrics, and optional OpenTelemetry tracing.
- Liveness and readiness health endpoints for deployment checks.

### Changed

- Added the `runs` table with Flyway migration V5. Migration V4 removes only the unchanged seeded admin account.
- Production checks now reject unsafe default credentials while retaining a local-only development seed account.
- Updated FastAPI, ASN.1-related dependencies, and CI image scanning configuration.
- Run endpoints reject zero and over-limit token budgets, including an explicitly supplied zero. Image publication now waits for quality and security checks to pass.

### Fixed

- Aligned Prometheus instrumentation with FastAPI so runtime metrics are collected consistently.
