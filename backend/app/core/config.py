from typing import Optional

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API
    PROJECT_NAME: str = "Broker Seguros API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DB_ECHO_LOG: bool = False

    # JWT
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str = "HS256"

    # PostgreSQL
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[PostgresDsn] = None

    # CORS
    BACKEND_CORS_ORIGINS: str

    # Environment
    ENVIRONMENT: str = "development"

    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = ""
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "info@brokerseguros.com"
    EMAILS_FROM_NAME: str = "BrokerSeguros"

    # First SuperUser
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return str(self.DATABASE_URL).replace(
                "postgresql://", "postgresql+asyncpg://"
            )
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                path=f"/{self.POSTGRES_DB}",
            )
        )

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "allow",  # Permitir campos extra en la configuración
    }


settings = Settings()
