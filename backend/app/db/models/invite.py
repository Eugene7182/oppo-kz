# backend/app/db/models/invite.py
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime, Index
from app.db.base_class import Base

class Invite(Base):
    __tablename__ = "invites"
    # Индексы для create_all (будут созданы без Alembic)
    __table_args__ = (
        Index("ix_invites_email", "email"),
        Index("ix_invites_active", "email", "used"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="promoter")

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)  # email создателя
