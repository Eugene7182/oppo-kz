# backend/app/schemas/sku.py
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

class SKUOut(BaseModel):
    """
    Универсальная схема для чтения SKU.
    Поля сделаны опциональными, чтобы не падать, если каких-то атрибутов нет в ORM.
    """
    model_config = ConfigDict(from_attributes=True)

    id: str  # в проекте id обычно UUID-строка; если у тебя int — тоже отработает (сконвертирует)
    sku: Optional[str] = None
    code: Optional[str] = None
    name: Optional[str] = None
    brand: Optional[str] = None
    model_name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None
