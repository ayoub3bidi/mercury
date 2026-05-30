# Contributing to Mercury

Thank you for your interest in contributing. This document covers the basics;
for day-to-day development, see the [README](README.md).

## Getting started

1. Fork the repository and clone your fork.
2. Copy environment config: `cp .env.dist .env`
3. Start the stack: `docker compose up --build`
4. Run checks before opening a PR (see below).

## Development workflow

1. Create a branch from `main` with a clear name (e.g. `feat/my-feature`, `fix/login-error`).
2. Make focused changes; keep PRs small when possible.
3. Add or update integration tests under `src/integration_tests/` for API behavior changes.
4. Run Flyway migrations for schema changes (`src/migrations/V{n}__description.sql`).
5. Follow the [How to add a new endpoint](README.md#how-to-add-a-new-endpoint) checklist in the README.

## Checks to run locally

```shell
# Linter
docker compose up --build --abort-on-container-exit mercury_linter

# Integration tests
docker compose up --build --abort-on-container-exit mercury_integration_tests

# Unit tests
docker compose up --build --abort-on-container-exit mercury_unit_tests
```

Optional: install [pre-commit](README.md#pre-commit) hooks for Ruff.

## Pull requests

- Use the [pull request template](.github/pull_request_template.md).
- Link related issues when applicable.
- Ensure CI is green before requesting review.
- Describe **what** changed and **why**.

## Reporting bugs and requesting features

Use the GitHub issue templates:

- [Bug report](.github/ISSUE_TEMPLATE/bug_report.md)
- [Feature request](.github/ISSUE_TEMPLATE/feature_request.md)

## Security issues

Do **not** open public issues for security vulnerabilities. See [SECURITY.md](SECURITY.md).

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Please be respectful and constructive.
