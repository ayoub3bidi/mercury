import contextvars
import json
import logging
import time
import uuid
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "request_id": request_id_var.get(),
            },
            ensure_ascii=False,
        )


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        try:
            if settings_otel_enabled():
                from opentelemetry import trace

                tracer = trace.get_tracer("mercury.http")
                with tracer.start_as_current_span("http.request") as span:
                    span.set_attribute("http.request.method", request.method)
                    span.set_attribute("url.path", request.url.path)
                    span.set_attribute("mercury.request_id", request_id)
                    response = await call_next(request)
                    span.set_attribute("http.response.status_code", response.status_code)
            else:
                response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            logging.getLogger("mercury.request").info(
                "request_complete method=%s path=%s status=%s duration_ms=%.2f",
                request.method,
                request.url.path,
                response.status_code,
                (time.perf_counter() - started) * 1000,
            )
            return response
        finally:
            request_id_var.reset(token)


def settings_otel_enabled() -> bool:
    from constants.settings import settings

    return settings.OTEL_ENABLED
