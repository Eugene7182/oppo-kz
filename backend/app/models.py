# backend/app/models.py
from __future__ import annotations

from datetime import date, datetime, timezone
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    Integer, String, Date, DateTime, Numeric, ForeignKey, Boolean,
    UniqueConstraint, Index, Text
)

class Base(DeclarativeBase):
    pass


# ---------- Справочники ----------
class Store(Base):
    __tablename__ = "stores"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    city: Mapped[str] = mapped_column(String(80), default="")
    network: Mapped[str] = mapped_column(String(120), default="")
    __table_args__ = (
        UniqueConstraint("name", "city", "network", name="uq_store_name_city_net"),
    )


class SKU(Base):
    __tablename__ = "sku"
    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(40), index=True)
    model: Mapped[str] = mapped_column(String(80), index=True)
    code: Mapped[str]  = mapped_column(String(40), unique=True, index=True)


class PriceList(Base):
    __tablename__ = "price_list"
    id: Mapped[int] = mapped_column(primary_key=True)
    sku_id: Mapped[int] = mapped_column(ForeignKey("sku.id", ondelete="CASCADE"), index=True)
    price: Mapped[Numeric] = mapped_column(Numeric(12, 2))
    valid_from: Mapped[date] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    sku = relationship("SKU")

Index("ix_price_valid", PriceList.sku_id, PriceList.valid_from, PriceList.valid_to)


# ---------- Пользователи / инвайты ----------
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)  # логин (может быть e-mail)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    role: Mapped[str] = mapped_column(String(20), index=True)  # 'super' | 'promoter'
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # опциональные привязки
    default_store_id: Mapped[int | None] = mapped_column(ForeignKey("stores.id"), nullable=True)
    network: Mapped[str | None] = mapped_column(String(120), nullable=True)


class UserInvite(Base):
    __tablename__ = "user_invites"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)       # токен приглашения
    role: Mapped[str] = mapped_column(String(20))                                 # 'promoter' | 'super'
    username: Mapped[str] = mapped_column(String(100))                            # будущий логин (может быть e-mail)
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    store_id: Mapped[int | None] = mapped_column(ForeignKey("stores.id"), nullable=True)
    network: Mapped[str | None] = mapped_column(String(120), nullable=True)

    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("code", name="uq_user_invites_code"),)


# ---------- Бонусные сетки ----------
class BonusGrid(Base):
    __tablename__ = "bonus_grids"
    id: Mapped[int] = mapped_column(primary_key=True)
    sku_id: Mapped[int | None] = mapped_column(ForeignKey("sku.id"), nullable=True)  # по SKU...
    network: Mapped[str | None] = mapped_column(String(120), nullable=True)          # ...или по сети
    qty_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bonus_per_unit: Mapped[Numeric] = mapped_column(Numeric(12, 2))
    valid_from: Mapped[date] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)


# ---------- Продажи промоутера (MVP) ----------
class PromoterSale(Base):
    __tablename__ = "promoter_sales"
    id: Mapped[int] = mapped_column(primary_key=True)
    promoter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), index=True)
    sku_id: Mapped[int] = mapped_column(ForeignKey("sku.id"), index=True)
    sold_at: Mapped[date] = mapped_column(Date, index=True)
    qty: Mapped[int] = mapped_column(Integer)
    amount: Mapped[Numeric | None] = mapped_column(Numeric(12, 2), nullable=True)  # если None — считаем по прайсу


# ---------- Итоговые / сетевые продажи (для сверки/отчёта; можно не трогать) ----------
class SalesNetwork(Base):
    __tablename__ = "sales_networks"
    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), index=True)
    sku_id: Mapped[int] = mapped_column(ForeignKey("sku.id"), index=True)
    qty: Mapped[int] = mapped_column(Integer)
    amount: Mapped[Numeric] = mapped_column(Numeric(12, 2), default=0)
    sold_at: Mapped[date] = mapped_column(Date, index=True)
    source_doc: Mapped[str] = mapped_column(String(120), default="")
    __table_args__ = (
        UniqueConstraint("store_id", "sku_id", "sold_at", "source_doc", name="uq_sn_key"),
    )


class SalesFinal(Base):
    __tablename__ = "sales_final"
    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), index=True)
    sku_id: Mapped[int] = mapped_column(ForeignKey("sku.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    qty: Mapped[int] = mapped_column(Integer)
    amount: Mapped[Numeric] = mapped_column(Numeric(12, 2), default=0)
    source: Mapped[str] = mapped_column(String(16))  # 'network' | 'promoter'
    __table_args__ = (
        UniqueConstraint("store_id", "sku_id", "date", name="uq_sf_key"),
    )


class StoreCoefficient(Base):
    __tablename__ = "store_coefficients"
    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(16), index=True)
    value: Mapped[Numeric | None] = mapped_column(Numeric(6, 2), nullable=True)
    note: Mapped[str | None] = mapped_column(String(200), nullable=True)
    valid_from: Mapped[date] = mapped_column(Date, default=date.today)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    __table_args__ = (
        UniqueConstraint("store_id", "code", "valid_from", name="uq_store_coeff_key"),
        Index("ix_store_coeff_active", "store_id", "code", "valid_from", "valid_to"),
    )

# ---------- Audit Log ----------
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_username: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    entity: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    before_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    after_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, index=True)

# ---------- Bonus Payout ----------
class BonusPayout(Base):
    __tablename__ = "bonus_payouts"
    id: Mapped[int] = mapped_column(primary_key=True)
    period_from: Mapped[date] = mapped_column(Date, index=True)
    period_to: Mapped[date] = mapped_column(Date, index=True)
    promoter_username: Mapped[str] = mapped_column(String(120), index=True)
    amount: Mapped[Numeric] = mapped_column(Numeric(12,2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, index=True)

# ---------- Campaigns ----------
class Campaign(Base):
    __tablename__ = "campaigns"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    start: Mapped[date] = mapped_column(Date, index=True)
    end: Mapped[date] = mapped_column(Date, index=True)
    note: Mapped[str | None] = mapped_column(String(300), nullable=True)
    stores_json: Mapped[str | None] = mapped_column(Text, nullable=True)   # JSON list of store codes
    skus_json: Mapped[str | None] = mapped_column(Text, nullable=True)     # JSON list of sku codes
    mechanics_json: Mapped[str | None] = mapped_column(Text, nullable=True) # JSON blob
