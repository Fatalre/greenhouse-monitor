import argparse
from datetime import UTC, datetime

from sqlalchemy import select

from app.core.config import settings
from app.core.security import generate_api_key, hash_api_key, hash_password
from app.db.session import SessionLocal
from app.models import AdminUser, Device, Experiment


def create_admin(username: str | None = None, password: str | None = None) -> None:
    username = username or settings.admin_username
    password = password or settings.admin_password
    with SessionLocal() as db:
        obj = db.scalar(select(AdminUser).where(AdminUser.username == username))
        if obj:
            obj.password_hash = hash_password(password)
        else:
            db.add(AdminUser(username=username, password_hash=hash_password(password)))
        db.commit()
        print(f"Administrator '{username}' created/updated")

def seed() -> None:
    with SessionLocal() as db:
        if not db.scalar(select(Device).where(Device.device_id == "greenhouse-mega-01")):
            key = generate_api_key()
            db.add(Device(
                device_id="greenhouse-mega-01",
                name="Greenhouse Mega 01",
                api_key_hash=hash_api_key(key),
            ))
            print("Demo device API key:", key)
        if not db.scalar(select(Experiment).where(
            Experiment.external_id == "experiment-001"
        )):
            db.add(Experiment(
                external_id="experiment-001",
                name="Демонстрационный эксперимент",
                is_active=True,
                started_at=datetime.now(UTC),
            ))
        db.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["create-admin", "seed"])
    parser.add_argument("--username")
    parser.add_argument("--password")
    args = parser.parse_args()
    if args.command == "create-admin":
        create_admin(args.username, args.password)
    else:
        seed()
