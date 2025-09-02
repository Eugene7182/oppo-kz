# backend/app/schemas/__init__.py
"""
Единая точка ре-экспорта pydantic-схем.
ВАЖНО: объявляем __all__ один раз и аккумулируем экспорт.
"""

# --- store ---
from .store import StoreIn, StoreOut

# --- sku ---
from .sku import SKUOut

# --- auth ---
try:
    from .auth import TokenOut, LoginInput, RefreshInput, RegisterByInviteIn
except Exception:
    TokenOut = LoginInput = RefreshInput = RegisterByInviteIn = None

# --- invites ---
try:
    from .invites import (
        InviteCreateIn, InviteCreateOut,
        InviteCheckIn, InviteCheckOut,
        RegisterByInviteIn as InviteRegisterByInviteIn,
        InviteAcceptIn, InviteAcceptOut,
    )
except Exception:
    InviteCreateIn = InviteCreateOut = InviteCheckIn = InviteCheckOut = InviteRegisterByInviteIn = InviteAcceptIn = InviteAcceptOut = None

# --- users ---
from .user import UserOut  # ВАЖНО: импорт именно из user.py (не users.py)

__all__ = [
    # store
    "StoreIn", "StoreOut",
    # sku
    "SKUOut",
    # auth (если есть)
    "TokenOut", "LoginInput", "RefreshInput", "RegisterByInviteIn",
    # invites (если есть)
    "InviteCreateIn", "InviteCreateOut",
    "InviteCheckIn", "InviteCheckOut",
    "InviteRegisterByInviteIn", "InviteAcceptIn", "InviteAcceptOut",
    # users
    "UserOut",
]
