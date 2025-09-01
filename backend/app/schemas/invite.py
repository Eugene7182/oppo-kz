from pydantic import BaseModel, EmailStr, Field

class InviteCreate(BaseModel):
    username: str = Field(min_length=2, max_length=128)
    role: str
    full_name: str | None = None
    expires_hours: int = 72

class InviteOut(BaseModel):
    code: str
    username: str
    role: str
    full_name: str | None = None
    email: EmailStr | None = None
    is_valid: bool

class InviteRegister(BaseModel):
    code: str
    password: str = Field(min_length=8)
    email: EmailStr
