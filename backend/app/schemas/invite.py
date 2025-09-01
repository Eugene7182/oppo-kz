from pydantic import BaseModel, EmailStr
from enum import Enum

class InviteRole(str, Enum):
    admin = "admin"
    office = "office"
    supervisor = "supervisor"  # <-- добавили
    promoter = "promoter"

class InviteCreate(BaseModel):
    email: EmailStr
    role: InviteRole
    full_name: str | None = None
    expires_hours: int = 72
