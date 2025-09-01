from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str  # если у вас Enum в БД — оставляем str для сериализации
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    position: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # позволяем создавать из ORM-объектов (SQLAlchemy)
    model_config = ConfigDict(from_attributes=True)
