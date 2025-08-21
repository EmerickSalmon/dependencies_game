from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src import models, crud
from src.database import engine, SessionLocal
from src.routers import robots, alimentations, guidages, licences
from logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    logger.info("Starting up - updating license health statuses")
    db = SessionLocal()
    try:
        crud.update_licences_health_status(db)
        logger.info("License health status update completed at startup")
    except Exception as e:
        logger.error(f"Error updating license health status at startup: {e}")
    finally:
        db.close()
    
    yield
    
    # Shutdown
    logger.info("Application shutting down")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"message": "Welcome to the API"}

@app.get("/health")
def read_health():
    logger.info("Health endpoint called")
    return {"status": "Healthy"}

app.include_router(robots.router)
app.include_router(alimentations.router)
app.include_router(guidages.router)
app.include_router(licences.router)
