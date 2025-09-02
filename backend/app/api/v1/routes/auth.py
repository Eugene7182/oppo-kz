# backend/app/api/v1/routes/auth.py
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt  # PyJWT
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..deps import get_db  # берем сессию БД из твоего deps.py
from app.models import User  # у тебя модели сведены в app.models (монолит)
from app.schemas.auth import TokenOut, LoginInput, RefreshInput
from app.schemas.user import UserOut


router = APIRouter(prefix="/auth", tags=["auth"])

# ---- Конфиги токенов и хэширования ----
ALGO = os.getenv("JWT_ALGORITHM", "HS256")
SECRET = os.getenv("JWT_SECRET", "CHANGE_ME_IN_PROD")
ACCESS_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ---- Утилиты безопасности (локально, чтобы не тащить внешние зависимости) ----
def _hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_token(sub: str, ttype: str, minutes: int | None = None, days: int | None = None) -> str:
    now = datetime.now(tz=timezone.utc)
    exp = now + (timedelta(days=days or 0) if days else timedelta(minutes=minutes or 30))
    payload: dict[str, Any] = {
        "sub": sub,
        "type": ttype,           # "access" | "refresh"
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def _decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, SECRET, algorithms=[ALGO])


def _create_access(sub: str) -> str:
    return _create_token(sub, "access", minutes=ACCESS_MIN)


def _create_refresh(sub: str) -> str:
    return _create_token(sub, "refresh", days=REFRESH_DAYS)


# ---- Зависимость: текущий пользователь по access-токену ----
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = _decode_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No subject in token")

    user = db.get(User, user_id)
    if not user or not getattr(user, "is_active", True):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User disabled or not found")
    return user


# ---- /auth/login (JSON) ----
@router.post("/login", response_model=TokenOut)
def login(payload: LoginInput, db: Session = Depends(get_db)) -> TokenOut:
    """
    Логин по JSON (username или email + пароль).
    Возвращает пару токенов: access/refresh.
    """
    user: User | None = (
        db.query(User)
        .filter(or_(User.username == payload.username, User.email == payload.username))
        .first()
    )
    if not user or not _verify_password(payload.password, getattr(user, "hashed_password", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")

    # Обновим last_login_at, если поле есть в модели.
    if hasattr(user, "last_login_at"):
        setattr(user, "last_login_at", datetime.utcnow())
        db.add(user)
        db.commit()

    return TokenOut(
        access_token=_create_access(user.id),
        refresh_token=_create_refresh(user.id),
    )


# ---- /auth/refresh ----
@router.post("/refresh", response_model=TokenOut)
def refresh(payload: RefreshInput, db: Session = Depends(get_db)) -> TokenOut:
    """
    Обновление пары токенов по refresh-токену.
    """
    try:
        data = _decode_token(payload.refresh_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_id = data.get("sub")
    user = db.get(User, user_id)
    if not user or not getattr(user, "is_active", True):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User disabled or not found")

    return TokenOut(
        access_token=_create_access(user.id),
        refresh_token=_create_refresh(user.id),
    )


# ---- /auth/me ----
@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)) -> UserOut:
    """
    Текущий пользователь по access-токену.
    """
    return current
