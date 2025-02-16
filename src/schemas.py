from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class AlimentationType(str, Enum):
    solaire = "SOLAIRE"
    nucleaire = "NUCLEAIRE"

class RobotBase(BaseModel):
    name: str
    isHealthy: bool
    alimentation_id: int
    guidage_id: int
    licence_id: int

class RobotCreate(RobotBase):
    pass

class Robot(RobotBase):
    id: int

    class Config:
        from_attributes = True

class AlimentationBase(BaseModel):
    alimentationType: AlimentationType
    isHealthy: bool

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
