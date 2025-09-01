from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.push import PushSubscriptionIn, PushPublicKeyOut
from app.services.push import get_vapid_keys, save_subscription, delete_subscription, send_push

router = APIRouter()

@router.get("/public-key", response_model=PushPublicKeyOut)
async def public_key(session: AsyncSession = Depends(get_session)):
    keys = await get_vapid_keys(session)
    return PushPublicKeyOut(public_key=keys["public"])

@router.post("/subscribe")
async def subscribe(payload: PushSubscriptionIn, session: AsyncSession = Depends(get_session), user_agent: str | None = Header(default=None)):
    user_id = 1  # TODO: заменить на текущего пользователя
    k = payload.keys or {}
    if not payload.endpoint or "p256dh" not in k or "auth" not in k:
        raise HTTPException(status_code=400, detail="Invalid subscription payload")
    await save_subscription(session, user_id, payload.endpoint, k["p256dh"], k["auth"], payload.user_agent or user_agent)
    return {"ok": True}

@router.post("/unsubscribe")
async def unsubscribe(payload: PushSubscriptionIn, session: AsyncSession = Depends(get_session)):
    if not payload.endpoint:
        raise HTTPException(status_code=400, detail="No endpoint")
    await delete_subscription(session, payload.endpoint)
    return {"ok": True}

@router.post("/test")
async def test_push(session: AsyncSession = Depends(get_session)):
    user_id = 1  # TODO: заменить на текущего пользователя
    await send_push(session, user_id, title="Тестовое уведомление", body="Web Push работает ✅")
    return {"sent": True}
