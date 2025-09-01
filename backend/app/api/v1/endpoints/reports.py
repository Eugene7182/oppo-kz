from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from fastapi.responses import StreamingResponse
import io, csv

router = APIRouter()

@router.get("/monthly")
async def monthly_report(month: str = Query(..., description="YYYY-MM"),
                         session: AsyncSession = Depends(get_session)):
    buf = io.StringIO(); w = csv.writer(buf)
    w.writerow(["Network","Store","Promoter","Plan","Fact","Achieved_%","Bonus"])
    w.writerow(["DemoNet","DemoStore","Ivan Petrov","100","120","120%","50000"])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue().encode("utf-8")]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=monthly_{month}.csv"})
