from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/guidages",
    tags=["guidages"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Guidage)
def create_guidage(guidage: schemas.GuidageCreate, db: Session = Depends(get_db)):
    logger.info("Creating guidage")
    return crud.create_guidage(db=db, guidage=guidage)

@router.get("/{guidage_id}", response_model=schemas.Guidage)
def read_guidage(guidage_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching guidage with ID {guidage_id}")
    db_guidage = crud.get_guidage(db, guidage_id=guidage_id)
    if db_guidage is None:
        logger.error(f"Guidage with ID {guidage_id} not found")
        raise HTTPException(status_code=404, detail="Guidage not found")
    return db_guidage

@router.get("/", response_model=list[schemas.Guidage])
def read_guidages(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    logger.info(f"Fetching guidages with skip={skip} and limit={limit}")
    guidages = crud.get_guidages(db, skip=skip, limit=limit)
    return guidages

@router.put("/{guidage_id}/status", response_model=schemas.Guidage)
async def update_guidage_status(guidage_id: int, status: bool, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    logger.info(f"Updating guidage status for ID {guidage_id} to {status}")
    db_guidage = crud.get_guidage(db, guidage_id=guidage_id)
    if db_guidage is None:
        logger.error(f"Guidage with ID {guidage_id} not found")
        raise HTTPException(status_code=404, detail="Guidage not found")
    db_guidage.isHealthy = status
    db.commit()
    db.refresh(db_guidage)
    if not status:
        background_tasks.add_task(crud.update_robots_health_status, db)
    return db_guidage
