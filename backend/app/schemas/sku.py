from pydantic import BaseModel, ConfigDict
from typing import Optional

class SKUOut(BaseModel):
    # + protected_namespaces=() — гасим конфликт с полем model_name
    model_config = ConfigDict(from_attributes=True, extra="allow", protected_namespaces=())
    id: str
    sku: Optional[str] = None
    code: Optional[str] = None
    name: Optional[str] = None
    brand: Optional[str] = None
    model_name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None
