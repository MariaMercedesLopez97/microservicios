from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from database import Base


# Modelo SQLAlchemy para la tabla reserva
class ReservaDB(Base):
    __tablename__ = "reservas"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    habitacion_id = Column(Integer, index=True)
    dias = Column(Integer)
    

# Modelo Pydantic para crear una reserva
class ReservaBase(BaseModel):
    nombre: str
    habitacion_id: int
    dias: int
    

# Modelo Pydantic para la respuesta de una reserva
class ReservaRespuesta(BaseModel):
    id: int
    nombre: str
    habitacion_id: int
    dias: int

    class Config:
        orm_mode = True