from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.session import get_session
from app.schemas import (
    NotificationOut,
    NotificationMarkReadIn,
    NotificationPrefOut,
    NotificationPrefUpdate,
)

from app.models.notification import Notification
from app.models.notification_pref import NotificationPreference

router = APIRouter()

@router.get("", response_model=List[NotificationOut])
async def list_notifications(session: AsyncSession = Depends(get_session)):
    q = select(Notification).order_by(Notification.created_at.desc())
    items = (await session.execute(q)).scalars().all()
    return items

@router.post("/read")
async def mark_read(payload: NotificationMarkReadIn, session: AsyncSession = Depends(get_session)):
    if not payload.ids: return {"updated": 0}
    res = await session.execute(update(Notification).where(Notification.id.in_(payload.ids)).values(is_read=True))
    await session.commit()
    return {"updated": res.rowcount or 0}

@router.get("/preferences", response_model=NotificationPrefOut)
async def get_prefs(session: AsyncSession = Depends(get_session)):
    pref = (await session.execute(select(NotificationPreference))).scalar_one_or_none()
    if not pref:
        pref = NotificationPreference(user_id=1)  # TODO: current_user.id
        session.add(pref); await session.commit(); await session.refresh(pref)
    return NotificationPrefOut(
        enable_time_reminders=pref.enable_time_reminders,
        times=pref.times,
        saturday_cutoff_hour=pref.saturday_cutoff_hour,
        enabled=pref.enabled
    )

@router.put("/preferences", response_model=NotificationPrefOut)
async def update_prefs(payload: NotificationPrefUpdate, session: AsyncSession = Depends(get_session)):
    pref = (await session.execute(select(NotificationPreference))).scalar_one_or_none()
    if not pref: raise HTTPException(status_code=404, detail="Preferences not found")
    if payload.enable_time_reminders is not None: pref.enable_time_reminders = payload.enable_time_reminders
    if payload.times is not None: pref.times = payload.times
    if payload.saturday_cutoff_hour is not None: pref.saturday_cutoff_hour = payload.saturday_cutoff_hour
    if payload.enabled is not None: pref.enabled = payload.enabled
    await session.commit(); await session.refresh(pref)
    return NotificationPrefOut(
        enable_time_reminders=pref.enable_time_reminders, times=pref.times,
        saturday_cutoff_hour=pref.saturday_cutoff_hour, enabled=pref.enabled
    )
