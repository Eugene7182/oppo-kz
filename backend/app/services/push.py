import json, os
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pywebpush import webpush, WebPushException
from app.models.push_subscription import PushSubscription
from app.models.app_setting import AppSetting

async def get_vapid_keys(session: AsyncSession) -> Dict[str, str]:
    pub = os.getenv("VAPID_PUBLIC_KEY")
    prv = os.getenv("VAPID_PRIVATE_KEY")
    sub = os.getenv("VAPID_SUBJECT", "mailto:admin@example.com")
    if pub and prv:
        return {"public": pub, "private": prv, "subject": sub}
    res_pub = await session.get(AppSetting, "VAPID_PUBLIC_KEY")
    res_prv = await session.get(AppSetting, "VAPID_PRIVATE_KEY")
    res_sub = await session.get(AppSetting, "VAPID_SUBJECT")
    if res_pub and res_prv:
        return {"public": res_pub.value, "private": res_prv.value, "subject": (res_sub.value if res_sub else sub)}
    try:
        from py_vapid import Vapid
        v = Vapid(); v.generate_keys()
        pub = v.public_key; prv = v.private_key
    except Exception as e:
        raise RuntimeError(f"Failed to generate VAPID keys: {e}")
    session.add(AppSetting(key="VAPID_PUBLIC_KEY", value=pub))
    session.add(AppSetting(key="VAPID_PRIVATE_KEY", value=prv))
    session.add(AppSetting(key="VAPID_SUBJECT", value=sub))
    await session.commit()
    return {"public": pub, "private": prv, "subject": sub}

async def save_subscription(session: AsyncSession, user_id: int, endpoint: str, p256dh: str, auth: str, ua: Optional[str]):
    existing = (await session.execute(select(PushSubscription).where(PushSubscription.endpoint == endpoint))).scalar_one_or_none()
    if existing:
        existing.user_id = user_id; existing.p256dh = p256dh; existing.auth = auth; existing.user_agent = ua
        await session.commit(); return existing
    sub = PushSubscription(user_id=user_id, endpoint=endpoint, p256dh=p256dh, auth=auth, user_agent=ua)
    session.add(sub); await session.commit(); await session.refresh(sub); return sub

async def delete_subscription(session: AsyncSession, endpoint: str):
    await session.execute(delete(PushSubscription).where(PushSubscription.endpoint == endpoint))
    await session.commit()

async def list_user_subscriptions(session: AsyncSession, user_id: int) -> List[PushSubscription]:
    res = await session.execute(select(PushSubscription).where(PushSubscription.user_id == user_id))
    return res.scalars().all()

async def send_push(session: AsyncSession, user_id: int, title: str, body: Optional[str] = None, data: Optional[dict] = None):
    keys = await get_vapid_keys(session)
    subs = await list_user_subscriptions(session, user_id)
    payload = json.dumps({"title": title, "body": body or "", "data": data or {}})
    for s in subs:
        try:
            webpush(
                subscription_info={"endpoint": s.endpoint, "keys": {"p256dh": s.p256dh, "auth": s.auth}},
                data=payload,
                vapid_private_key=keys["private"],
                vapid_claims={"sub": keys["subject"]},
                ttl=300,
            )
        except WebPushException as e:
            if getattr(e, "response", None) and e.response.status_code in (404, 410):
                await delete_subscription(session, s.endpoint)
