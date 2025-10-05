"""Monthly promoter plans and audit trail."""
from __future__ import annotations

import enum
import uuid

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.sale import utcnow


class PlanSource(str, enum.Enum):
    """Источник плана."""

    manual = "manual"
    import_file = "import"
    system = "system"


class PlanPromoterMonth(Base):
    """План на месяц для промоутера по магазину."""

    __tablename__ = "plan_promoter_month"
    __table_args__ = (
        Index("ix_plan_promoter_period", "promoter_id", "period_ym"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    period_ym: Mapped[str] = mapped_column(String(7), nullable=False)
    promoter_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    store_id: Mapped[str | None] = mapped_column(ForeignKey("stores.id", ondelete="SET NULL"), nullable=True)
    target_units: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_revenue: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    source: Mapped[PlanSource] = mapped_column(
        Enum(PlanSource, name="plansource", native_enum=True), default=PlanSource.manual, nullable=False
    )
    updated_by: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    audits = relationship("PlanAudit", back_populates="plan", cascade="all, delete-orphan")


class PlanAudit(Base):
    """Аудит изменений планов."""

    __tablename__ = "plan_audit"
    __table_args__ = (Index("ix_plan_audit_plan_id", "plan_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id: Mapped[str] = mapped_column(ForeignKey("plan_promoter_month.id", ondelete="CASCADE"), nullable=False)
    before_json: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    after_json: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    plan = relationship("PlanPromoterMonth", back_populates="audits")


__all__ = ["PlanPromoterMonth", "PlanAudit", "PlanSource"]
