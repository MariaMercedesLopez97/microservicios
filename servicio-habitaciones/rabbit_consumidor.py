import pika
import json
from database import SessionLocal
from models import Habitacion


def actualizar_estado_habitacion(mensaje):
    
    db = SessionLocal()
    datos = json.loads(mensaje)
    habitacion = db.query(Habitacion).filter(Habitacion.id == datos['habitacion_id']).first()
    if habitacion:
        habitacion.estado = datos['estado']
        db.commit()
    db.close()

def recibir_mensajes():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='actualizar_estado_habitacion')

    def callback(ch, method, properties, body):
        actualizar_estado_habitacion(body.decode())

    channel.basic_consume(queue='actualizar_estado_habitacion', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

recibir_mensajes()