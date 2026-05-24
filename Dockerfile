ARG PYTHON_VERSION=3.12-slim-bookworm
ARG FLYWAYDB_VERSION=10-alpine

# Base image
FROM python:${PYTHON_VERSION} AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production API
FROM base AS api

ENV LISTEN_ADDR="0.0.0.0" \
    LISTEN_PORT=8000 \
    UVICORN_WORKERS=4 \
    UVICORN_TIMEOUT_KEEP_ALIVE=65 \
    UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN=30

RUN addgroup --system app && adduser --system --ingroup app app
COPY --chown=app:app . .
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/v1/health')"

CMD ["python", "src/app.py"]

# Integration tests
FROM base AS integration_tests
COPY . .
WORKDIR /app/src/integration_tests

CMD ["pytest", "-v"]

# Unit tests
FROM base AS unit_tests
COPY . .
WORKDIR /app/src

CMD ["python", "-m", "unittest", "discover", "-s", "./unit_tests", "-p", "test_*.py", "-v"]

# Lint
FROM base AS linter
COPY . .
WORKDIR /app/src

CMD ["ruff", "check", "."]

# Scan
FROM base AS code_scanner
RUN pip install --no-cache-dir bandit
COPY . .

WORKDIR /app/src
CMD ["bandit", "-r", ".", "-f", "screen", "-s", "B101,B105"]
