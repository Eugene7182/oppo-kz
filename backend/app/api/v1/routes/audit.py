from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ....core.security import get_db, get_current_user, require_roles
from ....models import AuditLog
from ....schemas import AuditLogOut
from typing import List

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("/", response_model=List[AuditLogOut], dependencies=[Depends(require_roles("super"))])
def list_logs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.scalars(select(AuditLog).order_by(AuditLog.ts.desc()).limit(500)).all()
