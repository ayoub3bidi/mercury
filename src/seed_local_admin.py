"""Seed the development administrator only for explicitly local environments."""

from constants.settings import settings

if settings.APP_ENV != "local":
    print("Local admin seed skipped: APP_ENV is not local.")
    raise SystemExit(0)

from database.postgres_db import SessionLocal  # noqa: E402
from models.User import User  # noqa: E402
from repositories.user import UserRepository  # noqa: E402
from utils.security import get_password_hash  # noqa: E402

with SessionLocal() as db:
    if UserRepository.get_by_email(db, "test@admin.com") is None:
        db.add(
            User(
                username="admin",
                email="test@admin.com",
                password=get_password_hash("Cloud.456"),
                is_admin=True,
                disabled=False,
            )
        )
        db.commit()
