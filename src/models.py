from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime
from .database import Base
import enum
from datetime import datetime, timezone

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    isHealthy = Column(Boolean, default=True)

class AlimentationType(enum.Enum):
    SOLAIRE = "SOLAIRE"
    NUCLEAIRE = "NUCLEAIRE"

class MotorType(enum.Enum):
    PETIT = "PETIT"
    MOYEN = "MOYEN"
    GRAND = "GRAND"

class Robot(BaseModel):
    __tablename__ = "robots"

    name = Column(String, index=True)
    alimentation_id = Column(Integer)
    guidage_id = Column(Integer)
    licence_id = Column(Integer)
    motor = Column(Enum(MotorType), nullable=False)

    @property
    def power_consumption(self):
        motor_consumption = {
            MotorType.PETIT: 10,
            MotorType.MOYEN: 20,
            MotorType.GRAND: 30,
        }
        return motor_consumption.get(self.motor, 0)

    def __str__(self):
        return f"{self.name} id: {self.id}"

class Alimentation(BaseModel):
    __tablename__ = "alimentations"

    alimentationType = Column(Enum(AlimentationType), nullable=False)
    capacity = Column(Integer, nullable=False)

class Guidage(BaseModel):
    __tablename__ = "guidages"

class Licence(BaseModel):
    __tablename__ = "licences"

    expiration_date = Column(DateTime, nullable=False)

    def check_status(self):
        # Check if license has expired
        if self.expiration_date < datetime.now(timezone.utc).replace(tzinfo=None):
            self.isHealthy = False
