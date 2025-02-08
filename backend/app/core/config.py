from typing import Optional

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Broker Seguros API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DB_ECHO_LOG: bool = False  # Controla si SQLAlchemy debe mostrar las consultas SQL

    POSTGRES_SERVER: str = "postgres"  # Nombre del servicio en docker-compose
    POSTGRES_HOST: str  # Alias para POSTGRES_SERVER
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: Optional[PostgresDsn] = None

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

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
