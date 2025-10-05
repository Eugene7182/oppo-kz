"""Schemas for promoter monthly plans."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.plan import PlanSource


class PlanPromoterMonthItem(BaseModel):
    """Запрос на массовое обновление планов."""

    period_ym: str = Field(pattern=r"^\d{4}-\d{2}$")
    promoter_id: str
    store_id: str | None = None
    target_units: int | None = Field(default=None, ge=0)
    target_revenue: Decimal | None = Field(default=None, ge=0)
    source: PlanSource = PlanSource.manual
    reason: str | None = Field(default=None, max_length=255)


class PlanPromoterMonthOut(BaseModel):
    """Ответ с планом."""

    id: str
    period_ym: str
    promoter_id: str
    store_id: str | None
    target_units: int | None
    target_revenue: Decimal | None
    source: PlanSource
    version: int
    updated_by: str | None
    updated_at: datetime


class PlanList(BaseModel):
    """Список планов."""

    items: list[PlanPromoterMonthOut]


class PlanPatch(BaseModel):
    """Запрос на частичное обновление плана."""

    target_units: int | None = Field(default=None, ge=0)
    target_revenue: Decimal | None = Field(default=None, ge=0)
    reason: str | None = Field(default=None, max_length=255)


__all__ = [
    "PlanPromoterMonthItem",
    "PlanPromoterMonthOut",
    "PlanList",
    "PlanPatch",
]
