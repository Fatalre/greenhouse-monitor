from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.models import Device, Experiment, Measurement, ThermocoupleMeasurement
from app.repositories.measurements import MeasurementRepository
from app.schemas.measurement import MeasurementCreate


class InvalidDeviceKey(Exception):
    pass

class UnknownExperiment(Exception):
    pass

class MeasurementService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MeasurementRepository(db)

    def ingest(self, payload: MeasurementCreate, api_key: str):
        device = self.db.scalar(select(Device).where(Device.device_id == payload.device_id))
        if not device or not device.is_active or not verify_api_key(api_key, device.api_key_hash):
            raise InvalidDeviceKey

        experiment = None
        if payload.experiment_id:
            experiment = self.db.scalar(
                select(Experiment).where(Experiment.external_id == payload.experiment_id)
            )
            if not experiment:
                raise UnknownExperiment

        experiment_pk = experiment.id if experiment else None
        existing = self.repo.existing(device.id, payload.sample, experiment_pk)
        if existing:
            return existing, False

        received = datetime.now(UTC)
        measured = payload.timestamp or received
        measurement = Measurement(
            device_id=device.id,
            experiment_id=experiment_pk,
            sample=payload.sample,
            measured_at=measured,
            received_at=received,
            timestamp_source="device" if payload.timestamp else "server",
            uptime_ms=payload.uptime_ms,
            lux=payload.lux,
            dht22_temperature_c=payload.dht22.temperature_c if payload.dht22 else None,
            dht22_humidity_percent=payload.dht22.humidity_percent if payload.dht22 else None,
            bme680_temperature_c=payload.bme680.temperature_c if payload.bme680 else None,
            bme680_humidity_percent=payload.bme680.humidity_percent if payload.bme680 else None,
            bme680_pressure_hpa=payload.bme680.pressure_hpa if payload.bme680 else None,
            bme680_gas_resistance_kohm=payload.bme680.gas_resistance_kohm if payload.bme680 else None,
            soil_raw=payload.soil.raw if payload.soil else None,
            soil_moisture_percent=payload.soil.moisture_percent if payload.soil else None,
            raw_payload=payload.model_dump(mode="json"),
        )
        measurement.thermocouples = [
            ThermocoupleMeasurement(sensor_number=index + 1, temperature_c=value)
            for index, value in enumerate(payload.thermocouples_c)
        ]
        device.last_seen_at = received
        self.db.add(measurement)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            return self.repo.existing(device.id, payload.sample, experiment_pk), False
        self.db.refresh(measurement)
        return measurement, True
