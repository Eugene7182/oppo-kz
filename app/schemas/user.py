from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.user import UserRole

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    email: EmailStr | None = None
    full_name: str | None = None
    role: UserRole
    is_active: bool = True

class UserRead(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
