from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from constants.settings import settings
import database.redis_db as redis
from database.postgres_db import Base, dbEngine
from restful_ressources import import_resources

Base.metadata.create_all(bind=dbEngine)
redis.init()

_is_production = settings.APP_ENV == "production"

app = FastAPI(
    docs_url=None if _is_production else "/",
    redoc_url=None if _is_production else "/redoc",
    openapi_url=None if _is_production else "/openapi.json",
    title=settings.APP_TITLE,
    version=str(settings.APP_VERSION),
    description=settings.APP_DESCRIPTION,
)

if not _is_production:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

import_resources(app)
