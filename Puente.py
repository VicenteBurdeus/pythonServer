import socket
import threading
import time
import json

import LBmqtt
import PostSQTcom as SQL

PCSERVIDOR = 0 # 0 = PC, 1 = Servidor

def init():
    # Inicializa el socket y la conexión a la base de datos
    
    if PCSERVIDOR == 0:
        LBmqtt.setup_mqtt(client_id="Puente",broker=LBmqtt.BROKERREMOTE, port=1883)
    elif PCSERVIDOR == 1:
        LBmqtt.setup_mqtt(client_id="Puente",broker=LBmqtt.BROKER, port=1883)
    
    LBmqtt.register_callback("NT", NodeTemperature)

    

def NodeTemperature(topic, payload):

    tags = "ID ,temperatura, humedad, battery"
    NOMBRETABLANT = "sensores"

    try:
        data = json.loads(payload)
        node_id = data.get("ID")
        temperature = float(data.get("temperatura"))
        humidity = int(data.get("humedad"))

        # Battery puede ser None si no está o no es un número
        raw_battery = data.get("battery")
        try:
            battery = int(raw_battery) if raw_battery is not None else None
        except (ValueError, TypeError):
            battery = None

    except json.JSONDecodeError:
        print("Error al decodificar el JSON")
        return

    # Asegura que node_id contenga NT_
    if not node_id or not node_id.startswith("NT_"):
        print(f"ID de nodo no válido: {node_id}")
        return

    # Alerta si la batería es baja
    if battery is not None and battery < 20:
        LBmqtt.publish(f"PR2/A9/alerta/{node_id}", f"Batería baja: {battery}%")
        print(f"Alerta: Batería baja en el nodo {node_id}: {battery}%")

        
        LBmqtt.publish(f"PR2/A9/temperatura/{node_id}", f"Temperatura del nodo {node_id} es de: {temperature}°C")
    
    if PCSERVIDOR == 1:

        SQL.uploadBD(NOMBRETABLANT, tags, (node_id, temperature, humidity, battery))



init()

while True:
    pass