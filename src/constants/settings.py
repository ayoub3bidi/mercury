import os
from pathlib import Path
from typing import Any

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: Any,
        env_settings: Any,
        dotenv_settings: Any,
        file_secret_settings: Any,
    ) -> tuple[Any, ...]:
        def secret_file_settings() -> dict[str, str]:
            values: dict[str, str] = {}
            for name in (
                "JWT_SECRET_KEY",
                "POSTGRES_PASSWORD",
                "OIDC_GOOGLE_CLIENT_SECRET",
                "LLM_API_KEY",
            ):
                path = os.environ.get(f"{name}_FILE")
                if path:
                    values[name] = Path(path).read_text(encoding="utf-8").rstrip("\r\n")
            return values

        # File-backed secrets intentionally override plaintext environment values.
        return (init_settings, secret_file_settings, env_settings, dotenv_settings, file_secret_settings)

    LISTEN_ADDR: str
    LISTEN_PORT: int = 8000
    APP_VERSION: str = "0.4.0"
    APP_TITLE: str
    APP_DESCRIPTION: str
    API_VERSION: str = "v1"
    APP_ENV: str = "local"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1,0.0.0.0,testserver"
    API_URL: str = "http://localhost:8000"
    HTTP_REQUEST_TIMEOUT: int = 60

    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_SIZE_POOL: int = 30
    POSTGRES_MAX_OVERFLOW: int = 10
    POSTGRES_POOL_TIMEOUT: int = 30
    POSTGRES_POOL_RECYCLE: int = 1800

    REDIS_HOST: str = "mercury_cache"
    REDIS_PORT: int = 6379
    REDIS_CACHE_DB: int = 0
    REDIS_BROKER_DB: int = 1

    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    MERCURY_AGENT_ENABLED: bool = False
    LLM_BASE_URL: str = "http://localhost:11434/v1"
    LLM_API_KEY: SecretStr = SecretStr("local")
    RUN_TOKEN_BUDGET: int = 256
    RUN_TIMEOUT_SECONDS: int = 60
    CELERY_TASK_TIME_LIMIT: int = 90

    METRICS_ENABLED: bool = True
    OTEL_ENABLED: bool = False
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"

    GOOGLE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_TOKEN_URL: str = "https://accounts.google.com/o/oauth2/token"
    GOOGLE_USER_INFO_URL: str = "https://www.googleapis.com/oauth2/v1/userinfo"
    OIDC_GOOGLE_CLIENT_ID: str = "changeme"
    OIDC_GOOGLE_CLIENT_SECRET: str = "changeme"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def v(self) -> str:
        return self.API_VERSION

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL(self) -> str:
        password = self.POSTGRES_PASSWORD.get_secret_value()
        return (
            f"postgresql://{self.POSTGRES_USER}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def OIDC_GOOGLE_REDIRECT_URI(self) -> str:
        return f"{self.API_URL.rstrip('/')}/{self.API_VERSION}/oidc/google"

    @property
    def jwt_secret_key(self) -> str:
        return self.JWT_SECRET_KEY.get_secret_value()

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]


settings = Settings()
