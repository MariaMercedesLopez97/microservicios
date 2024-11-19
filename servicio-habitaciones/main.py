from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Habitacion, HabitacionBase, HabitacionRespuesta
from typing import List
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import pybreaker
from pybreaker import CircuitBreakerError


# Crea la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI()

#Configura circuit breaker
db_circuit_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=10)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Manejo de las excepciones para CircuitBreakerError
@app.exception_handler(CircuitBreakerError)
def circuit_breaker_exception_handler(request, exc):
    return JSONResponse(
        status_code=503,
        content={"detail": "Servicio temporalmente no disponible, por favor intente más tarde."},
    )

@app.get("/habitaciones/", response_model=List[HabitacionRespuesta])
@db_circuit_breaker
def get_habitaciones(db: Session = Depends(get_db)):
    habitaciones = db.query(Habitacion).all()
    return habitaciones

@app.post("/habitaciones/", response_model=HabitacionRespuesta)
@db_circuit_breaker
def crear_habitacion(habitacion: HabitacionBase, db: Session = Depends(get_db)):
    db_habitacion = Habitacion(tipo=habitacion.tipo, estado=habitacion.estado)
    db.add(db_habitacion)
    db.commit()
    db.refresh(db_habitacion)
    return db_habitacion

@app.get("/habitaciones/{habitacion_id}", response_model=HabitacionRespuesta)
@db_circuit_breaker
def get_habitacion(habitacion_id: int, db: Session = Depends(get_db)):
    habitacion = db.query(Habitacion).filter(Habitacion.id == habitacion_id).first()
    if habitacion is None:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    return habitacion

@app.put("/habitaciones/{habitacion_id}", response_model=HabitacionRespuesta)
@db_circuit_breaker
def actualizar_habitacion(habitacion_id: int, habitacion: HabitacionBase, db: Session = Depends(get_db)):
    db_habitacion = db.query(Habitacion).filter(Habitacion.id == habitacion_id).first()
    if db_habitacion is None:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    db_habitacion.tipo = habitacion.tipo
    db_habitacion.estado = habitacion.estado
    db.commit()
    db.refresh(db_habitacion)
    return db_habitacion

@app.delete("/habitaciones/{habitacion_id}")
@db_circuit_breaker
def eliminar_habitacion(habitacion_id: int, db: Session = Depends(get_db)):
    db_habitacion = db.query(Habitacion).filter(Habitacion.id == habitacion_id).first()
    if db_habitacion is None:
        raise HTTPException(status_code=404, detail="Habitación no encontrada")
    db.delete(db_habitacion)
    db.commit()
    return {"detail": "Habitación eliminada exitosamente"}
