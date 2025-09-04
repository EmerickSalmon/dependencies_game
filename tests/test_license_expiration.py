import pytest
import sys
import os
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path to import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import models, crud, schemas
from src.database import Base


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_license.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


class TestLicenseExpiration:
    
    def test_license_check_status_healthy_when_not_expired(self, db_session):
        """Test that a license remains healthy when not expired"""
        # Create a license that expires in the future
        future_date = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=30)
        license_data = schemas.LicenceCreate(
            isHealthy=True,
            expiration_date=future_date
        )
        
        # Create the license
        license = crud.create_licence(db_session, license_data)
        
        # License should still be healthy
        assert license.isHealthy == True
        
        # Call check_status explicitly
        license.check_status()
        assert license.isHealthy == True
    
    def test_license_check_status_unhealthy_when_expired(self, db_session):
        """Test that a license becomes unhealthy when expired"""
        # Create a license that expired in the past
        past_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)
        license_data = schemas.LicenceCreate(
            isHealthy=True,
            expiration_date=past_date
        )
        
        # Create the license
        license = crud.create_licence(db_session, license_data)
        
        # License should become unhealthy due to expiration
        assert license.isHealthy == False
    
    def test_update_licences_health_status_updates_expired_licenses(self, db_session):
        """Test that update_licences_health_status updates all expired licenses"""
        # Create multiple licenses - some expired, some not
        future_date = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=30)
        past_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)
        
        # Create healthy license that's not expired
        healthy_license_data = schemas.LicenceCreate(
            isHealthy=True,
            expiration_date=future_date
        )
        healthy_license = crud.create_licence(db_session, healthy_license_data)
        
        # Create expired license that's still marked as healthy
        expired_license = models.Licence(
            isHealthy=True,
            expiration_date=past_date
        )
        db_session.add(expired_license)
        db_session.commit()
        db_session.refresh(expired_license)
        
        # Run the update function
        result = crud.update_licences_health_status(db_session)
        
        # Check that the expired license is now unhealthy
        db_session.refresh(expired_license)
        db_session.refresh(healthy_license)
        
        assert expired_license.isHealthy == False
        assert healthy_license.isHealthy == True
        assert "Updated 1 licence(s)" in result["message"]
    
    def test_license_creation_with_expired_date(self, db_session):
        """Test that creating a license with an expired date makes it unhealthy immediately"""
        past_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=5)
        license_data = schemas.LicenceCreate(
            isHealthy=True,
            expiration_date=past_date
        )
        
        license = crud.create_licence(db_session, license_data)
        assert license.isHealthy == False
    
    def test_update_robots_health_status_calls_license_update(self, db_session):
        """Test that updating robot health status also updates license statuses"""
        # Create an expired license
        past_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)
        expired_license = models.Licence(
            isHealthy=True,  # Manually set to healthy even though expired
            expiration_date=past_date
        )
        db_session.add(expired_license)
        db_session.commit()
        db_session.refresh(expired_license)
        
        # Create related objects
        alimentation = models.Alimentation(alimentationType=models.AlimentationType.SOLAIRE, isHealthy=True, capacity=100)
        guidage = models.Guidage(isHealthy=True)
        db_session.add(alimentation)
        db_session.add(guidage)
        db_session.commit()
        db_session.refresh(alimentation)
        db_session.refresh(guidage)
        
        # Create a robot linked to the expired license
        robot = models.Robot(
            name="Test Robot",
            isHealthy=True,
            alimentation_id=alimentation.id,
            guidage_id=guidage.id,
            licence_id=expired_license.id,
            motor=models.MotorType.PETIT
        )
        db_session.add(robot)
        db_session.commit()
        db_session.refresh(robot)
        
        # Call update_robots_health_status
        crud.update_robots_health_status(db_session)
        
        # Check that the expired license is now unhealthy
        db_session.refresh(expired_license)
        db_session.refresh(robot)
        
        assert expired_license.isHealthy == False
        assert robot.isHealthy == False  # Robot should be unhealthy due to expired license


if __name__ == "__main__":
    pytest.main([__file__])