from fastapi.testclient import TestClient

client = None

def init(app):
    global client
    client = TestClient(app)