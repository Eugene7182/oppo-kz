# backend/app/schemas/auth.py
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class RefreshInput(BaseModel):
    refresh_token: str


# >>> ЭТОЙ МОДЕЛИ НЕ ХВАТАЛО <<<
class RegisterByInviteIn(BaseModel):
    """Поля под регистрацию по инвайту.
    Делайте их под ваш фактический payload.
    """
    invite_code: str          # или token: str — как у вас называется
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    # чтобы не падать, если прилетят лишние поля
    model_config = ConfigDict(extra="ignore")
