import os

import pytest

from database.postgres_db import SessionLocal
from init_test import client
from models.User import User
from utils.security import get_password_hash

v = os.getenv("API_VERSION", "v1")

# Test admin credentials (same as README / V1.3 seed); used only in tests
ADMIN_EMAIL = "test@admin.com"
ADMIN_PASSWORD = "Cloud.456"  # nosec B105

# ID of user created in test_add_user; used by test_get_user_by_id and test_delete_user
_created_user_id = None


def _ensure_admin_user_exists():
    """Create the test admin user if missing (self-contained tests; does not rely on migration order)."""
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == ADMIN_EMAIL).first() is not None:
            return
        user = User(
            username="admin",
            email=ADMIN_EMAIL,
            password=get_password_hash(ADMIN_PASSWORD),
            is_admin=True,
        )
        db.add(user)
        db.commit()
    finally:
        db.close()


@pytest.fixture(scope="module")
def admin_headers():
    """Obtain a JWT for the admin user and return headers for admin routes."""
    if client is None:
        pytest.skip("Client not initialized")
    _ensure_admin_user_exists()
    response = client.post(
        f"/{v}/token",
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_users(admin_headers):
    if client is None:
        pytest.skip("Client not initialized")

    response = client.get(f"/{v}/admin/user/all", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_add_user(admin_headers):
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
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data.get("email") == "test_user_integration@gmail.com"
    _created_user_id = str(data["id"])


def test_get_user_by_id(admin_headers):
    if client is None:
        pytest.skip("Client not initialized")
    if _created_user_id is None:
        pytest.skip("No user id from test_add_user")

    response = client.get(f"/{v}/admin/user/{_created_user_id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json().get("id") == _created_user_id or response.json().get("email") == "test_user_integration@gmail.com"


def test_delete_user(admin_headers):
    if client is None:
        pytest.skip("Client not initialized")
    if _created_user_id is None:
        pytest.skip("No user id from test_add_user")

    response = client.delete(f"/{v}/admin/user/{_created_user_id}", headers=admin_headers)
    assert response.status_code == 204
