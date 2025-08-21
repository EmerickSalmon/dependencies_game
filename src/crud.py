from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models, schemas
import logging

logger = logging.getLogger(__name__)

def get_robot(db: Session, robot_id: int):
    logger.info(f"Fetching robot with ID {robot_id}")
    db_robot = db.query(models.Robot).filter(models.Robot.id == robot_id).first()
    if db_robot is None:
        logger.error(f"Robot with ID {robot_id} not found")
        raise HTTPException(status_code=400, detail="Missing object")
    return db_robot

def get_robots(db: Session, skip: int = 0, limit: int = 10):
    logger.info(f"Fetching robots with skip={skip} and limit={limit}")
    return db.query(models.Robot).offset(skip).limit(limit).all()

def create_robot(db: Session, robot: schemas.RobotCreate):
    logger.info(f"Creating robot with name {robot.name}")
    db_robot = models.Robot(**robot.model_dump())
    db.add(db_robot)
    db.commit()
    db.refresh(db_robot)
    return db_robot

def get_alimentation(db: Session, alimentation_id: int):
    logger.info(f"Fetching alimentation with ID {alimentation_id}")
    db_alimentation = db.query(models.Alimentation).filter(models.Alimentation.id == alimentation_id).first()
    if db_alimentation is None:
        logger.error(f"Alimentation with ID {alimentation_id} not found")
        raise HTTPException(status_code=400, detail="Missing object")
    return db_alimentation

def get_alimentations(db: Session, skip: int = 0, limit: int = 10):
    logger.info(f"Fetching alimentations with skip={skip} and limit={limit}")
    return db.query(models.Alimentation).offset(skip).limit(limit).all()

def create_alimentation(db: Session, alimentation: schemas.AlimentationCreate):
    logger.info(f"Creating alimentation with type {alimentation.alimentationType}")
    db_alimentation = models.Alimentation(**alimentation.model_dump())
    db.add(db_alimentation)
    db.commit()
    db.refresh(db_alimentation)
    return db_alimentation

def get_guidage(db: Session, guidage_id: int):
    logger.info(f"Fetching guidage with ID {guidage_id}")
    db_guidage = db.query(models.Guidage).filter(models.Guidage.id == guidage_id).first()
    if db_guidage is None:
        logger.error(f"Guidage with ID {guidage_id} not found")
        raise HTTPException(status_code=400, detail="Missing object")
    return db_guidage

def get_guidages(db: Session, skip: int = 0, limit: int = 10):
    logger.info(f"Fetching guidages with skip={skip} and limit={limit}")
    return db.query(models.Guidage).offset(skip).limit(limit).all()

def create_guidage(db: Session, guidage: schemas.GuidageCreate):
    logger.info(f"Creating guidage")
    db_guidage = models.Guidage(**guidage.model_dump())
    db.add(db_guidage)
    db.commit()
    db.refresh(db_guidage)
    return db_guidage

def get_licence(db: Session, licence_id: int):
    logger.info(f"Fetching licence with ID {licence_id}")
    db_licence = db.query(models.Licence).filter(models.Licence.id == licence_id).first()
    if db_licence is None:
        logger.error(f"Licence with ID {licence_id} not found")
        raise HTTPException(status_code=400, detail="Missing object")
    return db_licence

def get_licences(db: Session, skip: int = 0, limit: int = 10):
    logger.info(f"Fetching licences with skip={skip} and limit={limit}")
    return db.query(models.Licence).offset(skip).limit(limit).all()

def create_licence(db: Session, licence: schemas.LicenceCreate):
    logger.info(f"Creating licence with expiration date {licence.expiration_date}")
    db_licence = models.Licence(**licence.model_dump())
    db_licence.check_status()
    db.add(db_licence)
    db.commit()
    db.refresh(db_licence)
    return db_licence

