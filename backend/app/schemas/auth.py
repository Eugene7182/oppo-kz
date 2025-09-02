# backend/app/schemas/auth.py
from __future__ import annotations

from pydantic import BaseModel


class LoginInput(BaseModel):
    """JSON-логин: username (или email) + пароль."""
    username: str
    password: str


class RefreshInput(BaseModel):
    """Запрос на обновление access-токена по refresh-токену."""
    refresh_token: str


class TokenOut(BaseModel):
    """Пара токенов на выходе."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
