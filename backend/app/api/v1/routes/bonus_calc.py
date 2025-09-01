from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ....core.security import get_db, get_current_user, require_roles
from ....schemas import BonusCalcPreviewIn, BonusCalcPreviewOut, BonusCommitIn, BonusCalcItem, BonusPayoutOut
from ....models import BonusPayout
from ....db import to_float

router = APIRouter(prefix="/bonus", tags=["bonus"])

@router.post("/calc-preview", response_model=BonusCalcPreviewOut)
def calc_preview(body: BonusCalcPreviewIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Minimal working preview:
    # If sales provided inline -> sum qty*100 by promoter; else total=0.
    total = 0.0
    by = {}
    sales = body.sales or []
    for s in sales:
        promoter = str(s.get("promoter") or s.get("promoter_username") or "unknown")
        qty = float(s.get("qty") or 0)
        unit_bonus = float(s.get("unit_bonus") or 100.0)  # default flat
        amt = qty * unit_bonus
        total += amt
        by[promoter] = by.get(promoter, 0.0) + amt
    return BonusCalcPreviewOut(total=total, by_promoter=[BonusCalcItem(promoter=k, amount=v) for k,v in by.items()])

@router.post("/calc-commit", response_model=List[BonusPayoutOut], dependencies=[Depends(require_roles("super"))])
def calc_commit(body: BonusCommitIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    out = []
    for item in body.by_promoter:
        p = BonusPayout(period_from=body.period_from, period_to=body.period_to,
                        promoter_username=item.promoter, amount=item.amount)
        db.add(p)
        db.flush()
        out.append(p)
    db.commit()
    return out
