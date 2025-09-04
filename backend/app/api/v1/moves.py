
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, require_roles
from app.services.moves import recommend_moves

router = APIRouter(prefix="/moves", tags=["moves"])

@router.get("/recommendations")
def recommendations(max_moves: int = Query(20, ge=1, le=200), horizon_days: int = Query(30, ge=7, le=180),
                    db: Session = Depends(get_db), _=Depends(require_roles("admin","office","supervisor"))):
    return recommend_moves(db, max_moves=max_moves, horizon_days=horizon_days)
