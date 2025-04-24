import paho.mqtt.client as mqtt
from paho.mqtt.client import topic_matches_sub
import threading
import uuid

_callbacks = []
_client = None
_lock = threading.Lock()

_GLOBAL_TOPIC_PREFIX = "PR2/A9/"

BROKER="0.0.0.0"
BROKERREMOTE="100.93.177.37"
PORT=1883

def register_callback(sub_topic, callback):
    """Registra una función callback asociada a un subtopic."""
    with _lock:
        full_topic = _GLOBAL_TOPIC_PREFIX + sub_topic
        _callbacks.append((full_topic, callback))

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    with _lock:
        for sub_topic, callback in _callbacks:
            if topic_matches_sub(sub_topic, topic):
                threading.Thread(target=callback, args=(topic, payload), daemon=True).start()

def setup_mqtt(client_id=None, broker=BROKERREMOTE, port=1883):
    """Inicia el cliente MQTT, se suscribe automáticamente a {prefix}#."""
    if client_id is None:
        client_id = str(uuid.uuid4())
    global _client
    _client = mqtt.Client(client_id=client_id)
    _client.on_message = on_message
    _client.connect(broker, port)
    _client.loop_start()

    # Suscripción general a todos los topics bajo el prefijo
    if _GLOBAL_TOPIC_PREFIX:
        _client.subscribe(f"{_GLOBAL_TOPIC_PREFIX}#")
    else:
        raise ValueError("El prefijo global no está definido.")


def disconnect():
    """Desconecta el cliente MQTT y detiene el bucle."""
    global _client
    if _client:
        _client.loop_stop()
        _client.disconnect()
        _client = None
    else:
        pass
    
def publish(topic, message, qos=2, retain=False):
    """Publica un mensaje en un topic con el prefijo aplicado."""
    if _client:
        _client.publish(f"{_GLOBAL_TOPIC_PREFIX}{topic}", message, qos, retain)
    else:
        raise RuntimeError("MQTT no está inicializado. Llama a setup_mqtt primero.")