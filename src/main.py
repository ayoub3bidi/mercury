from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import redis
from database.postgres_db import dbEngine, Base, SessionLocal
import database.redis_db as redis
from restful_ressources import import_resources
from sqlalchemy.orm import Session
from utils.security import create_admin_user

app_version = os.environ['APP_VERSION']
app_title = os.environ['APP_TITLE']
app_description = os.environ['APP_DESCRIPTION']

Base.metadata.create_all(bind=dbEngine)
redis.init()

app = FastAPI(
        docs_url="/",
        title=app_title,
        version=app_version,
        description=app_description,
    )

if os.getenv('APP_ENV') == 'local':
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

create_admin_user()

import_resources(app)