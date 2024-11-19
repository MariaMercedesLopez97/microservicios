import pika

def enviar_mensaje_estado(habitacion_id, estado):
    # Creamos una conexión con RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    #crea la cola
    channel.queue_declare(queue='actualizar_estado_habitacion')
    #Envia el mensaje
    mensaje = {"habitacion_id": habitacion_id, "estado": estado}

    channel.basic_publish(exchange='', routing_key='actualizar_estado_habitacion', body=str(mensaje))
    connection.close()