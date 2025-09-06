from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class AlimentationType(str, Enum):
    solaire = "SOLAIRE"
    nucleaire = "NUCLEAIRE"

class MotorType(str, Enum):
    petit = "PETIT"
    moyen = "MOYEN"
    grand = "GRAND"

class RobotBase(BaseModel):
    name: str
    isHealthy: bool
    alimentation_id: int
    guidage_id: int
    licence_id: int
    motor: MotorType

class RobotCreate(RobotBase):
    pass

class Robot(RobotBase):
    id: int
    # Ajout de la consommation du moteur du robot
    consumption: int

    class Config:
        from_attributes = True

class AlimentationBase(BaseModel):
    alimentationType: AlimentationType
    isHealthy: bool
    capacity: int

class AlimentationCreate(AlimentationBase):
    pass

class Alimentation(AlimentationBase):
    id: int

    class Config:
        from_attributes = True

class GuidageBase(BaseModel):
    isHealthy: bool

class GuidageCreate(GuidageBase):
    pass

class Guidage(GuidageBase):
    id: int

    class Config:
        from_attributes = True

class LicenceBase(BaseModel):
    isHealthy: bool
    expiration_date: datetime

class LicenceCreate(LicenceBase):
    pass

class Licence(LicenceBase):
    id: int

    class Config:
        from_attributes = True
