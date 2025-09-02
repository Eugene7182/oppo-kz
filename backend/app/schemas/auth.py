from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from pydantic import ConfigDict


# ======== AUTH ========

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class RefreshInput(BaseModel):
    refresh_token: str


# ======== INVITES ========

class InviteCreateIn(BaseModel):
    """
    Входная модель для создания инвайта.
    - email: обязательно
    - role: по умолчанию 'promoter' (подставь нужный дефолт)
    - note: опционально
    - expires_in_days: опционально, если хочешь задавать TTL в днях
    - expires_at: опционально, можно прислать конкретную дату
    """
    email: EmailStr
    role: str = Field(default="promoter", description="User role to be invited with")
    note: Optional[str] = None
    expires_in_days: Optional[int] = Field(default=7, ge=1, le=365)
    expires_at: Optional[datetime] = None


# на всякий случай оставим старое имя, если где-то используется InviteCreate
class InviteCreate(InviteCreateIn):
    pass


class InviteOut(BaseModel):
    id: int
    email: EmailStr
    code: str
    role: str
    note: Optional[str] = None
    expires_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
