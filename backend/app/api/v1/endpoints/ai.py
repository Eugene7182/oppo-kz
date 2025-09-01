from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, require_office_or_supervisor_or_admin as require_power
from app.ai.service import recommend_replenish, recommend_transfer, detect_anomalies, RecoParams

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/reco/replenish")
def ai_reco_replenish(days: int = Query(28, ge=7, le=120), leadtime: int = Query(3, ge=0, le=30),
                      target_days: int = Query(7, ge=1, le=60), min_qty: int = Query(1, ge=0, le=100),
                      same_city_only: bool = Query(True), same_network_only: bool = Query(True),
                      db: Session = Depends(get_db), _: None = Depends(require_power)):
    p = RecoParams(days=days, leadtime=leadtime, target_days=target_days, min_qty=min_qty,
                   same_city_only=same_city_only, same_network_only=same_network_only)
    return recommend_replenish(db, p)

@router.get("/reco/transfer")
def ai_reco_transfer(days: int = Query(28, ge=7, le=120), leadtime: int = Query(3, ge=0, le=30),
                     target_days: int = Query(7, ge=1, le=60), min_qty: int = Query(1, ge=0, le=100),
                     same_city_only: bool = Query(True), same_network_only: bool = Query(True),
                     db: Session = Depends(get_db), _: None = Depends(require_power)):
    p = RecoParams(days=days, leadtime=leadtime, target_days=target_days, min_qty=min_qty,
                   same_city_only=same_city_only, same_network_only=same_network_only)
    return recommend_transfer(db, p)

@router.get("/alerts/anomalies")
def ai_alerts_anomalies(db: Session = Depends(get_db), _: None = Depends(require_power)):
    return detect_anomalies(db)
