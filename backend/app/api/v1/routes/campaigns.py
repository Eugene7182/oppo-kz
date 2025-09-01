from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
import json as pyjson
from ....core.security import get_db, get_current_user, require_roles
from ....models import Campaign
from ....schemas import CampaignIn, CampaignOut
from typing import List

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

def _to_out(c: Campaign) -> CampaignOut:
    stores = pyjson.loads(c.stores_json) if c.stores_json else None
    skus = pyjson.loads(c.skus_json) if c.skus_json else None
    mech = pyjson.loads(c.mechanics_json) if c.mechanics_json else None
    return CampaignOut(id=c.id, name=c.name, start=c.start, end=c.end, note=c.note, stores=stores, skus=skus, mechanics=mech)

@router.get("/", response_model=List[CampaignOut])
def list_campaigns(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [_to_out(c) for c in db.scalars(select(Campaign).order_by(Campaign.start.desc())).all()]

@router.post("/", response_model=CampaignOut, dependencies=[Depends(require_roles("super"))])
def create_campaign(body: CampaignIn, db: Session = Depends(get_db)):
    c = Campaign(name=body.name, start=body.start, end=body.end, note=body.note,
                 stores_json=pyjson.dumps(body.stores) if body.stores is not None else None,
                 skus_json=pyjson.dumps(body.skus) if body.skus is not None else None,
                 mechanics_json=pyjson.dumps(body.mechanics) if body.mechanics is not None else None)
    db.add(c); db.commit(); db.refresh(c)
    return _to_out(c)


@router.get("/{cid}", response_model=CampaignOut)
def get_campaign(cid: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    c = db.get(Campaign, cid)
    if not c: raise HTTPException(status_code=404, detail="Not found")
    return _to_out(c)
