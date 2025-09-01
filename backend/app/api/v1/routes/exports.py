from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from ....core.security import get_current_user
from io import StringIO
import csv
from datetime import date

router = APIRouter(prefix="/exports", tags=["exports"])

TEMPLATES = {
    "skus": ["code","name","category","uom"],
    "stores": ["code","name","region","city"],
    "pricelist": ["sku_code","price","valid_from","valid_to"],
    "sales": ["store_code","sku_code","qty","sold_at","promoter"],
}

@router.get("/templates/{kind}.csv")
def template_csv(kind: str, user=Depends(get_current_user)):
    cols = TEMPLATES.get(kind)
    if not cols:
        cols = ["code","name"]
    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=cols)
    writer.writeheader()
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename={kind}_template_{date.today().isoformat()}.csv"
    })
