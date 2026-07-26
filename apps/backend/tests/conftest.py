import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_api_key, hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import app
from app.models import AdminUser, Device, Experiment


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        db.add(AdminUser(username="admin", password_hash=hash_password("admin")))
        db.add(Device(
            device_id="greenhouse-mega-01",
            name="Mega",
            api_key_hash=hash_api_key("test-key"),
        ))
        db.add(Experiment(external_id="experiment-001", name="Test"))
        db.commit()
    yield

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

@pytest.fixture
def payload():
    return {
        "device_id": "greenhouse-mega-01",
        "experiment_id": "experiment-001",
        "sample": 125,
        "timestamp": "2026-07-25T20:30:00+03:00",
        "uptime_ms": 380540,
        "thermocouples_c": [24.5, None, 25.0],
        "lux": 183.33,
        "dht22": {"temperature_c": 24.6, "humidity_percent": 51.8},
        "bme680": {
            "temperature_c": 25.16,
            "humidity_percent": 49.82,
            "pressure_hpa": 1012.64,
            "gas_resistance_kohm": 74.53,
        },
        "soil": {"raw": 650, "moisture_percent": 61},
    }
