from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class DeviceCreate(BaseModel):
    device_id: str = Field(max_length=120)
    name: str
    description: str | None = None

class DeviceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None

class DeviceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    device_id: str
    name: str
    description: str | None
    is_active: bool
    last_seen_at: datetime | None
    created_at: datetime

class DeviceCreated(DeviceRead):
    api_key: str

class ExperimentCreate(BaseModel):
    external_id: str
    name: str
    description: str | None = None

class ExperimentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class ExperimentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    external_id: str
    name: str
    description: str | None
    started_at: datetime | None
    finished_at: datetime | None
    is_active: bool
    created_at: datetime
