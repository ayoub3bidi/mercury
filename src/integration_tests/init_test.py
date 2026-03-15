from fastapi.testclient import TestClient

client = None


def init(app):
    """Create a sync test client for the FastAPI app. Requires httpx<0.28 for Starlette TestClient compatibility."""
    global client
    client = TestClient(app)