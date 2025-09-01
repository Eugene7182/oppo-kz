import pytz
from datetime import datetime, date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.feature_flags import FeatureFlags
from app.services.lock import advisory_lock
from app.models.notification import Notification
from app.models.notification_pref import NotificationPreference
from app.db.session import async_session
from app.services.push import send_push

scheduler: AsyncIOScheduler | None = None

async def _notify(session: AsyncSession, user_id: int, title: str, body: str | None = None,
                  kind: str = "reminder", for_date: date | None = None):
    session.add(Notification(user_id=user_id, title=title, body=body, kind=kind, for_date=for_date))
    await session.commit()

async def _photo_reminders_for_supervisors(session: AsyncSession, tzname: str):
    tz = pytz.timezone(tzname)
    now = datetime.now(tz)
    if now.weekday() == 6:  # Sunday
        return
    today = now.date()

    prefs = (await session.execute(select(NotificationPreference))).scalars().all()
    # NOTE: предполагаем, что prefs принадлежат супервизорам; в реальном коде фильтруйте по роли
    for pref in prefs:
        if not pref.enabled:
            continue
        # Временные напоминания нам не важны здесь — пуши по расписанию идут всегда для фото при включённом флаге
        if now.weekday() == 5 and now.hour > pref.saturday_cutoff_hour:
            continue

        # TODO: заменить на реальную проверку "в команде есть те, кто не загрузил фото сегодня"
        team_missing_photos = True
        if team_missing_photos:
            title = "Фото-отчёт: не у всех промоутеров есть фото за сегодня"
            body = f"Проверьте фото-отчёты команды на {today.isoformat()}"
            await _notify(session, pref.user_id, title, body, kind="photo", for_date=today)
            await send_push(session, pref.user_id, title=title, body=body,
                            data={"type": "photo_reminder", "date": today.isoformat()})

async def scheduled_job(app: FastAPI):
    flags = FeatureFlags()
    async with async_session() as session:
        async with advisory_lock(session, key=20250901) as got:
            if not got:
                return
            if flags.ENABLE_PHOTO_REMINDERS:
                await _photo_reminders_for_supervisors(session, flags.TIMEZONE)
            # другие периодические задачи добавляйте ниже

async def start_scheduler(app: FastAPI):
    global scheduler
    if scheduler:
        return
    flags = FeatureFlags()
    scheduler = AsyncIOScheduler(timezone=flags.TIMEZONE)
    # Проверяем каждые 15 минут. Внутри учитываем день/часы/субботний лимит.
    scheduler.add_job(scheduled_job, CronTrigger(minute="0,15,30,45"), args=[app])
    scheduler.start()
