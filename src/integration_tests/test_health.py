import pytest
import os
from init_test import client

v = os.getenv("VERSION")

def test_get_health():
    if client is None:
        pytest.skip("Client not initialized")
        
    response = client.get(f"/{v}/health")
    pytest.expect(response.status_code == 200)
    pytest.expect(response.json() == {
        'status': 'ok',
        'alive': True
    })
