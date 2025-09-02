from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict

class SKUOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")
    id: str
    sku: Optional[str] = None
    code: Optional[str] = None
    name: Optional[str] = None
    brand: Optional[str] = None
    model_name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None
