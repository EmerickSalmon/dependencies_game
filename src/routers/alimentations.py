from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/alimentations",
    tags=["alimentations"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Alimentation)
def create_alimentation(alimentation: schemas.AlimentationCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating alimentation with type {alimentation.alimentationType}")
    return crud.create_alimentation(db=db, alimentation=alimentation)

@router.get("/{alimentation_id}", response_model=schemas.Alimentation)
def read_alimentation(alimentation_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching alimentation with ID {alimentation_id}")
    db_alimentation = crud.get_alimentation(db, alimentation_id=alimentation_id)
    if db_alimentation is None:
        logger.error(f"Alimentation with ID {alimentation_id} not found")
        raise HTTPException(status_code=404, detail="Alimentation not found")
    return db_alimentation

@router.get("/", response_model=list[schemas.Alimentation])
def read_alimentations(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    logger.info(f"Fetching alimentations with skip={skip} and limit={limit}")
    alimentations = crud.get_alimentations(db, skip=skip, limit=limit)
    return alimentations

@router.put("/{alimentation_id}/status", response_model=schemas.Alimentation)
async def update_alimentation_status(alimentation_id: int, status: bool, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    logger.info(f"Updating alimentation status for ID {alimentation_id} to {status}")
    db_alimentation = crud.get_alimentation(db, alimentation_id=alimentation_id)
    if db_alimentation is None:
        logger.error(f"Alimentation with ID {alimentation_id} not found")
        raise HTTPException(status_code=404, detail="Alimentation not found")
    db_alimentation.isHealthy = status
    db.commit()
    db.refresh(db_alimentation)
    if not status:
        background_tasks.add_task(crud.update_robots_health_status, db)
    return db_alimentation
