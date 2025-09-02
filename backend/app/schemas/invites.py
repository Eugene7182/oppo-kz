# backend/app/schemas/invites.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr

# ----- INPUTS -----
class InviteCreateIn(BaseModel):
    email: EmailStr
    role: Optional[str] = None
    note: Optional[str] = None

class InviteCheckIn(BaseModel):
    code: str

class RegisterByInviteIn(BaseModel):
    code: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class InviteAcceptIn(BaseModel):
    code: str

# ----- OUTPUTS -----
class InviteCreateOut(BaseModel):
    id: int
    code: str
    email: EmailStr
    role: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class InviteCheckOut(BaseModel):
    valid: bool
    reason: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None

class InviteAcceptOut(BaseModel):
    accepted: bool
    user_id: Optional[int] = None
    invited_email: Optional[EmailStr] = None

__all__ = [
    "InviteCreateIn", "InviteCreateOut",
    "InviteCheckIn", "InviteCheckOut",
    "RegisterByInviteIn",
    "InviteAcceptIn", "InviteAcceptOut",
]
