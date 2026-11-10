from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from constants.settings import settings
import database.redis_db as redis
from database.postgres_db import SessionLocal, dbEngine
from middleware.request_context import RequestIdMiddleware, configure_logging
from restful_ressources import import_resources
from utils.production_checks import validate_production_settings, warn_if_seed_admin_present


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    validate_production_settings()
    redis.init()
    db = SessionLocal()
    try:
        warn_if_seed_admin_present(db)
    finally:
        db.close()
    try:
        yield
    finally:
        redis.redis_client.close()
        dbEngine.dispose()


_is_production = settings.APP_ENV == "production"

app = FastAPI(
    lifespan=lifespan,
    docs_url=None if _is_production else "/",
    redoc_url=None if _is_production else "/redoc",
    openapi_url=None if _is_production else "/openapi.json",
    title=settings.APP_TITLE,
    version=str(settings.APP_VERSION),
    description=settings.APP_DESCRIPTION,
)

app.add_middleware(RequestIdMiddleware)
if settings.METRICS_ENABLED:
    Instrumentator().instrument(app).expose(app, include_in_schema=False)

if settings.OTEL_ENABLED:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    provider = TracerProvider(resource=Resource.create({"service.name": "mercury"}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)))
    trace.set_tracer_provider(provider)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts_list)

if not _is_production:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

import_resources(app)
