from pydantic import BaseModel, EmailStr
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    office = "office"
    supervisor = "supervisor"  # <-- добавили
    promoter = "promoter"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: str
