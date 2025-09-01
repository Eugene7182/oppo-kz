# backend/app/schemas.py
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

# База под Pydantic v2 (ORM -> схемы)
class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# -------------------
# AUTH / USERS
# -------------------
class TokenOut(ORMModel):
    access_token: str
    token_type: str = "bearer"

class LoginIn(ORMModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=4)

class UserOut(ORMModel):
    id: int
    username: str
    full_name: Optional[str] = None
    role: Literal["super", "promoter"]
    is_active: bool = True
    store_id: Optional[int] = None
    network: Optional[str] = None

# --- Инвайты ---
class InviteCreateIn(ORMModel):
    username: str = Field(..., min_length=3)          # логин будущего пользователя (может быть e-mail)
    role: Literal["promoter", "super"] = "promoter"
    full_name: Optional[str] = None
    store_id: Optional[int] = None
    network: Optional[str] = None
    expires_hours: Optional[int] = 72

class InviteCreateOut(ORMModel):
    code: str
    username: str
    role: Literal["promoter", "super"]
    expires_at: datetime

class InviteCheckOut(ORMModel):
    valid: bool
    reason: Optional[Literal["not_found", "used", "expired"]] = None
    username: Optional[str] = None
    role: Optional[Literal["promoter", "super"]] = None
    full_name: Optional[str] = None
    store_id: Optional[int] = None
    network: Optional[str] = None
    expires_at: Optional[datetime] = None

class RegisterByInviteIn(ORMModel):
    code: str
    password: str = Field(..., min_length=4)
    full_name: Optional[str] = None

# -------------------
# СПРАВОЧНИКИ
# -------------------
class StoreIn(ORMModel):
    name: str
    city: Optional[str] = ""
    network: Optional[str] = ""

class StoreOut(ORMModel):
    id: int
    name: str
    city: str
    network: str

class SKUOut(ORMModel):
    id: int
    brand: str
    model: str
    code: str

# -------------------
# ПРАЙС-ЛИСТ
# -------------------
class PriceListIn(ORMModel):
    sku_id: int
    price: float
    valid_from: date
    valid_to: Optional[date] = None

class PriceListOut(ORMModel):
    id: int
    sku_id: int
    price: float
    valid_from: date
    valid_to: Optional[date] = None

# -------------------
# ЗАГРУЗКА ПРОДАЖ
# -------------------
class UploadResult(ORMModel):
    rows_total: int
    rows_inserted: int
    rows_skipped: int
    errors: List[str] = []

# -------------------
# СВЕРКА
# -------------------
class ReconciliationItem(ORMModel):
    date: date
    store_id: int
    store_name: str
    sku_id: int
    sku_code: str
    promoter_qty: int = 0
    network_qty: int = 0

    @property
    def diff(self) -> int:
        return (self.promoter_qty or 0) - (self.network_qty or 0)

class ReconciliationSummary(ORMModel):
    items: List[ReconciliationItem]
    total_promoter: int = 0
    total_network: int = 0
    total_diff: int = 0

class ReconciliationApproveItem(ORMModel):
    date: date
    store_id: int
    sku_id: int
    final_qty: int

class ReconciliationApproveIn(ORMModel):
    items: List[ReconciliationApproveItem]

# -------------------
# ИТОГОВЫЕ ПРОДАЖИ
# -------------------
class FinalSaleOut(ORMModel):
    id: int
    date: date
    store_id: int
    sku_id: int
    qty: int
    amount: float
    source: Literal["network", "promoter"]

# --- Bonus Grids ---
from datetime import date
from pydantic import BaseModel, Field
from typing import Optional

class BonusGridIn(BaseModel):
    sku_id: Optional[int] = Field(default=None, description="Конкретный SKU или None, если сетка по сети")
    network: Optional[str] = Field(default=None, description="Сеть (Store.network) или None, если сетка по SKU")
    qty_from: Optional[int] = Field(default=1, ge=1)
    bonus_per_unit: float = Field(..., ge=0)
    valid_from: date
    valid_to: Optional[date] = None

class BonusGridOut(BonusGridIn):
    id: int

class StoreCoefficientIn(ORMModel):
    store_id: int
    code: str
    value: float | None = None
    note: str | None = None
    valid_from: date | None = None
    valid_to: date | None = None

class StoreCoefficientOut(ORMModel):
    id: int
    store_id: int
    code: str
    value: float | None = None
    note: str | None = None
    valid_from: date
    valid_to: date | None = None

# ---------- Audit Log ----------
class AuditLogOut(ORMModel):
    id: int
    actor_username: str | None = None
    action: str
    entity: str | None = None
    entity_id: str | None = None
    before_json: str | None = None
    after_json: str | None = None
    ts: datetime

# ---------- Bonus ----------
class BonusCalcItem(ORMModel):
    promoter: str
    amount: float

class BonusCalcPreviewIn(ORMModel):
    period_from: date
    period_to: date
    sales: list[dict] | None = None  # optional inline sales data
    bonus_rules: list[dict] | None = None  # optional rules

class BonusCalcPreviewOut(ORMModel):
    total: float
    by_promoter: list[BonusCalcItem]

class BonusCommitIn(ORMModel):
    period_from: date
    period_to: date
    by_promoter: list[BonusCalcItem]

class BonusPayoutOut(ORMModel):
    id: int
    period_from: date
    period_to: date
    promoter_username: str
    amount: float
    created_at: datetime

# ---------- Campaigns ----------
class CampaignIn(ORMModel):
    name: str
    start: date
    end: date
    note: str | None = None
    stores: list[str] | None = None
    skus: list[str] | None = None
    mechanics: dict | None = None

class CampaignOut(ORMModel):
    id: int
    name: str
    start: date
    end: date
    note: str | None = None
    stores: list[str] | None = None
    skus: list[str] | None = None
    mechanics: dict | None = None
# backend/app/schemas.py
from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


# ---------- Notifications ----------
class NotificationOut(BaseModel):
    id: int
    title: str
    body: str | None = None
    is_read: bool
    created_at: datetime


class NotificationMarkReadIn(BaseModel):
    ids: list[int]


class NotificationPrefOut(BaseModel):
    email_enabled: bool = True
    push_enabled: bool = True


class NotificationPrefUpdate(BaseModel):
    email_enabled: bool | None = None
    push_enabled: bool | None = None
