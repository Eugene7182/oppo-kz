from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, DateTime
from datetime import datetime
import enum
from app.db.base_class import Base

class StockRequestStatus(str, enum.Enum):
    NEW = "new"
    APPROVED = "approved"
    REJECTED = "rejected"
    FULFILLED = "fulfilled"

class StockRequest(Base):
    __tablename__ = "stock_requests"
    id = Column(Integer, primary_key=True, index=True)
    promoter_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    supervisor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="SET NULL"), index=True, nullable=True)
    sku_id = Column(Integer, ForeignKey("skus.id", ondelete="SET NULL"), index=True, nullable=True)
    memory_option = Column(String(50), nullable=True)  # напр. '8/256'
    qty = Column(Integer, nullable=False, default=1)
    comment = Column(Text, nullable=True)
    status = Column(Enum("new", "approved", "rejected", "fulfilled", name="stock_request_status"), nullable=False, default="new")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
