# backend/app/core/security.py
from __future__ import annotations

"""
Security utilities: hashing, JWT tokens, and role-based access.
- Пароли: bcrypt (passlib)
- JWT: access/refresh, HS256
- Зависимости: current_user, RBAC
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Callable, List, Optional

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.db.session import get_db
from app.models.user import User, UserRole

# ----- Password hashing -----
_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Хеш пароля для хранения в БД."""
    return _pwd_ctx.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка совпадения пароля с хешем."""
    return _pwd_ctx.verify(plain_password, hashed_password)


# ----- JWT helpers -----
_bearer = HTTPBearer(auto_error=False)  # не падать, если нет заголовка


def _create_token(
    *, subject: str, token_type: str, expires_delta: timedelta
) -> str:
    """
    Сформировать JWT.
    subject: id пользователя (строка UUID).
    token_type: 'access' | 'refresh'
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    secret = settings.secret_key
    algorithm = getattr(settings, "ALGORITHM", "HS256")
    return jwt.encode(payload, secret, algorithm=algorithm)


def create_access_token(user_id: str) -> str:
    minutes = int(getattr(settings, "ACCESS_TOKEN_EXPIRES_MIN", 30))
    return _create_token(
        subject=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=minutes),
    )


def create_refresh_token(user_id: str) -> str:
    days = int(getattr(settings, "REFRESH_TOKEN_EXPIRES_DAYS", 7))
    return _create_token(
        subject=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=days),
    )


def decode_token(token: str) -> dict[str, Any]:
    """Декод без валидации ролей; бросает HTTP 401 на любой проблеме."""
    try:
        data = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[getattr(settings, "ALGORITHM", "HS256")],
            options={"require": ["sub", "type", "exp"]},
        )
        return data
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "token_expired", "detail": "Token expired"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "token_invalid", "detail": "Invalid token"},
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_refresh_token(token: str) -> str:
    """Return user id from refresh token."""
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "wrong_token_type", "detail": "Refresh token required"},
        )
    return payload.get("sub")


# ----- Dependencies -----
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """
    Достаёт пользователя из access-токена.
    Требует Authorization: Bearer <access>.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "credentials_missing", "detail": "Missing Bearer token"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "wrong_token_type", "detail": "Access token required"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "no_subject", "detail": "Token has no subject"},
        )

    # Загрузка пользователя
    user: Optional[User] = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "user_not_found", "detail": "User not found"},
        )
    return user


def rbac_required(allowed_roles: List[UserRole]) -> Callable[[User], User]:
    """
    Dependency-генератор: ограничение доступа по ролям.
    Пример:
        @router.get("/admin-only", dependencies=[Depends(rbac_required([UserRole.admin]))])
    """
    def _dep(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "forbidden", "detail": "Insufficient role"},
            )
        return current_user

    return _dep
