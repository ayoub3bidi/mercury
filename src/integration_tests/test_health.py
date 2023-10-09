import os
from init_test import client

v = os.getenv("VERSION")

def test_get_health():
    if (client != None):
        response = client.get(f"/{v}/health")
        assert response.status_code == 200
        assert response.json() == { 'status': 'ok', 'alive': True }