from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from database import Base

# Modelo SQLAlchemy para la tabla habitacion
class Habitacion(Base):
    __tablename__ = "habitacion"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, index=True)
    estado = Column(String, index=True)

# Modelo Pydantic para crear una habitación
class HabitacionBase(BaseModel):
    tipo: str
    estado: str

# Modelo Pydantic para la respuesta de una habitación
class HabitacionRespuesta(BaseModel):
    id: int
    tipo: str
    estado: str

    class Config:
        orm_mode = True
