# backend/app/deps.py
from __future__ import annotations

from typing import Generator, Optional
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt  # PyJWT

# --- гибкий импорт настроек ---
try:
    # если в config.py есть функция get_settings()
    from app.core.config import get_settings  # type: ignore
    settings = get_settings()
except Exception:
    try:
        # если в config.py уже создан объект settings
        from app.core.config import settings as _settings  # type: ignore
        settings = _settings
    except Exception:
        # безопасный фоллбек на переменные окружения
        class _Settings:
            JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
        settings = _Settings()
# --------------------------------

from app.db import SessionLocal
from app.models import User

# URL должен совпадать с твоим эндпоинтом выдачи токена
# Если у тебя другой путь (например, /api/v1/auth/token), поменяй ниже.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ===== DB session dependency =====
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===== Auth dependencies =====
def _get_user_by_identity(db: Session, identity: str) -> Optional[User]:
    q = db.query(User)
    if hasattr(User, "username") and hasattr(User, "email"):
        return q.filter((User.username == identity) | (User.email == identity)).first()
    if hasattr(User, "username"):
        return q.filter(User.username == identity).first()
    return q.filter(User.email == identity).first()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        sub = payload.get("sub") or payload.get("username") or payload.get("email")
        if not sub:
            raise credentials_exc
    except Exception:
        raise credentials_exc

    user = _get_user_by_identity(db, sub)
    if not user:
        raise credentials_exc

    if getattr(user, "is_active", True) is False:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


def get_current_user_admin_or_office(
    current_user: User = Depends(get_current_user),
) -> User:
    role = getattr(current_user, "role", None)
    is_super = bool(getattr(current_user, "is_superuser", False))

    if is_super:
        return current_user

    if isinstance(role, str) and role.lower() in {"admin", "office"}:
        return current_user

    try:
        if getattr(role, "name", "").lower() in {"admin", "office"}:
            return current_user
    except Exception:
        pass

    raise HTTPException(status_code=403, detail="Not enough permissions")
