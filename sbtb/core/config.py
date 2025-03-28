import logging
from pathlib import Path
from typing import List, Optional

from pydantic import AnyHttpUrl, Field, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = Field(default="dev")
    PROJECT_ROOT: Path = Path(__file__).parent.parent.resolve()

    LOG_LEVEL: int = Field(default=logging.INFO)

    VERSION: str = Field(default="v1")

    DEBUG: bool = Field(default=True)
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    POSTGRES_USER: str = Field(default="")
    POSTGRES_PASSWORD: str = Field(default="")
    POSTGRES_HOST: str = Field(default="")
    POSTGRES_PORT: str = Field(default="")
    POSTGRES_DB: str = Field(default="")
    POOL_SIZE: int = Field(default=10)
    MAX_OVERFLOW: int = Field(default=10)

    DATABASE_URI: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
