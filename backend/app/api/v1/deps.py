# backend/app/api/v1/deps.py
from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

# ТРИ точки: app.api.v1 -> up2 -> app
from ...core.security import get_db as _get_db, get_current_user, require_roles
from ...models import User

def get_db() -> Session:
    yield from _get_db()

def require_super():
    return require_roles("super")

def require_promoter_or_super():
    return require_roles("promoter", "super")

def current_user(user: User = Depends(get_current_user)) -> User:
    return user
