from routes import auth, health
from routes.user import user
from routes.admin import user as admin_user
from routes.oidc import google
from constants.environment_variables import v


def import_resources(app):
    app.include_router(health.router, tags=["Information"], prefix=f"/{v}")
    app.include_router(auth.router, prefix=f"/{v}")
    app.include_router(google.router, tags=["OIDC"], prefix=f"/{v}/oidc")
    app.include_router(admin_user.router, tags=['Admin'], prefix=f'/{v}/admin/user')
    app.include_router(user.router, tags=['User'], prefix=f'/{v}/user')