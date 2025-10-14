from __future__ import annotations
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # DB / SQLAlchemy
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SQL_ECHO: bool = Field(False, env="SQL_ECHO")

    # Auth
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # CORS（カンマ区切り or 複数値の両対応）
    CORS_ORIGINS: List[str] = Field(default_factory=list, env="CORS_ORIGINS")

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
