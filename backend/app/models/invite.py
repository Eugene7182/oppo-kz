import uuid
from datetime import datetime, timedelta
from sqlalchemy import String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base  # если нет, используй app.db.session.Base

class Invite(Base):
    __tablename__ = "invite"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    # логин будущего пользователя (на UI у тебя "username"); email зададим при регистрации
    username: Mapped[str] = mapped_column(String(128), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(256), nullable=True)

    # роль храним как строку, валидируем в коде
    role: Mapped[str] = mapped_column(String(32), nullable=False)

    email: Mapped[str | None] = mapped_column(String(256), nullable=True)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(hours=72))

    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("user.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
