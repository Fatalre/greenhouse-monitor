from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_admin
from app.core.security import generate_api_key, hash_api_key
from app.db.session import get_db
from app.models import Device
from app.schemas.admin import DeviceCreate, DeviceCreated, DeviceRead, DeviceUpdate

router = APIRouter(prefix="/devices", tags=["devices"], dependencies=[Depends(current_admin)])

@router.get("", response_model=list[DeviceRead])
def list_devices(db: Session = Depends(get_db)):
    return list(db.scalars(select(Device).order_by(Device.id)))

@router.post("", response_model=DeviceCreated, status_code=201)
def create_device(data: DeviceCreate, db: Session = Depends(get_db)):
    key = generate_api_key()
    obj = Device(**data.model_dump(), api_key_hash=hash_api_key(key))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return DeviceCreated(**DeviceRead.model_validate(obj).model_dump(), api_key=key)

@router.get("/{item_id}", response_model=DeviceRead)
def get_device(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Device, item_id)
    if not obj:
        raise HTTPException(404, "Device not found")
    return obj

@router.patch("/{item_id}", response_model=DeviceRead)
def patch_device(item_id: int, data: DeviceUpdate, db: Session = Depends(get_db)):
    obj = db.get(Device, item_id)
    if not obj:
        raise HTTPException(404, "Device not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

@router.post("/{item_id}/rotate-key", response_model=DeviceCreated)
def rotate_key(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Device, item_id)
    if not obj:
        raise HTTPException(404, "Device not found")
    key = generate_api_key()
    obj.api_key_hash = hash_api_key(key)
    db.commit()
    db.refresh(obj)
    return DeviceCreated(**DeviceRead.model_validate(obj).model_dump(), api_key=key)

@router.delete("/{item_id}", status_code=204)
def delete_device(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Device, item_id)
    if not obj:
        raise HTTPException(404, "Device not found")
    db.delete(obj)
    db.commit()
