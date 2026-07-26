import csv
import io
import math
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import current_admin, device_api_key
from app.db.session import get_db
from app.models import Device, Experiment, Measurement
from app.repositories.measurements import MeasurementRepository
from app.schemas.measurement import MeasurementCompactResponse, MeasurementCreate
from app.services.measurements import (
    InvalidDeviceKey,
    MeasurementService,
    UnknownExperiment,
)
from app.websocket.manager import manager

router = APIRouter(prefix="/measurements", tags=["measurements"])


def serialize(measurement: Measurement, db: Session) -> dict:
    device = db.get(Device, measurement.device_id)

    if device is None:
        raise HTTPException(
            status_code=500,
            detail="Measurement references a missing device",
        )

    experiment = (
        db.get(Experiment, measurement.experiment_id)
        if measurement.experiment_id
        else None
    )

    tc: list[float | None] = [None] * 18

    for item in measurement.thermocouples:
        tc[item.sensor_number - 1] = item.temperature_c

    return {
        "id": measurement.id,
        "device_id": device.device_id,
        "experiment_id": experiment.external_id if experiment else None,
        "sample": measurement.sample,
        "measured_at": measurement.measured_at,
        "received_at": measurement.received_at,
        "timestamp_source": measurement.timestamp_source,
        "uptime_ms": measurement.uptime_ms,
        "thermocouples_c": tc,
        "lux": measurement.lux,
        "dht22": {
            "temperature_c": measurement.dht22_temperature_c,
            "humidity_percent": measurement.dht22_humidity_percent,
        },
        "bme680": {
            "temperature_c": measurement.bme680_temperature_c,
            "humidity_percent": measurement.bme680_humidity_percent,
            "pressure_hpa": measurement.bme680_pressure_hpa,
            "gas_resistance_kohm": measurement.bme680_gas_resistance_kohm,
        },
        "soil": {
            "raw": measurement.soil_raw,
            "moisture_percent": measurement.soil_moisture_percent,
        },
    }


@router.post("", response_model=MeasurementCompactResponse)
async def ingest(
    payload: MeasurementCreate,
    response: Response,
    key: str = Depends(device_api_key),
    db: Session = Depends(get_db),
):
    try:
        measurement, created = MeasurementService(db).ingest(payload, key)
    except InvalidDeviceKey:
        raise HTTPException(401, "Invalid device or API key") from None
    except UnknownExperiment:
        raise HTTPException(422, "Unknown experiment_id") from None
    if measurement is None:
        raise HTTPException(503, "Could not persist measurement")
    response.status_code = 201 if created else 200
    if created:
        await manager.broadcast(
            {
                "type": "measurement.created",
                "data": serialize(measurement, db),
            }
        )
    return MeasurementCompactResponse(
        created=created,
        measurement_id=measurement.id,
        received_at=measurement.received_at,
    )


@router.get("/latest", dependencies=[Depends(current_admin)])
def latest(device_id: str | None = None, db: Session = Depends(get_db)):
    query = (
        select(Measurement)
        .options(selectinload(Measurement.thermocouples))
        .join(Device)
    )
    if device_id:
        query = query.where(Device.device_id == device_id)
    measurement = db.scalar(query.order_by(Measurement.measured_at.desc()).limit(1))
    if not measurement:
        raise HTTPException(404, "No measurements")
    return serialize(measurement, db)


@router.get("/chart", dependencies=[Depends(current_admin)])
def chart(
    device_id: str | None = None,
    experiment_id: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    metrics: str = "TC1,lux",
    interval: str = "raw",
    aggregation: str = "average",
    db: Session = Depends(get_db),
):
    # Raw data is capped. For non-raw intervals PostgreSQL date_bin aggregation
    # can be added without changing the API contract.
    items, _ = MeasurementRepository(db).list(
        device_id=device_id,
        experiment_id=experiment_id,
        date_from=date_from,
        date_to=date_to,
        page=1,
        page_size=5000,
        ordering="measured_at",
    )
    return {
        "interval": interval,
        "aggregation": aggregation,
        "metrics": metrics.split(","),
        "items": [serialize(item, db) for item in items],
    }


def export_items(db: Session, **filters):
    items, _ = MeasurementRepository(db).list(
        page=1, page_size=100000, ordering="measured_at", **filters
    )
    return items


@router.get("/export.csv", dependencies=[Depends(current_admin)])
def export_csv(
    device_id: str | None = None,
    experiment_id: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: Session = Depends(get_db),
):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "measured_at",
            "device_id",
            "experiment_id",
            "sample",
            *[f"TC{i}" for i in range(1, 19)],
            "lux",
            "dht22_temperature_c",
            "dht22_humidity_percent",
            "bme680_temperature_c",
            "bme680_humidity_percent",
            "bme680_pressure_hpa",
            "bme680_gas_resistance_kohm",
            "soil_raw",
            "soil_moisture_percent",
        ]
    )
    for item in export_items(
        db,
        device_id=device_id,
        experiment_id=experiment_id,
        date_from=date_from,
        date_to=date_to,
    ):
        data = serialize(item, db)
        writer.writerow(
            [
                data["measured_at"].isoformat(),
                data["device_id"],
                data["experiment_id"],
                data["sample"],
                *data["thermocouples_c"],
                data["lux"],
                data["dht22"]["temperature_c"],
                data["dht22"]["humidity_percent"],
                data["bme680"]["temperature_c"],
                data["bme680"]["humidity_percent"],
                data["bme680"]["pressure_hpa"],
                data["bme680"]["gas_resistance_kohm"],
                data["soil"]["raw"],
                data["soil"]["moisture_percent"],
            ]
        )
    return Response(
        output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=measurements.csv"},
    )


@router.get("/export.json", dependencies=[Depends(current_admin)])
def export_json(
    device_id: str | None = None,
    experiment_id: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: Session = Depends(get_db),
):
    return [
        serialize(item, db)
        for item in export_items(
            db,
            device_id=device_id,
            experiment_id=experiment_id,
            date_from=date_from,
            date_to=date_to,
        )
    ]


@router.get("", dependencies=[Depends(current_admin)])
def list_measurements(
    device_id: str | None = None,
    experiment_id: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    ordering: str = "-measured_at",
    has_errors: bool | None = None,
    min_temperature: float | None = None,
    max_temperature: float | None = None,
    db: Session = Depends(get_db),
):
    items, total = MeasurementRepository(db).list(
        device_id=device_id,
        experiment_id=experiment_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
        ordering=ordering,
        has_errors=has_errors,
        min_temperature=min_temperature,
        max_temperature=max_temperature,
    )
    return {
        "items": [serialize(item, db) for item in items],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": math.ceil(total / page_size) if total else 0,
    }


@router.get("/{item_id}", dependencies=[Depends(current_admin)])
def measurement_details(item_id: int, db: Session = Depends(get_db)):
    measurement = db.scalar(
        select(Measurement)
        .options(selectinload(Measurement.thermocouples))
        .where(Measurement.id == item_id)
    )
    if not measurement:
        raise HTTPException(404, "Measurement not found")
    data = serialize(measurement, db)
    data["raw_payload"] = measurement.raw_payload
    data["latency_ms"] = (
        measurement.received_at - measurement.measured_at
    ).total_seconds() * 1000
    return data
