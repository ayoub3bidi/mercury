ARG PYTHON_IMAGE=python:3.12.16-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df

FROM ${PYTHON_IMAGE} AS builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /build
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM ${PYTHON_IMAGE} AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    LISTEN_ADDR=0.0.0.0 \
    LISTEN_PORT=8000 \
    UVICORN_WORKERS=4 \
    UVICORN_TIMEOUT_KEEP_ALIVE=65 \
    UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN=30
WORKDIR /app
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels && \
    addgroup --system app && adduser --system --ingroup app app
COPY --chown=app:app . .
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/v1/health/live', timeout=3)"

FROM runtime AS api
CMD ["python", "src/app.py"]

FROM runtime AS worker
CMD ["celery", "--workdir", "/app/src", "-A", "worker.celery_app:celery_app", "worker", "--loglevel", "INFO"]

FROM runtime AS integration_tests
USER root
WORKDIR /app/src/integration_tests
USER app
CMD ["pytest", "-v"]

FROM runtime AS unit_tests
WORKDIR /app/src
CMD ["pytest", "-v", "unit_tests"]

FROM runtime AS linter
WORKDIR /app/src
CMD ["ruff", "check", "."]

FROM runtime AS code_scanner
USER root
RUN pip install --no-cache-dir bandit==1.8.6
WORKDIR /app/src
USER app
CMD ["bandit", "-r", ".", "-f", "screen", "-s", "B101,B105"]
