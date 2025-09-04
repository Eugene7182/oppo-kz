
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.v1.deps import get_db, require_roles
from app.services.jobs import create_job, get_job, list_jobs
from app.worker.background import start_thread, run_sales_import_job

router = APIRouter(prefix="/imports", tags=["imports"])

@router.post("/sales/{source}")
def start_sales_import(source: str, file: UploadFile = File(...), db: Session = Depends(get_db), _=Depends(require_roles("admin","office"))):
    if source not in ("network","promoters"):
        raise HTTPException(400, "source must be network|promoters")
    data = file.file.read()
    job = create_job(db, type=f"sales_{source}", filename=(file.filename or "upload.csv"), payload=data, mime=(file.content_type or "text/csv"))
    start_thread(run_sales_import_job, job_id=job.id, source=source, file_bytes=data)
    return {"job_id": job.id, "status": "queued"}

@router.get("")
def list_(status: str | None = Query(None), type: str | None = Query(None), limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0),
          db: Session = Depends(get_db), _=Depends(require_roles("admin","office","supervisor"))):
    rows = list_jobs(db, status=status, type=type, limit=limit, offset=offset)
    return {"items": [dict(id=r.id, type=r.type, filename=r.filename, status=r.status, progress=r.progress, processed=r.processed, total=r.total, error=r.error, created_at=str(r.created_at), updated_at=str(r.updated_at), has_payload=bool(r.payload)) for r in rows]}

@router.get("/{job_id}")
def job_status(job_id: int, db: Session = Depends(get_db), _=Depends(require_roles("admin","office","supervisor"))):
    r = get_job(db, job_id)
    if not r: raise HTTPException(404, "job not found")
    return dict(id=r.id, type=r.type, filename=r.filename, status=r.status, progress=r.progress, processed=r.processed, total=r.total, error=r.error, created_at=str(r.created_at), updated_at=str(r.updated_at), has_payload=bool(r.payload))

@router.post("/{job_id}/retry")
def retry(job_id: int, db: Session = Depends(get_db), _=Depends(require_roles("admin","office"))):
    orig = get_job(db, job_id)
    if not orig: raise HTTPException(404, "job not found")
    if not orig.payload: raise HTTPException(400, "no payload to retry")
    if not orig.type.startswith("sales_"):
        raise HTTPException(400, "retry supported only for sales imports")
    source = orig.type.split("_",1)[1]
    new_job = create_job(db, type=orig.type, filename=orig.filename, payload=orig.payload, mime=orig.mime)
    start_thread(run_sales_import_job, job_id=new_job.id, source=source, file_bytes=orig.payload)
    return {"job_id": new_job.id, "status": "queued"}
