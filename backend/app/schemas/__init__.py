# backend/app/schemas/__init__.py

from .auth import (
    TokenOut,
    LoginInput,
    RefreshInput,
)

# ВАЖНО: plural — .invites
from .invites import (
    InviteCreateIn, InviteCreateOut,
    InviteCheckIn, InviteCheckOut,
    RegisterByInviteIn,
    InviteAcceptIn, InviteAcceptOut,
)

__all__ = [
    # auth
    "TokenOut", "LoginInput", "RefreshInput",
    # invites
    "InviteCreateIn", "InviteCreateOut",
    "InviteCheckIn", "InviteCheckOut",
    "RegisterByInviteIn",
    "InviteAcceptIn", "InviteAcceptOut",
]
