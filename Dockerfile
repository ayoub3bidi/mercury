ARG PYTHON_VERSION=3.9.16
ARG FLYWAYDB_VERSION=9.20-alpine

# Base image
FROM python:${PYTHON_VERSION} as api

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    LISTEN_ADDR="0.0.0.0" \
    LISTEN_PORT=5000 \
    UVICORN_WORKERS=10 \
    UVICORN_TIMEOUT_KEEP_ALIVE=65 \
    UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN=30

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN find . -name '*.pyc' -type f -delete && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf *.tgz && \
    apt clean -y

COPY . /app/

EXPOSE 5000

CMD ["python", "src/app.py"]

# Integration tests
FROM api AS integration_tests

WORKDIR /app/src/integration_tests

CMD ["pytest"]

# Unit tests
FROM api AS unit_tests

WORKDIR /app/src

CMD ["python", "-m", "unittest", "discover", "-s", "./unit_tests", "-p", "test_*.py", "-v"]

# Lint
FROM api AS linter

WORKDIR /app/src

CMD ["ruff", "check", "--fix", "."]

# Scan
FROM api AS code_scanner

WORKDIR /app/src

RUN pip install bandit

CMD ["bandit", "-r", ".", "-f", "screen"]
