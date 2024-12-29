import pytest
import os
from init_test import client

headers = {"Authorization": "Bearer your_token_here"}
v = os.getenv("VERSION")

def test_get_users():
    if client is None:
        pytest.skip("Client not initialized")
        
    response = client.get(f"/{v}/admin/user/all", headers=headers)
    pytest.expect(response.status_code == 200)
    pytest.expect(len(response.json()) > 0)
        
def test_get_user_by_id():
    if client is None:
        pytest.skip("Client not initialized")
        
    response = client.get(f"/{v}/admin/user/1", headers=headers)
    pytest.expect(response.status_code == 200)
    pytest.expect(response.json()["id"] == 1)

def test_add_user():
    if client is None:
        pytest.skip("Client not initialized")
        
    response = client.post(
        f"/{v}/admin/user/register",
        json={
            "username": "test_user",
            "email": "test_user@gmail.com",
            "password": "GoodPassword123",
            "is_admin": True,
            "disabled": False
        },
        headers=headers
    )
    pytest.expect(response.status_code == 201)
    pytest.expect(response.json()["username"] == "test_user")

def test_delete_user():
    if client is None:
        pytest.skip("Client not initialized")
        
    response = client.delete(f"/{v}/admin/user/1", headers=headers)
    pytest.expect(response.text is None)
