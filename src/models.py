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

class Robot(BaseModel):
    __tablename__ = "robots"

    name = Column(String, index=True)
    alimentation_id = Column(Integer)
    guidage_id = Column(Integer)
    licence_id = Column(Integer)

    def __str__(self):
        return f"{self.name} id: {self.id}"

class Alimentation(BaseModel):
    __tablename__ = "alimentations"

    alimentationType = Column(Enum(AlimentationType), nullable=False)

class Guidage(BaseModel):
    __tablename__ = "guidages"

class Licence(BaseModel):
    __tablename__ = "licences"

    expiration_date = Column(DateTime, nullable=False)

    def check_status(self):
        if self.expiration_date < datetime.now(timezone.utc).replace(tzinfo=None):
            self.isHealthy = False
