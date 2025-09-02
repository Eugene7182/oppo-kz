# backend/app/schemas/bonus_grids.py
from __future__ import annotations
from typing import Optional, Any
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class BonusGridIn(BaseModel):
    """
    Входная схема для создания/обновления строк бонусной сетки.
    Делаем поля опциональными и разрешаем лишние ключи,
    чтобы не падать на несовпадениях с фактической моделью/JSON.
    """
    model_config = ConfigDict(extra="allow")

    # идентификаторы
    id: Optional[str] = None
    sku_id: Optional[str] = None
    store_id: Optional[str] = None
    network_id: Optional[str] = None
    region: Optional[str] = None

    # параметры бонуса
    bonus_type: Optional[str] = None         # %, фикс и т.п.
    bonus_value: Optional[float] = None      # величина бонуса
    min_qty: Optional[float] = None
    max_qty: Optional[float] = None

    # период действия
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    # флаги/метаданные
    is_active: Optional[bool] = None
    meta: Optional[dict[str, Any]] = None


class BonusGridOut(BaseModel):
    """
    Выходная схема для чтения/возврата бонусных сеток.
    """
    model_config = ConfigDict(from_attributes=True, extra="allow")

    id: str
    sku_id: Optional[str] = None
    store_id: Optional[str] = None
    network_id: Optional[str] = None
    region: Optional[str] = None

    bonus_type: Optional[str] = None
    bonus_value: Optional[float] = None
    min_qty: Optional[float] = None
    max_qty: Optional[float] = None

    start_date: Optional[date] = None
    end_date: Optional[date] = None

    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    meta: Optional[dict[str, Any]] = None
