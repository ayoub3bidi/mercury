import os

import pytest

from init_test import client

headers = {"Authorization": "Bearer your_token_here"}
v = os.getenv("API_VERSION", "v1")

# ID of user created in test_add_user; used by test_get_user_by_id and test_delete_user
_created_user_id = None


def test_get_users():
    if client is None:
        pytest.skip("Client not initialized")

    response = client.get(f"/{v}/admin/user/all", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_add_user():
    if client is None:
        pytest.skip("Client not initialized")

    global _created_user_id
    response = client.post(
        f"/{v}/admin/user/register",
        json={
            "username": "test_user",
            "email": "test_user_integration@gmail.com",
            "password": "GoodPassword123",
            "is_admin": True,
            "disabled": False,
        },
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data.get("email") == "test_user_integration@gmail.com"
    _created_user_id = str(data["id"])


def test_get_user_by_id():
    if client is None:
        pytest.skip("Client not initialized")
    if _created_user_id is None:
        pytest.skip("No user id from test_add_user")

    response = client.get(f"/{v}/admin/user/{_created_user_id}", headers=headers)
    assert response.status_code == 200
    assert response.json().get("id") == _created_user_id or response.json().get("email") == "test_user_integration@gmail.com"


def test_delete_user():
    if client is None:
        pytest.skip("Client not initialized")
    if _created_user_id is None:
        pytest.skip("No user id from test_add_user")

    response = client.delete(f"/{v}/admin/user/{_created_user_id}", headers=headers)
    assert response.status_code == 204
