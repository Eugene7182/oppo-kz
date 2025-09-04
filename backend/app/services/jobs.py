
from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.models.job import ImportJob

def create_job(db: Session, *, type: str, filename: str, payload: bytes | None = None, mime: str | None = None) -> ImportJob:
    job = ImportJob(type=type, filename=filename, status="queued", progress=0, total=0, processed=0, error=None,
                    created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
                    payload=payload, mime=mime)
    db.add(job); db.flush(); return job

def get_job(db: Session, job_id: int) -> ImportJob | None:
    return db.get(ImportJob, job_id)

def list_jobs(db: Session, *, status: str | None = None, type: str | None = None, limit: int = 50, offset: int = 0):
    q = select(ImportJob).order_by(desc(ImportJob.created_at)).limit(limit).offset(offset)
    if status: q = q.where(ImportJob.status == status)
    if type: q = q.where(ImportJob.type == type)
    return db.execute(q).scalars().all()

def update_progress(db: Session, job_id: int, *, processed: int, total: int):
    job = db.get(ImportJob, job_id); 
    if not job: return
    job.processed = processed; job.total = total
    job.progress = int((processed/total)*100) if total>0 else 0
    job.updated_at = datetime.now(timezone.utc)

def mark_running(db: Session, job_id: int):
    job = db.get(ImportJob, job_id); 
    if job: job.status="running"; job.updated_at = datetime.now(timezone.utc)

def mark_done(db: Session, job_id: int):
    job = db.get(ImportJob, job_id); 
    if job: job.status="done"; job.progress=100; job.updated_at = datetime.now(timezone.utc)

def mark_error(db: Session, job_id: int, error: str):
    job = db.get(ImportJob, job_id); 
    if job: job.status="error"; job.error=error[:2000]; job.updated_at = datetime.now(timezone.utc)
