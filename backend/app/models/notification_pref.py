from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, TIME
from app.db.base_class import Base

class NotificationPreference(Base):
    __tablename__ = "notification_prefs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    enable_time_reminders = Column(Boolean, nullable=False, default=False)
    times = Column(ARRAY(TIME), nullable=True)  # по умолчанию [11:00, 12:00, 14:00, 16:00, 18:00]
    saturday_cutoff_hour = Column(Integer, nullable=False, default=16)
    enabled = Column(Boolean, nullable=False, default=True)
