from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Device, Experiment, Measurement, ThermocoupleMeasurement


class MeasurementRepository:
    def __init__(self, db: Session):
        self.db = db

    def existing(self, device_pk: int, sample: int, experiment_pk: int | None):
        query = select(Measurement).where(
            Measurement.device_id == device_pk,
            Measurement.sample == sample,
            Measurement.experiment_id.is_(None)
            if experiment_pk is None
            else Measurement.experiment_id == experiment_pk,
        )
        return self.db.scalar(query)

    def list(
        self, *, device_id=None, experiment_id=None, date_from=None, date_to=None,
        page=1, page_size=50, ordering="-measured_at", has_errors=None,
        min_temperature=None, max_temperature=None,
    ):
        query = select(Measurement).join(Device).outerjoin(Experiment)
        filters = []
        if device_id:
            filters.append(Device.device_id == device_id)
        if experiment_id:
            filters.append(Experiment.external_id == experiment_id)
        if date_from:
            filters.append(Measurement.measured_at >= date_from)
        if date_to:
            filters.append(Measurement.measured_at <= date_to)
        if has_errors is not None:
            null_exists = select(ThermocoupleMeasurement.id).where(
                ThermocoupleMeasurement.measurement_id == Measurement.id,
                ThermocoupleMeasurement.temperature_c.is_(None),
            ).exists()
            filters.append(null_exists if has_errors else ~null_exists)
        if min_temperature is not None:
            filters.append(select(ThermocoupleMeasurement.id).where(
                ThermocoupleMeasurement.measurement_id == Measurement.id,
                ThermocoupleMeasurement.temperature_c >= min_temperature,
            ).exists())
        if max_temperature is not None:
            filters.append(select(ThermocoupleMeasurement.id).where(
                ThermocoupleMeasurement.measurement_id == Measurement.id,
                ThermocoupleMeasurement.temperature_c <= max_temperature,
            ).exists())
        query = query.where(*filters)
        total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
        column = Measurement.measured_at if "measured_at" in ordering else Measurement.id
        query = query.order_by(
            column.desc() if ordering.startswith("-") else column.asc()
        ).offset((page - 1) * page_size).limit(page_size)
        return list(self.db.scalars(query).unique()), total
