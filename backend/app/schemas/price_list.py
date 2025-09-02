from __future__ import annotations
from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict

class PriceListIn(BaseModel):
    """
    Входная схема для создания/обновления прайс-записи.
    Поля опциональны, чтобы не падать на несовпадениях.
    """
    model_config = ConfigDict(extra="allow")  # разрешаем лишние ключи

    sku_id: Optional[str] = None
    price: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


class PriceListOut(BaseModel):
    """
    Выходная схема для чтения прайс-записей.
    """
    model_config = ConfigDict(from_attributes=True, extra="allow")

    id: str
    sku_id: Optional[str] = None
    price: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
