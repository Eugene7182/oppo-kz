"""Network model."""

from __future__ import annotations

import uuid

from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Network(Base):
    """Торговая сеть."""

    __tablename__ = "networks"
    __table_args__ = (Index("ix_networks_name", "name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    stores = relationship("Store", back_populates="network", cascade="all, delete-orphan")


__all__ = ["Network"]
