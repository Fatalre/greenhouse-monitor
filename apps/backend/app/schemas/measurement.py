from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class DHT22(BaseModel):
    temperature_c: float | None = None
    humidity_percent: float | None = None

class BME680(BaseModel):
    temperature_c: float | None = None
    humidity_percent: float | None = None
    pressure_hpa: float | None = None
    gas_resistance_kohm: float | None = None

class Soil(BaseModel):
    raw: int | None = None
    moisture_percent: float | None = None

class MeasurementCreate(BaseModel):
    device_id: str = Field(min_length=1, max_length=120)
    experiment_id: str | None = None
    sample: int = Field(ge=0)
    timestamp: datetime | None = None
    uptime_ms: int | None = Field(default=None, ge=0)
    thermocouples_c: list[float | None] = Field(default_factory=list, max_length=18)
    lux: float | None = None
    dht22: DHT22 | None = None
    bme680: BME680 | None = None
    soil: Soil | None = None

    @field_validator("thermocouples_c")
    @classmethod
    def pad_thermocouples(cls, value: list[float | None]) -> list[float | None]:
        if len(value) > 18:
            raise ValueError("thermocouples_c must contain at most 18 values")
        return value + [None] * (18 - len(value))

class MeasurementCompactResponse(BaseModel):
    ok: bool = True
    created: bool
    measurement_id: int
    received_at: datetime
