import os
from init_test import client

headers = {"Authorization": "Bearer your_token_here"}
v = os.getenv("VERSION")

def test_get_users():
    if (client != None):
        response = client.get(f"/{v}/admin/user/all", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) > 0
        
def test_get_user_by_id():
    if (client != None):
        response = client.get(f"/{v}/admin/user/1", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == 1

def test_add_user():
    if (client != None):
        response = client.post(f"/{v}/admin/user/register", json={"username": "test_user", "email": "test_user@gmail.com", "password": "GoodPassword123", "is_admin": True, "disabled": False }, headers=headers)
        assert response.status_code == 201
        assert response.json()["username"] == "test_user"

def test_delete_user():
    if (client != None):
        response = client.delete(f"/{v}/admin/user/1", headers=headers)
        assert response.text == None