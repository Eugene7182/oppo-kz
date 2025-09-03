from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class InviteCreateIn(BaseModel):
    email: EmailStr
    role: str = "promoter"
    full_name: str | None = None
    expires_hours: int = Field(default=72, ge=1, le=24*14)

class InviteOut(BaseModel):
    code: str
    email: EmailStr
    role: str
    full_name: str | None
    expires_at: datetime

class InviteCheckOut(BaseModel):
    code: str
    status: str
    email: EmailStr
    role: str
    full_name: str | None
    expires_at: datetime

class InviteRegisterIn(BaseModel):
    code: str
    password: str
