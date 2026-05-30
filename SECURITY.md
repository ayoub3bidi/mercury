# Security Policy

## Supported versions

Security fixes are applied to the latest release on the `main` branch. Older tags may not receive patches unless noted in a release.

## Reporting a vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, use one of the following:

1. **GitHub Security Advisories** — open a [private vulnerability report](https://github.com/ayoub3bidi/mercury/security/advisories/new) on this repository (preferred).
2. **Maintainer contact** — reach the repository owner via GitHub profile contact options if advisories are unavailable.

Include:

- A description of the issue and impact
- Steps to reproduce
- Affected versions or commits (if known)
- Any suggested fix (optional)

We aim to acknowledge reports within a few business days and will coordinate disclosure after a fix is available.

## Production deployment

When `APP_ENV=production`, Mercury blocks startup if weak default secrets are detected (`JWT_SECRET_KEY`, `POSTGRES_PASSWORD`). See `src/utils/production_checks.py`.

Before going to production:

- Use strong, unique secrets (JWT at least 32 characters).
- Remove or disable the seeded admin user (`test@admin.com`).
- Restrict CORS and `ALLOWED_HOSTS` to your real domains.
- Keep dependencies updated and run `mercury_security` (Bandit) in CI.

## Safe harbor

We appreciate responsible disclosure and will not pursue legal action against researchers who follow this policy in good faith.
