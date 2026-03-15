import httpx

client = None


def init(app):
    """Create an HTTP client that talks to the ASGI app (works with httpx 0.24+ including 0.28+)."""
    global client
    transport = httpx.ASGITransport(app=app)
    client = httpx.Client(transport=transport, base_url="http://testserver")