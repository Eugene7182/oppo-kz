# backend/app/schemas/__init__.py
"""
Public exports for app.schemas so that `from app.schemas import ...` works.
"""

# ---- Auth schemas ----
from .auth import (
    TokenOut,
    LoginInput,
    RefreshInput,
    InviteCreateIn,
    InviteCreateOut,
    InviteCheckOut,
    RegisterByInviteIn,
)

# ---- User schemas ----
# Поддержим и user.py, и users.py — вдруг файл назван по-разному
try:
    from .user import UserOut  # type: ignore
except Exception:  # noqa: BLE001
    from .users import UserOut  # type: ignore

# ---- Optional: то, что уже встречалось в логах ----
try:
    from .stock_request import StockRequestCreate, StockRequestOut  # type: ignore
except Exception:
    pass

__all__ = [
    # auth
    "TokenOut",
    "LoginInput",
    "RefreshInput",
    "InviteCreateIn",
    "InviteCreateOut",
    "InviteCheckOut",
    "RegisterByInviteIn",
    # users
    "UserOut",
    # stock requests (если есть)
    "StockRequestCreate",
    "StockRequestOut",
]
