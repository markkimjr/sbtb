import json
import os
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_SERVER_DIR = Path(__file__).parent.parent.parent


class Environment(StrEnum):
    local = "local"
    development = "development"
    testing = "testing"
    production = "production"


env = Environment(os.getenv("SBTB_ENV", Environment.local))
if env == Environment.local:
    _env_file = str(_SERVER_DIR / ".env.local")
elif env == Environment.testing:
    _env_file = str(_SERVER_DIR / ".env.test")
elif env == Environment.production:
    _env_file = str(_SERVER_DIR / ".env.prod")
else:
    _env_file = str(_SERVER_DIR / ".env.local")


class Settings(BaseSettings):
    ENV: Environment = Environment.local

    LOG_LEVEL: int = 20

    DEBUG: bool = True
    SQLALCHEMY_ECHO: bool = True

    POSTGRES_USER: str = "local"
    POSTGRES_PASSWORD: str = "local"
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_SESSION_PORT: int = 5432
    POSTGRES_DB: str = "sbtb"
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 10

    SENTRY_DSN: str | None = None

    CORS_ALLOWED_ORIGINS: list[str] = [
        "https://sbtb.io",
        "http://localhost",
        "http://localhost:3000",
    ]
    CORS_ALLOWED_HEADERS: list[str] = ["*"]

    BOXING_RANKINGS_URL: str | None = None
    BOXING_SCHEDULE_URL: str | None = None
    BOXING_HEADERS: dict | None = None

    @field_validator("BOXING_HEADERS", mode="before")
    @classmethod
    def parse_boxing_headers(cls, v: Any) -> dict | None:
        if isinstance(v, str):
            return json.loads(v)
        return v

    model_config = SettingsConfigDict(
        env_file=_env_file,
        env_file_encoding="utf-8",
        extra="allow",
    )

    @property
    def POSTGRES_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def POSTGRES_DATABASE_SESSION_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_SESSION_PORT}/{self.POSTGRES_DB}"

    def is_environment(self, environments: set[Environment]) -> bool:
        return self.ENV in environments

    def is_local(self) -> bool:
        return self.is_environment({Environment.local})

    def is_development(self) -> bool:
        return self.is_environment({Environment.development})

    def is_testing(self) -> bool:
        return self.is_environment({Environment.testing})

    def is_production(self) -> bool:
        return self.is_environment({Environment.production})


settings = Settings()
