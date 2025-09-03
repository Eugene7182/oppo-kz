from __future__ import annotations
import os

def _norm(url: str | None) -> str | None:
    if not url:
        return url
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

PROJECT_NAME = os.getenv("PROJECT_NAME", "OPPO KZ API")
PROJECT_VERSION = os.getenv("PROJECT_VERSION", "0.1.0")

DATABASE_URL = _norm(os.getenv("DATABASE_URL")) or "sqlite:///./data.db"

CORS_ORIGINS_RAW = os.getenv("CORS_ORIGINS", "").strip()
CORS_ORIGINS = ["*"] if not CORS_ORIGINS_RAW else [o.strip() for o in CORS_ORIGINS_RAW.split(",") if o.strip()]

JWT_SECRET = os.getenv("JWT_SECRET", os.getenv("SECRET_KEY", "change-me"))
JWT_ALGO = os.getenv("JWT_ALGO", os.getenv("ALGORITHM", "HS256"))
ACCESS_TOKEN_EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MIN", os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")))

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@oppo.kz")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "ChangeMe_123")
