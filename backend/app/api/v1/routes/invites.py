"""Invite endpoints with RBAC rules."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.authz import require_roles
from app.core.security import get_db, get_password_hash
from app.models.invite import Invite, InviteScopeType, InviteStatus, default_expiry, secrets_token
from app.models.store import Store
from app.models.user import User, UserRole, UserStatus
from app.schemas.invite import InviteAccept, InviteCreate, InviteList, InviteOut, InviteTokenView

router = APIRouter(prefix="/invites", tags=["invites"])


@router.post("", response_model=InviteOut, status_code=status.HTTP_201_CREATED)
def create_invite(
    payload: InviteCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles([UserRole.admin, UserRole.office, UserRole.supervisor])),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> Invite:
    """Создаёт или возвращает существующий инвайт."""

    existing_user = db.query(User).filter(User.email == payload.email).one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    # Supervisor guard rails
    if current.role == UserRole.supervisor:
        if payload.role_requested != "promoter":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Supervisor may invite only promoter")
        if not current.region_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supervisor must be attached to region")
        scope_type = payload.scope_type or InviteScopeType.region
        scope_id = payload.scope_id or current.region_id
        if scope_type == InviteScopeType.region and scope_id != current.region_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invite must stay in supervisor region")
        if scope_type == InviteScopeType.store:
            store = db.query(Store).filter(Store.id == scope_id).one_or_none()
            if not store or store.region_id != current.region_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Store outside supervisor region")
        if scope_type == InviteScopeType.country:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Supervisor cannot invite for country scope")
        payload = payload.copy(update={"scope_type": scope_type, "scope_id": scope_id})
    else:
        # Office role cannot invite admins unless explicit feature toggle (not implemented -> forbid)
        if current.role == UserRole.office and payload.role_requested == "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Office cannot invite admin")

    # Idempotency by email (and optional header if provided)
    query = db.query(Invite).filter(Invite.email == payload.email, Invite.status == InviteStatus.pending)
    if idempotency_key:
        query = query.filter(Invite.token == idempotency_key)
    invite = query.one_or_none()
    if invite:
        invite.mark_expired()
        db.commit()
        db.refresh(invite)
        if invite.status == InviteStatus.pending:
            return invite

    # reuse header token if provided else generate
    token = idempotency_key or secrets_token()
    invite = Invite(
        email=payload.email,
        role_requested=payload.role_requested,
        scope_type=payload.scope_type,
        scope_id=payload.scope_id,
        token=token,
        invited_by=current.id,
        expires_at=default_expiry(payload.ttl_hours),
        status=InviteStatus.pending,
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


@router.get("", response_model=InviteList)
def list_invites(
    status_filter: InviteStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles([UserRole.admin, UserRole.office, UserRole.supervisor])),
) -> InviteList:
    """Возвращает список приглашений с фильтрацией по статусу."""

    query = db.query(Invite)
    if status_filter:
        query = query.filter(Invite.status == status_filter)
    invites = query.order_by(Invite.created_at.desc()).all()
    return InviteList(items=invites)


@router.post("/{invite_id}/revoke", response_model=InviteOut)
def revoke_invite(
    invite_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles([UserRole.admin, UserRole.office])),
) -> Invite:
    """Отзывает незавершённый инвайт."""

    invite = db.query(Invite).filter(Invite.id == invite_id).one_or_none()
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
    invite.mark_expired()
    if invite.status not in {InviteStatus.pending, InviteStatus.expired}:
        return invite
    invite.status = InviteStatus.revoked
    invite.updated_at = datetime.now(timezone.utc)
    invite.invited_by = current.id
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


@router.get("/{token}", response_model=InviteTokenView)
def check_invite(token: str, db: Session = Depends(get_db)) -> InviteTokenView:
    """Проверяет статус инвайта по токену."""

    invite = db.query(Invite).filter(Invite.token == token).one_or_none()
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
    invite.mark_expired()
    db.commit()
    expired = invite.status != InviteStatus.pending or datetime.now(timezone.utc) >= invite.expires_at
    return InviteTokenView(
        email=invite.email,
        role_requested=invite.role_requested,
        scope_type=invite.scope_type,
        scope_id=invite.scope_id,
        status=invite.status,
        expires_at=invite.expires_at,
        expired=expired,
    )


@router.post("/{token}/accept", response_model=InviteOut)
def accept_invite(
    token: str,
    payload: InviteAccept,
    db: Session = Depends(get_db),
) -> Invite:
    """Регистрирует пользователя и закрывает инвайт."""

    invite = db.query(Invite).filter(Invite.token == token).one_or_none()
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")
    invite.mark_expired()
    if invite.status != InviteStatus.pending:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Invite {invite.status.value}")
    if datetime.now(timezone.utc) >= invite.expires_at:
        invite.status = InviteStatus.expired
        db.commit()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invite expired")

    if db.query(User).filter(User.email == invite.email).first():
        invite.status = InviteStatus.accepted
        db.commit()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already registered")

    region_id = None
    if invite.scope_type == InviteScopeType.region:
        region_id = invite.scope_id
    elif invite.scope_type == InviteScopeType.store and invite.scope_id:
        store = db.query(Store).filter(Store.id == invite.scope_id).one_or_none()
        region_id = store.region_id if store else None

    new_user = User(
        email=invite.email,
        full_name=payload.full_name,
        role=UserRole(invite.role_requested),
        hashed_password=get_password_hash(payload.password),
        region_id=region_id,
        status=UserStatus.active,
    )
    db.add(new_user)
    invite.status = InviteStatus.accepted
    invite.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(invite)
    return invite
