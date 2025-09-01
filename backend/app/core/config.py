# backend/app/core/config.py
import os
from dotenv import load_dotenv
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
ACCESS_TOKEN_EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MIN", "43200"))  # минут (30 суток по умолчанию)
DB_DSN     = os.getenv("DB_DSN", "sqlite:///./data.db")

_raw_cors = os.getenv("CORS_ORIGINS", "*").strip()
CORS_ORIGINS = ["*"] if _raw_cors in ("*", "") else [o.strip() for o in _raw_cors.split(",") if o.strip()]

ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "localhost").split(",")]

def cors_allow_credentials() -> bool:
    """Credentials (cookies) нельзя с origin='*'. Пока у нас токены/куки не нужны — выключаем."""
    return not ("*" in CORS_ORIGINS)
