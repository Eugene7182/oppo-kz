"""Application settings.

Настройки читаются из переменных окружения.
"""

from __future__ import annotations

import json
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_db_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


class Settings(BaseSettings):
    """Project configuration via environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    database_url: str = "sqlite:///./app.db"
    secret_key: str = "change_me"
    cors_origins: list[str] = []
    debug: bool = False
    version: str = "0.1.0"
    git_commit: str | None = None
    algorithm: str = "HS256"
    access_token_expires_min: int = 30
    refresh_token_expires_days: int = 7
    admin_email: str | None = None
    admin_password: str | None = None
    enable_bonuses: bool = False
    enable_messages: bool = False
    enable_imports: bool = False
    enable_analytics: bool = False

    @field_validator("database_url", mode="before")
    @classmethod
    def _validate_db_url(cls, v: str) -> str:
        return _normalize_db_url(v)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            if v.startswith("["):
                return list(json.loads(v))
            return [o.strip() for o in v.split(",") if o.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()
