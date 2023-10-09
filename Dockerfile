ARG PYTHON_VERSION=3.9.16

FROM python:${PYTHON_VERSION} as api

ENV WERKZEUNG_RUN_MAIN=true \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    LISTEN_ADDR="0.0.0.0" \
    LISTEN_PORT=8000

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN find . -name '*.pyc' -type f -delete && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["python", "src/app.py"]

FROM api AS integration_tests

WORKDIR /app/src/integration_tests

CMD ["pytest"]

FROM api AS unit_tests

WORKDIR /app/src

CMD ["python", "-m", "unittest", "discover", "-s", "./unit_tests", "-p", "test_*.py", "-v"]