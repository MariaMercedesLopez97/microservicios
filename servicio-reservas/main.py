from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import requests
from database import engine, SessionLocal, Base
from models import ReservaDB, ReservaBase, ReservaRespuesta
from typing import List
from fastapi.responses import JSONResponse
import pybreaker
from pybreaker import CircuitBreakerError

# Crea la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configura Circuit Breaker para el servicio de habitaciones
habitaciones_circuit_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=10)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Maneja las excepciones para CircuitBreakerError
@app.exception_handler(CircuitBreakerError)
def circuit_breaker_exception_handler(request, exc):
    return JSONResponse(
        status_code=503,
        content={"detail": "Servicio de habitaciones temporalmente no disponible. Intente más tarde."},
    )

@app.post("/reservas/", response_model=ReservaRespuesta)
@habitaciones_circuit_breaker
def crear_reserva(reserva: ReservaBase, db: Session = Depends(get_db)):
    # Verifica disponibilidad de la habitación en el servicio de habitaciones
    try:
        response = habitaciones_circuit_breaker.call(
            requests.get, f"http://localhost:8000/habitaciones/{reserva.habitacion_id}"
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Habitación no encontrada")
        
        habitacion = response.json()
        
        if habitacion['estado'] != 'Disponible':
            raise HTTPException(status_code=400, detail="La habitación no está disponible")
        
        # Crea reserva en la base de datos
        db_reserva = ReservaDB(
            nombre=reserva.nombre,
            habitacion_id=reserva.habitacion_id,
            dias=reserva.dias
        )
        
        db.add(db_reserva)
        db.commit()
        db.refresh(db_reserva)
        
        # Actualiza estado de la habitación
        update_response = habitaciones_circuit_breaker.call(
            requests.put,
            f"http://localhost:8000/habitaciones/{reserva.habitacion_id}",
            json={"tipo": habitacion['tipo'], "estado": "ocupado"}
        )
        
        return db_reserva
    
    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Error al comunicarse con el servicio de habitaciones")

@app.get("/reservas/", response_model=List[ReservaRespuesta])
def obtener_reservas(db: Session = Depends(get_db)):
    reservas = db.query(ReservaDB).all()
    return reservas

@app.get("/reservas/{reserva_id}", response_model=ReservaRespuesta)
def get_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(ReservaDB).filter(ReservaDB.id == reserva_id).first()
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva

@app.put("/reservas/{reserva_id}", response_model=ReservaRespuesta)
def actualizar_reserva(reserva_id: int, reserva: ReservaBase, db: Session = Depends(get_db)):
    db_reserva = db.query(ReservaDB).filter(ReservaDB.id == reserva_id).first()
    if db_reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    db_reserva.nombre = reserva.nombre
    db_reserva.habitacion_id = reserva.habitacion_id
    db_reserva.dias = reserva.dias
    db.commit()
    db.refresh(db_reserva)
    return db_reserva

@app.delete("/reservas/{reserva_id}")
def eliminar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    db_reserva = db.query(ReservaDB).filter(ReservaDB.id == reserva_id).first()
    if db_reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    db.delete(db_reserva)
    db.commit()
    
    # Opcional: Actualizar estado de la habitación a disponible
    try:
        habitaciones_circuit_breaker.call(
            requests.put,
            f"http://localhost:8000/habitaciones/{db_reserva.habitacion_id}", 
            json={"tipo": "habitacion", "estado": "Disponible"}
        )
    except:
        pass
    
    return {"detail": "Reserva eliminada exitosamente"}
