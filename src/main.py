from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from constants.settings import settings
import database.redis_db as redis
from database.postgres_db import Base, dbEngine
from restful_ressources import import_resources

Base.metadata.create_all(bind=dbEngine)
redis.init()

app = FastAPI(
    docs_url="/",
    title=settings.APP_TITLE,
    version=str(settings.APP_VERSION),
    description=settings.APP_DESCRIPTION,
)

if settings.APP_ENV == "local":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

import_resources(app)
