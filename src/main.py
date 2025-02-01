from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from constants.environment_variables import APP_DESCRIPTION, APP_TITLE, APP_VERSION, APP_ENV
from database.postgres_db import dbEngine, Base
import database.redis_db as redis
from restful_ressources import import_resources
# from utils.security import create_admin_user

Base.metadata.create_all(bind=dbEngine)
redis.init()

app = FastAPI(
        docs_url="/",
        title=APP_TITLE,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
    )

if APP_ENV == 'local':
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# create_admin_user()

import_resources(app)