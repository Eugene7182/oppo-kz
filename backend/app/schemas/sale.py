"""Pydantic models for sale API."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, constr

from app.models.sale import SaleStatus


class SaleCreate(BaseModel):
    """Создание продажи."""

    sale_id: constr(min_length=32, max_length=36)
    date: date
    store_id: str
    sku_id: str
    qty: int = Field(gt=0)
    price: Optional[Decimal] = Field(default=None, ge=0)


class SaleUpdate(BaseModel):
    """Частичное обновление продажи."""

    date: Optional[date] = None
    qty: Optional[int] = Field(default=None, ge=0)
    price: Optional[Decimal] = Field(default=None, ge=0)
    reason: Optional[str] = Field(default=None, max_length=500)


class SaleOut(BaseModel):
    """Ответ с продажей и фактическими данными."""

    id: str
    promoter_id: str
    store_id: str
    sku_id: str
    date: date
    qty: int
    price: Optional[Decimal]
    status: SaleStatus
    version: int
    locked: bool
    corrected: bool
    fact_qty: int
    fact_revenue: Optional[Decimal]
    locked_at: Optional[datetime]


class SaleCorrectionCreate(BaseModel):
    """Коррекция продажи."""

    delta_qty: int
    delta_price: Optional[Decimal] = Field(default=None)
    reason: str = Field(max_length=500)


class SaleCorrectionOut(BaseModel):
    """Выходная модель коррекции."""

    id: str
    sale_id: str
    delta_qty: int
    delta_price: Optional[Decimal]
    reason: str
    created_at: datetime


class SaleList(BaseModel):
    """Список продаж."""

    items: list[SaleOut]


__all__ = [
    "SaleCreate",
    "SaleUpdate",
    "SaleOut",
    "SaleCorrectionCreate",
    "SaleCorrectionOut",
    "SaleList",
]
