
import os
from routes import health
import middleware.auth_guard as auth_guard
from routes.user import user
from routes.admin import user as admin_user
from constants.environment_variables import v

def import_resources(app):
    app.include_router(health.router, tags=['Information'], prefix=f'/{v}')
    app.include_router(auth_guard.router, tags=['Access Token'], prefix=f'/{v}')
    app.include_router(admin_user.router, tags=['Admin'], prefix=f'/{v}/admin/user')
    app.include_router(user.router, tags=['User'], prefix=f'/{v}/user')