from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    LISTEN_ADDR: str
    LISTEN_PORT: int = 8000
    APP_VERSION: str = "1.0"
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

    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

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
