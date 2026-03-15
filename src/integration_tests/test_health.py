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
