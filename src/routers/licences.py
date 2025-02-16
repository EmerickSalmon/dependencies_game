from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/licences",
    tags=["licences"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Licence)
def create_licence(licence: schemas.LicenceCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating licence with expiration date {licence.expiration_date}")
    return crud.create_licence(db=db, licence=licence)

@router.get("/{licence_id}", response_model=schemas.Licence)
def read_licence(licence_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching licence with ID {licence_id}")
    db_licence = crud.get_licence(db, licence_id=licence_id)
    if db_licence is None:
        logger.error(f"Licence with ID {licence_id} not found")
        raise HTTPException(status_code=404, detail="Licence not found")
    return db_licence

@router.get("/", response_model=list[schemas.Licence])
def read_licences(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    logger.info(f"Fetching licences with skip={skip} and limit={limit}")
    licences = crud.get_licences(db, skip=skip, limit=limit)
    return licences

@router.put("/{licence_id}/status", response_model=schemas.Licence)
async def update_licence_status(licence_id: int, status: bool, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    logger.info(f"Updating licence status for ID {licence_id} to {status}")
    db_licence = crud.get_licence(db, licence_id=licence_id)
    if db_licence is None:
        logger.error(f"Licence with ID {licence_id} not found")
        raise HTTPException(status_code=404, detail="Licence not found")
    db_licence.isHealthy = status
    db_licence.check_status()
    db.commit()
    db.refresh(db_licence)
    if not status:
        background_tasks.add_task(crud.update_robots_health_status, db)
    return db_licence
