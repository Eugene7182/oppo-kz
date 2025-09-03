# backend/app/schemas/auth.py
from pydantic import BaseModel, EmailStr

class LoginIn(BaseModel):
    username: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
