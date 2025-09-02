# backend/app/schemas/__init__.py
"""
Единая точка ре-экспорта pydantic-схем.
ВАЖНО: не задавать __all__ повторно — только один раз.
"""

# --- store ---
from .store import StoreIn, StoreOut

# --- auth ---
# Подстрой под твои реальные имена в app/schemas/auth.py
try:
    from .auth import TokenOut, LoginInput, RefreshInput, RegisterByInviteIn
except Exception:
    # если ещё нет этих схем — не валимся на импорте
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
# 🔧 ВАЖНО: импортируем ИЗ user.py (единственное правильное имя файла), а НЕ из users.py
from .user import UserOut

__all__ = [
    # store
    "StoreIn", "StoreOut",
    # auth (если есть)
    "TokenOut", "LoginInput", "RefreshInput", "RegisterByInviteIn",
    # invites (если есть)
    "InviteCreateIn", "InviteCreateOut",
    "InviteCheckIn", "InviteCheckOut",
    "InviteRegisterByInviteIn", "InviteAcceptIn", "InviteAcceptOut",
    # users
    "UserOut",
]
