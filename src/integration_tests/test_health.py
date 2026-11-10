import os

import pytest

from init_test import client

v = os.getenv("API_VERSION", "v1")


def test_get_health():
    if client is None:
        pytest.skip("Client not initialized")

    response = client.get(f"/{v}/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "alive": True,
    }


def test_live_endpoint_and_legacy_alias():
    if client is None:
        pytest.skip("Client not initialized")

    live = client.get(f"/{v}/health/live")
    legacy = client.get(f"/{v}/health")

    assert live.status_code == 200
    assert legacy.status_code == 200
    assert live.json() == legacy.json()
    assert live.headers["x-request-id"]


def test_readiness_checks_dependencies():
    if client is None:
        pytest.skip("Client not initialized")

    response = client.get(f"/{v}/health/ready")

    assert response.status_code == 200
    assert response.json()["ready"] is True
    assert response.json()["checks"] == {"postgres": True, "redis": True}
