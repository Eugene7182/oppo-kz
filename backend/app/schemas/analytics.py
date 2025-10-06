"""Analytics API schemas."""
from __future__ import annotations

from datetime import date
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PeriodValue(BaseModel):
    """Общие показатели периода."""

    qty: int
    revenue: Decimal

    model_config = ConfigDict(from_attributes=True)


class PeriodDelta(BaseModel):
    """Дельта между периодами."""

    current: PeriodValue | None
    previous: PeriodValue | None
    change_pct: Decimal | None


class FactValue(BaseModel):
    """Факт продаж: база + коррекции."""

    base_qty: int
    base_revenue: Decimal
    correction_qty: int
    correction_revenue: Decimal
    fact_qty: int
    fact_revenue: Decimal

    model_config = ConfigDict(from_attributes=True)


class SalesPerformanceOut(BaseModel):
    """Ответ аналитики продаж."""

    as_of: date
    mtd: FactValue
    mtd_lfl: PeriodDelta
    wow: PeriodDelta
    mom: PeriodDelta
    yoy: PeriodDelta


__all__ = [
    "PeriodValue",
    "PeriodDelta",
    "FactValue",
    "SalesPerformanceOut",
]
