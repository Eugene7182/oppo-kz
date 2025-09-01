from datetime import date, datetime, time
from typing import List, Optional
from pydantic import BaseModel

class NotificationBase(BaseModel):
    title: str
    body: Optional[str] = None
    kind: str = "info"
    for_date: Optional[date] = None

class NotificationOut(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    class Config: from_attributes = True

class NotificationMarkReadIn(BaseModel):
    ids: List[int]

class NotificationPrefOut(BaseModel):
    enable_time_reminders: bool
    times: Optional[List[time]] = None
    saturday_cutoff_hour: int
    enabled: bool

class NotificationPrefUpdate(BaseModel):
    enable_time_reminders: Optional[bool] = None
    times: Optional[List[time]] = None
    saturday_cutoff_hour: Optional[int] = None
    enabled: Optional[bool] = None
