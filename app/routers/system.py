import time
from fastapi import APIRouter
from sqlalchemy import text
from app.database import SessionLocal

router = APIRouter(tags=["System"])

START_TIME = time.time()
REQUEST_COUNT = {"total": 0}

@router.get("/health")
def health_check():
    db_status = "ok"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception:
        db_status = "unreachable"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "uptime_seconds": round(time.time() - START_TIME, 2),
    }

@router.get("/metrics")
def metrics():
    return {
        "total_requests": REQUEST_COUNT["total"],
        "uptime_seconds": round(time.time() - START_TIME, 2),
    }