from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_session
from app.schemas.stock_request import StockRequestCreate, StockRequestOut
from app.models.stock_request import StockRequest, StockRequestStatus

router = APIRouter()

@router.post("/requests", response_model=StockRequestOut)
async def create_request(payload: StockRequestCreate, session: AsyncSession = Depends(get_session)):
    sr = StockRequest(
        promoter_id=1,  # TODO: current_user.id
        supervisor_id=None,
        store_id=payload.store_id, sku_id=payload.sku_id,
        memory_option=payload.memory_option, qty=payload.qty, comment=payload.comment
    )
    session.add(sr); await session.commit(); await session.refresh(sr)
    return sr

@router.get("/requests", response_model=List[StockRequestOut])
async def list_requests(session: AsyncSession = Depends(get_session)):
    q = select(StockRequest).order_by(StockRequest.created_at.desc())
    return (await session.execute(q)).scalars().all()

@router.post("/requests/{req_id}/approve", response_model=StockRequestOut)
async def approve_request(req_id: int, session: AsyncSession = Depends(get_session)):
    sr = (await session.execute(select(StockRequest).where(StockRequest.id == req_id))).scalar_one_or_none()
    if not sr: raise HTTPException(status_code=404, detail="Not found")
    sr.status = StockRequestStatus.APPROVED; await session.commit(); await session.refresh(sr); return sr

@router.post("/requests/{req_id}/reject", response_model=StockRequestOut)
async def reject_request(req_id: int, session: AsyncSession = Depends(get_session)):
    sr = (await session.execute(select(StockRequest).where(StockRequest.id == req_id))).scalar_one_or_none()
    if not sr: raise HTTPException(status_code=404, detail="Not found")
    sr.status = StockRequestStatus.REJECTED; await session.commit(); await session.refresh(sr); return sr

@router.post("/requests/{req_id}/fulfill", response_model=StockRequestOut)
async def fulfill_request(req_id: int, session: AsyncSession = Depends(get_session)):
    sr = (await session.execute(select(StockRequest).where(StockRequest.id == req_id))).scalar_one_or_none()
    if not sr: raise HTTPException(status_code=404, detail="Not found")
    sr.status = StockRequestStatus.FULFILLED; await session.commit(); await session.refresh(sr); return sr
