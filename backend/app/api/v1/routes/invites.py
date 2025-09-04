# backend/app/api/v1/routes/invites.py
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.security_rbac import require_roles
from app.core.security import get_db, get_password_hash
from app.db.models.invite import Invite
from app.db.models.user import User
from app.schemas.invites import InviteCreateIn, InviteOut, InviteCheckOut, InviteRegisterIn

router = APIRouter(prefix="/auth/invites", tags=["auth"])

def _gen_code() -> str:
    return secrets.token_urlsafe(10)

@router.post("", response_model=InviteOut, summary="Создать инвайт", dependencies=[Depends(require_roles("admin"))])
def create_invite(
    data: InviteCreateIn,
    db: Session = Depends(get_db),
):
    code = _gen_code()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=data.expires_hours or 72)
    inv = Invite(email=data.email, full_name=data.full_name, role=data.role,
                 code=code, expires_at=expires_at, used=False)
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv

@router.get("/{code}", response_model=InviteCheckOut, summary="Проверить инвайт", dependencies=[Depends(require_roles("admin"))])
def check_invite(code: str, db: Session = Depends(get_db)):
    inv = db.query(Invite).filter(Invite.code == code).first()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
    now = datetime.now(timezone.utc)
    return {
        "email": inv.email,
        "full_name": inv.full_name,
        "role": inv.role,
        "used": inv.used,
        "expired": now >= inv.expires_at
    }

@router.post("/register", summary="Зарегистрироваться по инвайту", dependencies=[Depends(require_roles("admin"))])
def register_by_invite(data: InviteRegisterIn, db: Session = Depends(get_db)):
    inv = db.query(Invite).filter(Invite.code == data.code).first()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
    now = datetime.now(timezone.utc)
    if inv.used:
        raise HTTPException(status_code=400, detail="Invite already used")
    if now >= inv.expires_at:
        raise HTTPException(status_code=400, detail="Invite expired")
    if db.query(User).filter(User.email == inv.email).first():
        raise HTTPException(status_code=409, detail="User already exists")

    user = User(
        email=inv.email,
        full_name=inv.full_name,
        role=inv.role,
        password_hash=get_password_hash(data.password),
        is_active=True
    )
    db.add(user)
    inv.used = True
    db.add(inv)
    db.commit()
    return {"status": "registered", "email": user.email, "role": user.role}
