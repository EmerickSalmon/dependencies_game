from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from src import models
from src.database import engine
from src.routers import robots, alimentations, guidages, licences
from logging_config import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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
