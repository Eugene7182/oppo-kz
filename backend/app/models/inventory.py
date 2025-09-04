
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Float, UniqueConstraint
from app.db.base import Base

class StockBalance(Base):
    __tablename__ = "stock_balances"
    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int] = mapped_column(Integer, nullable=False)
    sku_id: Mapped[int] = mapped_column(Integer, nullable=False)
    on_hand: Mapped[float] = mapped_column(Float, default=0.0)
    in_transit: Mapped[float] = mapped_column(Float, default=0.0)
    __table_args__ = (UniqueConstraint("store_id", "sku_id", name="uq_balance_store_sku"),)
