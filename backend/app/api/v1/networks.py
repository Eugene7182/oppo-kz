"""Network endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import get_current_user, rbac_required
from app.db.session import get_db
from app.models.network import Network
from app.models.user import UserRole
from app.schemas.network import NetworkCreate, NetworkRead, NetworkUpdate

router = APIRouter(prefix="/networks", tags=["networks"])


@router.get("", dependencies=[Depends(get_current_user)], response_model=dict)
def list_networks(
    limit: int = 100,
    offset: int = 0,
    q: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    """Список сетей с фильтром по имени."""
    stmt = select(Network)
    if q:
        stmt = stmt.where(Network.name.ilike(f"%{q}%"))
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.order_by(Network.name).offset(offset).limit(limit)).all()
    items = [NetworkRead.model_validate(r) for r in rows]
    return {"items": items, "total": total}


_admin_office = rbac_required([UserRole.admin, UserRole.office])


@router.post("", dependencies=[Depends(_admin_office)], response_model=NetworkRead, status_code=status.HTTP_201_CREATED)
def create_network(data: NetworkCreate, db: Session = Depends(get_db)) -> Network:
    """Создать сеть."""
    exists = db.scalar(select(Network).where(Network.name == data.name))
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"detail": "Network already exists", "code": "network_exists"},
        )
    network = Network(name=data.name)
    db.add(network)
    db.commit()
    db.refresh(network)
    return network


@router.put("/{network_id}", dependencies=[Depends(_admin_office)], response_model=NetworkRead)
def update_network(network_id: str, data: NetworkUpdate, db: Session = Depends(get_db)) -> Network:
    """Обновить сеть."""
    network = db.get(Network, network_id)
    if not network:
        raise HTTPException(status_code=404, detail={"detail": "Network not found", "code": "network_not_found"})
    if data.name != network.name:
        exists = db.scalar(select(Network).where(Network.name == data.name, Network.id != network_id))
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"detail": "Network already exists", "code": "network_exists"},
            )
        network.name = data.name
    db.add(network)
    db.commit()
    db.refresh(network)
    return network


@router.delete("/{network_id}", dependencies=[Depends(_admin_office)], response_model=NetworkRead)
def delete_network(network_id: str, db: Session = Depends(get_db)) -> Network:
    """Удалить сеть."""
    network = db.get(Network, network_id)
    if not network:
        raise HTTPException(status_code=404, detail={"detail": "Network not found", "code": "network_not_found"})
    db.delete(network)
    db.commit()
    return network


__all__ = ["router"]
