import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from ....core.security import (
    hash_password, verify_password, create_access_token,
    require_roles, get_db, get_current_user
)
from ....models import User, UserInvite
from ....schemas import (
    TokenOut, UserOut,
    InviteCreateIn, InviteCreateOut, InviteCheckOut,
    RegisterByInviteIn,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------- LOGIN ----------
@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Принимает x-www-form-urlencoded: username, password
    Возвращает JWT.
    """
    user = db.scalar(select(User).where(User.username == form.username))
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": user.username, "role": user.role})
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current


# ---------- INVITES ----------
@router.post("/invites", response_model=InviteCreateOut, dependencies=[Depends(require_roles("super"))])
def create_invite(body: InviteCreateIn, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # генерим уникальный код
    code = secrets.token_urlsafe(20)

    expires_hours = body.expires_hours or 72
    expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_hours)

    inv = UserInvite(
        code=code,
        role=body.role,
        username=body.username.strip(),
        full_name=(body.full_name or "").strip() or None,
        store_id=body.store_id,
        network=(body.network or "").strip() or None,
        created_by=current.id,
        expires_at=expires_at,
    )
    db.add(inv)
    db.commit()
    return InviteCreateOut(code=code, username=inv.username, role=inv.role, expires_at=expires_at)


@router.get("/invites/{code}", response_model=InviteCheckOut)
def check_invite(code: str, db: Session = Depends(get_db)):
    inv = db.scalar(select(UserInvite).where(UserInvite.code == code))
    if not inv:
        return InviteCheckOut(valid=False, reason="not_found")

    if inv.used_at:
        return InviteCheckOut(valid=False, reason="used")

    if inv.expires_at <= datetime.now(timezone.utc):
        return InviteCheckOut(valid=False, reason="expired")

    return InviteCheckOut(
        valid=True,
        username=inv.username,
        role=inv.role, full_name=inv.full_name,
        store_id=inv.store_id, network=inv.network,
        expires_at=inv.expires_at,
    )


# ---------- REGISTER BY INVITE ----------
@router.post("/register", response_model=TokenOut)
def register_by_invite(body: RegisterByInviteIn, db: Session = Depends(get_db)):
    inv = db.scalar(select(UserInvite).where(UserInvite.code == body.code))
    if not inv:
        raise HTTPException(status_code=404, detail="Invite not found")

    if inv.used_at:
        raise HTTPException(status_code=400, detail="Invite already used")

    if inv.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invite expired")

    # username берем из инвайта, full_name — из body (если указали)
    username = inv.username
    full_name = (body.full_name or inv.full_name or "").strip() or None

    # проверяем, что пользователя еще нет
    exists = db.scalar(select(User).where(User.username == username))
    if exists:
        raise HTTPException(status_code=409, detail="User already exists")

    user = User(
        username=username,
        full_name=full_name,
        role=inv.role,
        password_hash=hash_password(body.password),
        is_active=True,
        store_id=inv.store_id,
        network=inv.network,
    )
    db.add(user)
    # помечаем инвайт использованным
    inv.used_at = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token({"sub": user.username, "role": user.role})
    return TokenOut(access_token=token)


# ---------- REFRESH ----------
@router.post("/refresh", response_model=TokenOut)
def refresh_token(current: User = Depends(get_current_user)):
    token = create_access_token({"sub": current.username, "role": current.role})
    return TokenOut(access_token=token)

# ---------- BACKWARD-COMPAT: /invites/register ----------
@router.post("/invites/register", response_model=TokenOut)
def register_by_invite_alias(body: RegisterByInviteIn, db: Session = Depends(get_db)):
    return register_by_invite(body=body, db=db)
