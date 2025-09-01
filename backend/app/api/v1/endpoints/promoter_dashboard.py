from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, get_current_user, require_promoter
from app.promoter.dashboard import promoter_month_progress

router = APIRouter(prefix="/promoter", tags=["promoter"])

@router.get("/me/dashboard")
def promoter_me_dashboard(db: Session = Depends(get_db), user = Depends(get_current_user), _: None = Depends(require_promoter)):
    username = getattr(user, "username", None)
    return promoter_month_progress(db, username)
