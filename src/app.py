import uvicorn

from constants.settings import settings
from utils.common import get_env_int

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.LISTEN_ADDR,
        port=get_env_int("LISTEN_PORT", settings.LISTEN_PORT),
        workers=get_env_int("UVICORN_WORKERS", 4),
        timeout_keep_alive=get_env_int("UVICORN_TIMEOUT_KEEP_ALIVE", 30),
        timeout_graceful_shutdown=get_env_int("UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN", 10),
    )
