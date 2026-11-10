import logging

from constants.settings import settings
from repositories.user import UserRepository

logger = logging.getLogger(__name__)

_DEFAULT_JWT_SECRETS = frozenset({"mysecretkey", "changeme", "secret"})
_DEFAULT_DB_PASSWORDS = frozenset({"mercury", "postgres", ""})
_SEED_ADMIN_EMAIL = "test@admin.com"


def validate_production_settings(config=settings) -> None:
    jwt_secret = config.jwt_secret_key
    if config.APP_ENV != "local" and jwt_secret == "mysecretkey":
        raise RuntimeError(
            "Startup blocked: set JWT_SECRET_KEY to a non-default value when APP_ENV is not local."
        )
    if config.APP_ENV != "production":
        return

    jwt_secret = config.jwt_secret_key
    if jwt_secret in _DEFAULT_JWT_SECRETS or len(jwt_secret) < 32:
        raise RuntimeError(
            "Production startup blocked: set a strong JWT_SECRET_KEY (at least 32 characters, not a default value)."
        )

    db_password = config.POSTGRES_PASSWORD.get_secret_value()
    if db_password in _DEFAULT_DB_PASSWORDS:
        raise RuntimeError(
            "Production startup blocked: set a strong POSTGRES_PASSWORD (not the default 'mercury' or empty)."
        )

    logger.warning(
        "Production mode: ensure CORS is restricted and the seeded admin user (%s) is removed or disabled.",
        _SEED_ADMIN_EMAIL,
    )


def warn_if_seed_admin_present(db, config=settings) -> None:
    if config.APP_ENV != "production":
        return
    if UserRepository.get_by_email(db, _SEED_ADMIN_EMAIL) is not None:
        logger.warning(
            "Production mode: default seed admin %s still exists in the database.",
            _SEED_ADMIN_EMAIL,
        )
