import socket
import threading
import time
import json

import where as W
import LBmqtt
import PostSQTcom as SQL


def parse_float(value):
    if value is None:
        return None
    """Convierte un valor de texto en un número flotante, manejando comas y redondeo."""
    if isinstance(value, str):
        # Reemplaza las comas por puntos
        value = value.replace(",", ".")
    try:
        # Convierte el valor a float y lo redondea a 2 decimales (puedes ajustar la precisión)
        return round(float(value), 2)
    except ValueError:
        print(f"Error al convertir el valor a float: {value}")
        return None

def parse_int(value):
    if value is None:
        return None
    """Convierte un valor de texto en un número entero, manejando comas y redondeo."""
    if isinstance(value, str):
        value = value.replace(",", ".").strip()  # Reemplaza las comas por puntos y elimina espacios
    try:
        return round(float(value))  # Convierte el valor a float y luego lo redondea a entero
    except ValueError as e:
        print(f"Error al convertir el valor '{value}' a entero: {e}")
        return None  # Devuelve None si no puede convertirse

def init():
    # Inicializa el socket y la conexión a la base de datos
    
    if W.PCSERVIDOR == 0:
        LBmqtt.setup_mqtt(client_id="Puente_Server",broker=LBmqtt.BROKER, port=1883)
    elif W.PCSERVIDOR < 100:
        LBmqtt.setup_mqtt(client_id=f"Puente{W.PCSERVIDOR}",broker=LBmqtt.BROKERREMOTE, port=1883)
    elif W.PCSERVIDOR >= 100:
        LBmqtt.setup_mqtt(client_id=f"Puente_NO_VPN{W.PCSERVIDOR}",broker=LBmqtt.BROKERREMOTE, port=1883)
    else:
        raise RuntimeError("Error en la configuración del puente")

    LBmqtt.register_callback("NT", NodeTemperature)

    LBmqtt.publish("PR2/A9/estado", "Puente activo")
    

def NodeTemperature(topic, payload):

    tags = ("id_nodo, temperatura, humedad, bateria")
    NOMBRETABLANT = "ntdato"

    try:
        data = json.loads(payload)
        node_id = data.get("ID")
        temperature = parse_float(data.get("temperatura"))
        humidity = parse_int(data.get("humedad"))

        # Battery puede ser None si no está o no es un número
        raw_battery = parse_int(data.get("battery"))
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
        #print(f"Alerta: Batería baja en el nodo {node_id}: {battery}%")

        
    LBmqtt.publish(f"PR2/A9/temperatura/{node_id}", f"Temperatura del nodo {node_id} es de: {temperature}°C con una humadad de: {humidity}%")
    
    if W.PCSERVIDOR == 0:
        if battery is not None:
            SQL.uploadBD(NOMBRETABLANT, tags, (node_id, temperature, humidity, battery))
        else:
            SQL.uploadBD(NOMBRETABLANT, tags, (node_id, temperature, humidity, "NULL"))
    else:
        print(f"ID: {node_id}, Temperatura: {temperature}, Humedad: {humidity}, Batería: {battery}")

init()

while True:
    pass