from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
from .. import crud
from .. import models, schemas
from ..database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/robots",
    tags=["robots"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Robot)
def create_robot(robot: schemas.RobotCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating robot with name {robot.name}")
    return crud.create_robot(db=db, robot=robot)

@router.get("/{robot_id}", response_model=schemas.Robot)
def read_robot(robot_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching robot with ID {robot_id}")
    db_robot = crud.get_robot(db, robot_id=robot_id)
    if db_robot is None:
        logger.error(f"Robot with ID {robot_id} not found")
        raise HTTPException(status_code=404, detail="Robot not found")
    return db_robot

@router.get("/", response_model=List[schemas.Robot])
def read_robots(
    skip: int = 0,
    limit: int = 10,
    isHealthy: Optional[bool] = None,
    alimentation_id: Optional[int] = None,
    guidage_id: Optional[int] = None,
    licence_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    logger.info("Fetching robots with filters")
    query = db.query(models.Robot)
    if isHealthy is not None:
        query = query.filter(models.Robot.isHealthy == isHealthy)
    if alimentation_id is not None:
        query = query.filter(models.Robot.alimentation_id == alimentation_id)
    if guidage_id is not None:
        query = query.filter(models.Robot.guidage_id == guidage_id)
    if licence_id is not None:
        query = query.filter(models.Robot.licence_id == licence_id)

    robots = query.offset(skip).limit(limit).all()
    return robots

@router.put("/{robot_id}/status", response_model=schemas.Robot)
async def update_robot_status(robot_id: int, status: bool, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    logger.info(f"Updating robot status for ID {robot_id} to {status}")
    db_robot = crud.update_robot_status(db, robot_id=robot_id, status=status)
    if db_robot is None:
        logger.error(f"Robot with ID {robot_id} not found")
        raise HTTPException(status_code=404, detail="Robot not found")
    return db_robot

@router.put("/update_health_status", response_model=dict)
def update_robots_health_status(db: Session = Depends(get_db)):
    logger.info("Updating robots health status")
    return crud.update_robots_health_status(db)
