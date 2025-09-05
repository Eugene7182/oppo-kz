"""Security utilities: hashing, JWT tokens and role-based access."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable, Sequence

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.db.session import get_db
from app.models.user import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ===== password helpers =====


def get_password_hash(password: str) -> str:
    """Return hashed password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ===== JWT helpers =====


def _create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(user: User) -> str:
    """Create short-lived access token."""
    return _create_token(
        {"sub": user.id, "role": user.role.value, "type": "access"},
        timedelta(minutes=settings.access_token_expires_min),
    )


def create_refresh_token(user: User) -> str:
    """Create long-lived refresh token."""
    return _create_token(
        {"sub": user.id, "role": user.role.value, "type": "refresh"},
        timedelta(days=settings.refresh_token_expires_days),
    )


def decode_refresh_token(token: str) -> str:
    """Return user id from refresh token or raise 401."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != "refresh":
            raise ValueError
        sub = payload.get("sub")
        if sub is None:
            raise ValueError
        return str(sub)
    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": "Invalid refresh token", "code": "invalid_token"},
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


# ===== dependencies =====


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),  # noqa: B008
    token: str = Depends(oauth2_scheme),  # noqa: B008
) -> User:
    """Decode access token and return current user."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"detail": "Could not validate credentials", "code": "not_authenticated"},
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != "access":
            raise ValueError
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError
    except Exception:  # noqa: BLE001
        raise credentials_exc from None

    from app.services import user_service

    user = user_service.get_user(db, str(user_id))
    if not user:
        raise credentials_exc
    request.state.user_id = user.id
    return user


def rbac_required(allowed_roles: Sequence[UserRole]) -> Callable[[User], User]:
    """Dependency to ensure user has allowed role."""

    def _dep(current_user: User = Depends(get_current_user)) -> User:  # noqa: B008
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"detail": "Forbidden", "code": "forbidden"},
            )
        return current_user

    return _dep


__all__ = [
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_refresh_token",
    "get_current_user",
    "rbac_required",
]
