"""Store model."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Store(Base):
    """Магазин сети в регионе."""

    __tablename__ = "stores"
    __table_args__ = (
        Index("ix_stores_network_id", "network_id"),
        Index("ix_stores_region_id", "region_id"),
        Index("ix_stores_active", "active"),
        UniqueConstraint("network_id", "code", name="uq_stores_network_code"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    network_id: Mapped[str] = mapped_column(ForeignKey("networks.id", ondelete="RESTRICT"), nullable=False)
    region_id: Mapped[str] = mapped_column(ForeignKey("regions.id", ondelete="RESTRICT"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    network = relationship("Network", back_populates="stores")
    region = relationship("Region", back_populates="stores")


__all__ = ["Store"]
