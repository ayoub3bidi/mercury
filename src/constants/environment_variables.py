import os


def _require(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def validate_required_env() -> None:
    """Validate that all required environment variables are set. Call at startup."""
    required = [
        "LISTEN_ADDR",
        "LISTEN_PORT",
        "APP_VERSION",
        "APP_TITLE",
        "APP_DESCRIPTION",
        "API_VERSION",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_PORT",
        "POSTGRES_HOST",
        "JWT_SECRET_KEY",
        "JWT_ALGORITHM",
    ]
    for name in required:
        _require(name)


validate_required_env()

LISTEN_ADDR = os.environ["LISTEN_ADDR"]
LISTEN_PORT = os.environ["LISTEN_PORT"]
APP_VERSION = os.environ["APP_VERSION"]
APP_TITLE = os.environ["APP_TITLE"]
APP_DESCRIPTION = os.environ["APP_DESCRIPTION"]
v = os.environ["API_VERSION"]
APP_ENV = os.getenv("APP_ENV")
API_URL = os.getenv("API_URL")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
HTTP_REQUEST_TIMEOUT = os.getenv("HTTP_REQUEST_TIMEOUT")
GOOGLE_AUTH_URL = os.getenv("GOOGLE_AUTH_URL")
GOOGLE_TOKEN_URL = os.getenv("GOOGLE_TOKEN_URL")
GOOGLE_USER_INFO_URL = os.getenv("GOOGLE_USER_INFO_URL")
OIDC_GOOGLE_CLIENT_ID = os.getenv("OIDC_GOOGLE_CLIENT_ID")
OIDC_GOOGLE_CLIENT_SECRET = os.getenv("OIDC_GOOGLE_CLIENT_SECRET")
OIDC_GOOGLE_REDIRECT_URI = f"{API_URL}/{v}/oidc/google"