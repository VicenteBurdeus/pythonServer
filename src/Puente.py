import socket
import threading
import time
import json
from uuid import uuid4 as uuid

import where as W
import LBmqtt as LBmqtt
import PostSQTcom as SQL
import Parses as P

TOPIC_MAP = {}

def init():
    # Inicializa el socket y la conexión a la base de datos
    LBmqtt.disconnect()
    print("Conectando al broker MQTT...")
    LBmqtt.setup_mqtt(client_id=f"{uuid()}", broker=LBmqtt.BROKER, port=LBmqtt.PORT)
    

    cargar_topics_en_memoria()  # Carga los topics en memoria
    for topic in TOPIC_MAP:
        print(f"Topic: {topic} -> ID: {TOPIC_MAP[topic]}")


    LBmqtt.register_callback("#", mqtt_global_handler)  # Callback para el estado del puente
    # Asigna las funciona por topic
    LBmqtt.register_callback("debug", debug)  # Callback para el estado del puente
    LBmqtt.register_callback("NT", NodeTemperature)
    LBmqtt.register_callback("AGV", agvEnd)
    LBmqtt.register_callback("CAM", camInfo)
    print("Se a establecido los callbacks")

    

    LBmqtt.publish("PR2/A9/estado", "Puente activo")
    #intenta conectar a la base de datos
    try:
        SQL._ensure_connection()
        LBmqtt.publish("PR2/A9/estado", "Conexión a la base de datos exitosa")
    except Exception as e:
        print(f"[DB] Error al conectar con la base de datos: {e}")
        LBmqtt.publish("PR2/A9/estado", f"Error de conexión a la base de datos: {e}")
        raise

    
def debug(topic, payload):
    LBmqtt.publish("PR2/A9/estado", f"Estado del puente: {payload}")
    cargar_topics_en_memoria()

def cargar_topics_en_memoria():
    """Carga todos los topics de la base de datos a memoria."""
    global TOPIC_MAP
    try:
        registros = SQL.request("SELECT id_topic, topic FROM mqtt_topics")
        TOPIC_MAP = {t[1].strip(): t[0] for t in registros}
        print(f"[TOPICS] Se han cargado {len(TOPIC_MAP)} topics en memoria.")
    except Exception as e:
        print(f"[TOPICS] Error al cargar topics: {e}")
        LBmqtt.publish("db/status", f"Error al cargar topics: {e}")
        raise

def mqtt_global_handler(topic, payload):
    global TOPIC_MAP
    try:
        # Verifica si el topic existe en la base de datos
        if topic not in TOPIC_MAP:
            SQL.uploadBD("mqtt_topics", "topic", (topic,))
            cargar_topics_en_memoria()
        payload_clean = payload.replace("\n","").replace("\r", "").strip()
        SQL.uploadBD("mqtt_datos", "id_dato, payload", (TOPIC_MAP[topic], payload_clean))
    except Exception as e:
        print(f"[MQTT] Error al manejar el topic {topic}: {e}")
        #LBmqtt.publish("db/status", f"Error al manejar el topic {topic}: {e}")
        raise


    


def NodeTemperature(topic, payload):

    tags = ("id_nodo, temperatura, humedad, bateria")
    tagsnobattery = ("id_nodo, temperatura, humedad")
    NOMBRETABLANT = "ntdato"

    try:
        data = json.loads(payload)
        node_id = data.get("ID")
        temperature = P.parse_float(data.get("temperatura"))
        humidity = P.parse_int(data.get("humedad"))

        # Battery puede ser None si no está o no es un número
        raw_battery = P.parse_int(data.get("battery"))
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

        
    #LBmqtt.publish(f"PR2/A9/temperatura/{node_id}", f"Temperatura del nodo {node_id} es de: {temperature}°C con una humadad de: {humidity}%")
    

    if battery is not None:
        SQL.uploadBD(NOMBRETABLANT, tags, (node_id, temperature, humidity, battery))
    else:
        SQL.uploadBD(NOMBRETABLANT, tagsnobattery, (node_id, temperature, humidity))

def agvEnd(topic, payload):
    tags = ("id_robot, estado, carga")
    NOMBRETABLAAGV = "robotagvinfo"

    try:
        data = json.loads(payload)
        agv_id = data.get("ID")
        state = data.get("estado")
        load = P.parse_int(data.get("carga"))
    except json.JSONDecodeError:
        print("Error al decodificar el JSON")
        return
    SQL.alter(NOMBRETABLAAGV, "estado = %s, carga = %s", (state, load), f"id_robot = '{agv_id}'")
    #LBmqtt.publish(f"PR2/A9/estado/{agv_id}", f"Estado del AGV {agv_id} es: {state} con una carga de: {load}%")

def camInfo(topic, payload):
    tag = ("id_usuario,ip")
    NOMBRETABLACAM = "userinfo"
    NOMBRETABLALOGIN = "logininfo"

    try:
        data = json.loads(payload)
        cam_id = data.get("ID")
        urlid = data.get("data")
    except json.JSONDecodeError:
        print("Error al decodificar el JSON")
        return
    
    if not cam_id or not cam_id.startswith("CAM_"):
        print(f"ID de cámara no válido: {cam_id}")
        return
    
    result = SQL.request(f"SELECT id_usuario FROM {NOMBRETABLACAM} WHERE dataid = '{urlid}'")
    if result is None or len(result) == 0:
        print(f"ID de cámara no encontrado: {cam_id}")
        return
    
    LBmqtt.publish(f"PR2/A9/login", f"Se logueando el usuario {result[0][0]}")
    SQL.uploadBD(NOMBRETABLALOGIN, tag, (result[0][0], cam_id))


init()

while True:
    pass