"""City reference model."""
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class City(Base):
    """Город внутри региона."""

    __tablename__ = "cities"
    __table_args__ = (
        Index("ix_cities_region_id", "region_id"),
        UniqueConstraint("region_id", "name", name="uq_cities_region_name"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    region_id: Mapped[str] = mapped_column(ForeignKey("regions.id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    region = relationship("Region", back_populates="cities")


__all__ = ["City"]
