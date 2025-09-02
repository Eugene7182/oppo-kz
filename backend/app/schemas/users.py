# backend/app/schemas/users.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class UserOut(BaseModel):
    id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None

    # чтобы работать с ORM-объектами (SQLAlchemy)
    model_config = ConfigDict(from_attributes=True)

__all__ = ["UserOut"]
