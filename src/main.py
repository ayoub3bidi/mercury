from routes import user, health
import middleware.auth_guard as auth_guard
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import redis
from database.postgres_db import dbEngine, Base
import database.redis_db as redis

app_version = os.environ['APP_VERSION']
app_title = os.environ['APP_TITLE']
app_description = os.environ['APP_DESCRIPTION']
v = os.environ['API_VERSION']

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

app.include_router(health.router, tags=['Information'], prefix=f'/{v}')
app.include_router(auth_guard.router, tags=['Access Token'], prefix=f'/{v}')
app.include_router(user.router, tags=['User'], prefix=f'/{v}/user')