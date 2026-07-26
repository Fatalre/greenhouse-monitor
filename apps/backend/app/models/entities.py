from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

class AdminUser(Base, TimestampMixin):
    __tablename__ = "admin_users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Device(Base, TimestampMixin):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    api_key_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

class Experiment(Base, TimestampMixin):
    __tablename__ = "experiments"
    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

class Measurement(Base):
    __tablename__ = "measurements"
    __table_args__ = (
        UniqueConstraint(
            "device_id", "sample", "experiment_id",
            name="uq_measurement_idempotency",
            postgresql_nulls_not_distinct=True,
        ),
        Index("ix_measurements_device_measured", "device_id", "measured_at"),
        Index("ix_measurements_experiment_measured", "experiment_id", "measured_at"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True)
    experiment_id: Mapped[int | None] = mapped_column(ForeignKey("experiments.id"), nullable=True, index=True)
    sample: Mapped[int] = mapped_column(Integer)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    timestamp_source: Mapped[str] = mapped_column(String(10))
    uptime_ms: Mapped[int | None] = mapped_column(Integer)
    lux: Mapped[float | None] = mapped_column(Float)
    dht22_temperature_c: Mapped[float | None] = mapped_column(Float)
    dht22_humidity_percent: Mapped[float | None] = mapped_column(Float)
    bme680_temperature_c: Mapped[float | None] = mapped_column(Float)
    bme680_humidity_percent: Mapped[float | None] = mapped_column(Float)
    bme680_pressure_hpa: Mapped[float | None] = mapped_column(Float)
    bme680_gas_resistance_kohm: Mapped[float | None] = mapped_column(Float)
    soil_raw: Mapped[int | None] = mapped_column(Integer)
    soil_moisture_percent: Mapped[float | None] = mapped_column(Float)
    raw_payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    thermocouples: Mapped[list["ThermocoupleMeasurement"]] = relationship(
        cascade="all, delete-orphan", lazy="selectin"
    )

class ThermocoupleMeasurement(Base):
    __tablename__ = "thermocouple_measurements"
    __table_args__ = (Index("ix_tc_measurement_sensor", "measurement_id", "sensor_number"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    measurement_id: Mapped[int] = mapped_column(
        ForeignKey("measurements.id", ondelete="CASCADE"), index=True
    )
    sensor_number: Mapped[int] = mapped_column(Integer, index=True)
    temperature_c: Mapped[float | None] = mapped_column(Float)
