from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from constants.environment_variables import APP_DESCRIPTION, APP_ENV, APP_TITLE, APP_VERSION
import database.redis_db as redis
from database.postgres_db import Base, dbEngine, SessionLocal
from restful_ressources import import_resources
from utils.security import create_admin_user

Base.metadata.create_all(bind=dbEngine)
redis.init()

# Bootstrap admin user if configured
_db = SessionLocal()
try:
    create_admin_user(_db)
finally:
    _db.close()

app = FastAPI(
    docs_url="/",
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
)

if APP_ENV == "local":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

import_resources(app)