def update_licence_status(db: Session, licence_id: int, status: bool):
    logger.info(f"Updating licence status for ID {licence_id} to {status}")
    db_licence = get_licence(db, licence_id)
    if db_licence.isHealthy != status:
        db_licence.isHealthy = status
        db_licence.check_status()
        db.commit()
        db.refresh(db_licence)
    return db_licence

def update_licences_health_status(db: Session):
    logger.info("Updating all licences health status based on expiration dates")
    licences = db.query(models.Licence).all()
    updated_count = 0
    
    for licence in licences:
        original_status = licence.isHealthy
        licence.check_status()
        if licence.isHealthy != original_status:
            updated_count += 1
            db.commit()
            db.refresh(licence)
    
    logger.info(f"Updated {updated_count} licence(s) health status based on expiration")
    return {"message": f"Updated {updated_count} licence(s) health status based on expiration"}

def update_robot_status(db: Session, robot_id: int, status: bool):
    logger.info(f"Updating robot status for ID {robot_id} to {status}")
    db_robot = get_robot(db, robot_id)
    if status:
        # Check if related objects are healthy
        alimentation = get_alimentation(db, db_robot.alimentation_id)
        guidage = get_guidage(db, db_robot.guidage_id)
        licence = get_licence(db, db_robot.licence_id)
        if (alimentation and not alimentation.isHealthy) or \
           (guidage and not guidage.isHealthy) or \
           (licence and not licence.isHealthy):
            logger.error(f"Related objects for robot ID {robot_id} are not healthy")
            raise HTTPException(status_code=400, detail="Related objects are not healthy")
    db_robot.isHealthy = status
    db.commit()
    db.refresh(db_robot)
    return db_robot

def update_robots_health_status(db: Session):
    logger.info("Updating robots health status based on related objects")
    
    # First, update all licences based on expiration dates
    update_licences_health_status(db)
    
    # Get all unhealthy alimentations
    unhealthy_alimentations = db.query(models.Alimentation).filter(models.Alimentation.isHealthy == False).all()
    # Get all unhealthy guidages
    unhealthy_guidages = db.query(models.Guidage).filter(models.Guidage.isHealthy == False).all()
    # Get all unhealthy licences
    unhealthy_licences = db.query(models.Licence).filter(models.Licence.isHealthy == False).all()

    # Update robots linked to unhealthy alimentations
    for alimentation in unhealthy_alimentations:
        robots = db.query(models.Robot).filter(models.Robot.alimentation_id == alimentation.id).all()
        for robot in robots:
            robot.isHealthy = False
            db.commit()
            db.refresh(robot)

    # Update robots linked to unhealthy guidages
    for guidage in unhealthy_guidages:
        robots = db.query(models.Robot).filter(models.Robot.guidage_id == guidage.id).all()
        for robot in robots:
            robot.isHealthy = False
            db.commit()
            db.refresh(robot)

    # Update robots linked to unhealthy licences
    for licence in unhealthy_licences:
        robots = db.query(models.Robot).filter(models.Robot.licence_id == licence.id).all()
        for robot in robots:
            robot.isHealthy = False
            db.commit()
            db.refresh(robot)
    
    unhealthy_robots = db.query(models.Robot).filter(models.Robot.isHealthy == False).all()
    print(f"Unhealthy robots found: {len(unhealthy_robots)}")
    for robot in unhealthy_robots:
        alimentation = db.query(models.Alimentation).filter(models.Alimentation.id == robot.alimentation_id).first()
        guidage = db.query(models.Guidage).filter(models.Guidage.id == robot.guidage_id).first()
        licence = db.query(models.Licence).filter(models.Licence.id == robot.licence_id).first()
        if alimentation and alimentation.isHealthy and guidage and guidage.isHealthy and licence and licence.isHealthy:
            robot.isHealthy = True
            db.commit()
            db.refresh(robot)
    # return {"message": "Unhealthy robots updated if all related objects are healthy."}

    return {"message": "Robots health status updated based on related objects"}
