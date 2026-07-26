from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import current_admin
from app.db.session import get_db
from app.models import Experiment
from app.schemas.admin import ExperimentCreate, ExperimentRead, ExperimentUpdate

router = APIRouter(
    prefix="/experiments", tags=["experiments"], dependencies=[Depends(current_admin)]
)


@router.get("", response_model=list[ExperimentRead])
def list_experiments(db: Session = Depends(get_db)):
    return list(db.scalars(select(Experiment).order_by(Experiment.created_at.desc())))


@router.post("", response_model=ExperimentRead, status_code=201)
def create_experiment(
    data: ExperimentCreate,
    db: Session = Depends(get_db),
):
    existing = db.scalar(
        select(Experiment).where(Experiment.external_id == data.external_id)
    )

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Experiment with this external_id already exists",
        )

    obj = Experiment(**data.model_dump())
    db.add(obj)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Experiment with this external_id already exists",
        ) from None

    db.refresh(obj)
    return obj


@router.get("/{item_id}", response_model=ExperimentRead)
def get_experiment(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Experiment, item_id)
    if not obj:
        raise HTTPException(404, "Experiment not found")
    return obj


@router.patch("/{item_id}", response_model=ExperimentRead)
def patch_experiment(
    item_id: int, data: ExperimentUpdate, db: Session = Depends(get_db)
):
    obj = db.get(Experiment, item_id)
    if not obj:
        raise HTTPException(404, "Experiment not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/{item_id}/start", response_model=ExperimentRead)
def start_experiment(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Experiment, item_id)
    if not obj:
        raise HTTPException(404, "Experiment not found")
    now = datetime.now(UTC)
    db.execute(
        update(Experiment)
        .where(Experiment.is_active.is_(True))
        .values(is_active=False, finished_at=now)
    )
    obj.is_active = True
    obj.started_at = now
    obj.finished_at = None
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/{item_id}/finish", response_model=ExperimentRead)
def finish_experiment(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Experiment, item_id)
    if not obj:
        raise HTTPException(404, "Experiment not found")
    obj.is_active = False
    obj.finished_at = datetime.now(UTC)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{item_id}", status_code=204)
def delete_experiment(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Experiment, item_id)
    if not obj:
        raise HTTPException(404, "Experiment not found")
    db.delete(obj)
    db.commit()
