
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class ImportJob(Base):
  __tablename__ = "import_jobs"
  id: Mapped[int] = mapped_column(primary_key=True)
  type: Mapped[str] = mapped_column(String(50))
  filename: Mapped[str] = mapped_column(String(255))
  status: Mapped[str] = mapped_column(String(20), default="queued")
  progress: Mapped[int] = mapped_column(Integer, default=0)
  total: Mapped[int] = mapped_column(Integer, default=0)
  processed: Mapped[int] = mapped_column(Integer, default=0)
  error: Mapped[str | None] = mapped_column(Text)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
  updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
  payload: Mapped[bytes | None] = mapped_column(LargeBinary)
  mime: Mapped[str | None] = mapped_column(String(100))
