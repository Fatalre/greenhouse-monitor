from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.api.deps import current_admin
from app.core.config import settings
from app.db.session import get_db
from app.models import Device, Measurement
from app.websocket.manager import manager

router = APIRouter(tags=["system"])

@router.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "version": settings.app_version}

@router.get("/system/status", dependencies=[Depends(current_admin)])
def system_status(db: Session = Depends(get_db)):
    now = datetime.now(UTC)
    last = db.scalar(select(func.max(Measurement.received_at)))
    count = db.scalar(select(func.count(Measurement.id))) or 0
    devices = []
    for device in db.scalars(select(Device)):
        online = bool(
            device.last_seen_at
            and (now - device.last_seen_at).total_seconds()
            <= settings.device_offline_threshold_seconds
        )
        devices.append({
            "device_id": device.device_id,
            "online": online,
            "last_seen_at": device.last_seen_at,
        })
    size = None
    if not settings.database_url.startswith("sqlite"):
        size = db.scalar(text("SELECT pg_database_size(current_database())"))
    return {
        "backend": "ok",
        "database": "ok",
        "last_measurement_at": last,
        "measurement_count": count,
        "database_size_bytes": size,
        "websocket_clients": len(manager.connections),
        "devices": devices,
        "version": settings.app_version,
    }
