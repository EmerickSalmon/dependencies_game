import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

# Add the parent directory to the path to import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import app
from src.database import Base, get_db
from src import models

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_robots.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_read_robots_includes_consumption(db_session):
    """
    Test that the /robots endpoint returns robots with the 'consumption' key.
    """
    # Create some test data
    alimentation = models.Alimentation(alimentationType="SOLAIRE", isHealthy=True, capacity=100)
    guidage = models.Guidage(isHealthy=True)
    licence = models.Licence(isHealthy=True, expiration_date=datetime.now(timezone.utc))
    db_session.add(alimentation)
    db_session.add(guidage)
    db_session.add(licence)
    db_session.commit()

    robot1 = models.Robot(
        name="Test Robot 1",
        isHealthy=True,
        alimentation_id=alimentation.id,
        guidage_id=guidage.id,
        licence_id=licence.id,
        motor=models.MotorType.PETIT,
    )
    db_session.add(robot1)
    db_session.commit()

    # Make a request to the /robots endpoint
    response = client.get("/robots")
    assert response.status_code == 200
    robots = response.json()

    # Check that the response contains the robot with the consumption key
    assert len(robots) == 1
    assert "consumption" in robots[0]
    assert robots[0]["consumption"] == 10  # PETIT motor has a consumption of 10
    assert robots[0]["name"] == "Test Robot 1"
