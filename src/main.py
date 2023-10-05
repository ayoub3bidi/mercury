from api import user, health
import auth_guard
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import redis
from fastapi.openapi.utils import get_openapi
from database import dbEngine, Base

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Mercury API Docs",
        version=os.environ['VERSION'],
        description="This is the Swagger documentation of the Mercury API",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

Base.metadata.create_all(bind=dbEngine)
redis_host = os.getenv('REDIS_HOST')
redis_client = redis.Redis(host=redis_host, port=6379)

app = FastAPI(docs_url="/")
app.openapi = custom_openapi

if os.getenv('APP_ENV') == 'local':
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(health.router, tags=['Information'], prefix='/v1')
app.include_router(auth_guard.router, tags=['Access Token'], prefix='/v1')
app.include_router(user.router, tags=['User'], prefix='/v1/user')