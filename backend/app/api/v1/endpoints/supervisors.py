from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.deps import get_db, get_current_user_admin_or_office  # пример RBAC
from app.models import User, UserRole
from app.schemas import UserOut

router = APIRouter(tags=["supervisors"])

@router.get("/supervisors", response_model=list[UserOut])
def list_supervisors(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    _: User = Depends(get_current_user_admin_or_office)  # admin/office видят список
):
    q = db.query(User).filter(User.role == UserRole.supervisor).offset(skip).limit(limit)
    return q.all()
