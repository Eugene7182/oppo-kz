# backend/app/core/security.py
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Callable

import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..db import SessionLocal, get_db
from ..models import User


# =========================
# Пароли: bcrypt (passlib)
# =========================
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return _pwd.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return _pwd.verify(password, password_hash)


# =========================
# JWT
# =========================
ALGORITHM = "HS256"
SECRET_KEY = os.getenv("SECRET_KEY") or os.getenv("JWT_SECRET") or "CHANGE_ME_LONG_RANDOM_SECRET"

def create_access_token(
    data: Dict[str, Any],
    expires_minutes: int = 60 * 24,  # 24 часа по умолчанию
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return None


# =========================
# DB session dependency
# =========================
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# Current user & ACL
# =========================
_bearer = HTTPBearer(auto_error=False)

def _auth_error(detail: str, code: int = status.HTTP_401_UNAUTHORIZED):
    raise HTTPException(
        status_code=code,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
   
    # #turn user

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        _auth_error("Could not validate credentials")
    username = payload.get("sub")
    if username is None:
        _auth_error("Missing subject in token")
    user = db.query(User).filter(User.email == username).first()
    if user is None:
        _auth_error("User not found")
    return user


def require_roles(*roles: str) -> Callable[[User], User]:
    """
    Зависимость-валидатор ролей:
      @router.post(..., dependencies=[Depends(require_roles("super"))])
      def handler(current: User = Depends(get_current_user)): ...
    Или:
      def handler(current: User = Depends(require_roles("promoter","super"))): ...
    """
    def _dep(user: User = Depends(get_current_user)) -> User:
        if roles and user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user
    return _dep
