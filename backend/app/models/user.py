from enum import Enum as PyEnum
from sqlalchemy import Enum as SAEnum, Column, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base

class UserRole(str, PyEnum):
    admin = "admin"
    office = "office"
    supervisor = "supervisor"   # <-- добавили
    promoter = "promoter"

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, name="userrole", native_enum=True), nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    # остальное как было
