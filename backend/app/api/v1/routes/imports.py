from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from .. import api  # type: ignore
from ....core.security import require_roles, get_current_user
import csv
from io import StringIO

router = APIRouter(prefix="/imports", tags=["imports"])

@router.post("/{kind}")
async def import_csv(kind: str, file: UploadFile = File(...), user=Depends(get_current_user)):
    # Only allow text/csv for now
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only .csv supported in this build")
    text = (await file.read()).decode("utf-8", errors="ignore")
    reader = csv.DictReader(StringIO(text))
    count = 0
    sample = None
    for row in reader:
        count += 1
        if sample is None:
            sample = row
    return {"kind": kind, "rows": count, "sample": sample}
