from pathlib import Path

from pydantic import SecretStr

from constants.settings import Settings
from utils.production_checks import validate_production_settings


def test_secret_file_overrides_plain_environment(monkeypatch, tmp_path: Path):
    secret_file = tmp_path / "jwt"
    secret_file.write_text("file-secret\n", encoding="utf-8")
    for name, value in {
        "LISTEN_ADDR": "127.0.0.1",
        "APP_TITLE": "Test",
        "APP_DESCRIPTION": "Test app",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_USER": "test",
        "POSTGRES_PASSWORD": "db-secret",
        "POSTGRES_DB": "test",
        "JWT_SECRET_KEY": "environment-secret",
        "JWT_SECRET_KEY_FILE": str(secret_file),
    }.items():
        monkeypatch.setenv(name, value)

    settings = Settings(_env_file=None)

    assert settings.jwt_secret_key == "file-secret"


def test_default_jwt_secret_is_rejected_outside_local():
    class Config:
        APP_ENV = "staging"
        JWT_SECRET_KEY = SecretStr("mysecretkey")
        POSTGRES_PASSWORD = SecretStr("strong-password")

        @property
        def jwt_secret_key(self):
            return self.JWT_SECRET_KEY.get_secret_value()

    try:
        validate_production_settings(Config())
    except RuntimeError as exc:
        assert "APP_ENV is not local" in str(exc)
    else:
        raise AssertionError("default JWT secret must fail outside local mode")


def test_default_jwt_secret_is_allowed_in_local():
    class Config:
        APP_ENV = "local"
        JWT_SECRET_KEY = SecretStr("mysecretkey")

        @property
        def jwt_secret_key(self):
            return self.JWT_SECRET_KEY.get_secret_value()

    validate_production_settings(Config())
