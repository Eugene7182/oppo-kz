# backend/app/deps.py
from __future__ import annotations

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt  # PyJWT

from app.core.config import settings
from app.db import SessionLocal
from app.models import User

# Тот же endpoint, где выдаётся токен (см. auth/login роут)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ===== DB session dependency =====
def get_db() -> Generator[Session, None, None]:
    """Отдаёт SQLAlchemy Session и корректно закрывает её."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===== Auth dependencies =====
def _get_user_by_identity(db: Session, identity: str) -> Optional[User]:
    """
    Пытаемся найти пользователя по username или email — поддерживаем оба варианта,
    чтобы не зависеть от конкретного поля в модели.
    """
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
    """
    Декодируем JWT и достаём пользователя из БД.
    Ожидаем HS256 и subject в 'sub' (или 'username'/'email' на всякий случай).
    """
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
    """
    Разрешаем доступ admin/superuser/office.
    Поддерживаем как строковые роли, так и Enum (через .name).
    """
    role = getattr(current_user, "role", None)
    is_super = bool(getattr(current_user, "is_superuser", False))

    if is_super:
        return current_user

    # строковые роли
    if isinstance(role, str) and role.lower() in {"admin", "office"}:
        return current_user

    # enum-подобные роли
    try:
        if getattr(role, "name", "").lower() in {"admin", "office"}:
            return current_user
    except Exception:
        pass

    raise HTTPException(status_code=403, detail="Not enough permissions")
