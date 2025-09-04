import csv
import io
import threading
from typing import Callable

from app.db.session import SessionLocal
from app.services.jobs import mark_done, mark_error, mark_running, update_progress
from app.services.sales import import_sales_csv


def _with_db(fn: Callable):
    def wrapper(*args, **kwargs):
        db = SessionLocal()
        try:
            return fn(db, *args, **kwargs)
        finally:
            db.close()

    return wrapper


@_with_db
def run_sales_import_job(db, *, job_id: int, source: str, file_bytes: bytes):
    try:
        mark_running(db, job_id)
        text = file_bytes.decode("utf-8-sig")
        total = sum(1 for _ in csv.DictReader(io.StringIO(text)))
        if total == 0:
            update_progress(db, job_id, processed=0, total=0)
            mark_done(db, job_id)
            return
        processed = 0

        def progress_cb(done: int):
            nonlocal processed
            processed = done
            update_progress(db, job_id, processed=processed, total=total)

        res = import_sales_csv(
            db,
            file_bytes,
            source=source,
            dry_run=False,
            progress_cb=progress_cb,
        )
        if not res.get("ok"):
            mark_error(db, job_id, res.get("error") or "Import failed")
        else:
            update_progress(db, job_id, processed=total, total=total)
            mark_done(db, job_id)
    except Exception as e:
        mark_error(db, job_id, str(e))


def start_thread(target, **kwargs):
    th = threading.Thread(target=target, kwargs=kwargs, daemon=True)
    th.start()
    return th
