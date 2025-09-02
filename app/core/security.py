from __future__ import annotations
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Literal
import jwt
from passlib.context import CryptContext

ACCESS_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE_ME_IN_PROD")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str: return pwd_context.hash(password)
def verify_password(plain: str, hashed: str) -> bool: return pwd_context.verify(plain, hashed)

def _create_token(sub: str, token_type: Literal["access","refresh"], minutes=30, days=0) -> str:
    now = datetime.now(timezone.utc)
    exp = now + (timedelta(days=days) if days else timedelta(minutes=minutes))
    payload: dict[str, Any] = {"sub": sub, "type": token_type, "iat": int(now.timestamp()), "nbf": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(sub: str) -> str: return _create_token(sub, "access", minutes=ACCESS_MINUTES)
def create_refresh_token(sub: str) -> str: return _create_token(sub, "refresh", days=REFRESH_DAYS)
def decode_token(token: str) -> dict[str, Any]: return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
