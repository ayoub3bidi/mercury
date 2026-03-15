"""Pytest fixtures for integration tests. Ensures the FastAPI app and TestClient are initialized."""
import os
import sys
from pathlib import Path

# Add parent (src) to path so "main" can be imported when running from integration_tests/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set required env vars before importing main (which validates them)
os.environ.setdefault("LISTEN_ADDR", "0.0.0.0")  # nosec B104 - test env only, not production bind
os.environ.setdefault("LISTEN_PORT", "8000")
os.environ.setdefault("APP_VERSION", "1.0")
os.environ.setdefault("APP_TITLE", "Mercury")
os.environ.setdefault("APP_DESCRIPTION", "Mercury API")
os.environ.setdefault("API_VERSION", "v1")
os.environ.setdefault("POSTGRES_DB", "mercury")
os.environ.setdefault("POSTGRES_USER", "mercury")
os.environ.setdefault("POSTGRES_PASSWORD", "mercury")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

import init_test


def pytest_configure(config):
    """Initialize the TestClient with the FastAPI app before any tests run."""
    import main

    init_test.init(main.app)
