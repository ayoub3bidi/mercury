import logging

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from database.postgres_db import SessionLocal
from database.redis_db import redis_connect

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
def get_health():
    return {"status": "ok", "alive": True}


@router.get("/health/live")
def get_liveness():
    return {"status": "ok", "alive": True}


@router.get("/health/ready")
def get_readiness(response: Response):
    checks = {"postgres": False, "redis": False}
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        checks["postgres"] = True
    except Exception as exc:
        logger.warning("readiness check failed dependency=postgres error_type=%s", type(exc).__name__)
    try:
        checks["redis"] = bool(redis_connect.ping())
    except Exception as exc:
        logger.warning("readiness check failed dependency=redis error_type=%s", type(exc).__name__)

    ready = all(checks.values())
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "ok" if ready else "not_ready", "ready": ready, "checks": checks}
