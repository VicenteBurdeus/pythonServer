import psycopg2
import LBmqtt as mqtt

# Configura tu conexión a PostgreSQL
DB_CONFIG = {
    'dbname': 'Queso',
    'user': 'admin',
    'password': 'admin',
    'host': 'postgres',
    'port': 5432
}

# Conexión global para mantenerla abierta
_conn = None
_cursor = None

def _ensure_connection():
    global _conn, _cursor
    if _conn is None or _conn.closed:
        try:
            _conn = psycopg2.connect(**DB_CONFIG)
            _cursor = _conn.cursor()
            print("[DB] Conexión establecida correctamente.")
            mqtt.publish("db/status", "Conexión a PostgreSQL exitosa.")
        except Exception as e:
            print(f"[DB] Error al conectar con la base de datos: {e}")
            mqtt.publish("db/status", f"Error de conexión a PostgreSQL: {e}")
            raise



def uploadBD(table: str, columns: str, values: tuple):
    """Ejecuta una sentencia INSERT en la base de datos usando parámetros para evitar inyecciones SQL."""
    if not columns or not columns.strip():
        raise ValueError("Las columnas no pueden estar vacías.")
    
    if not values:
        raise ValueError("Los valores no pueden estar vacíos.")
    
    if not isinstance(values, (tuple, list)):
        raise TypeError("Los valores deben ser una tupla o lista.")
    
    try:
        # Preparar placeholders seguros para los valores
        placeholders = ', '.join(['%s'] * len(values))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        _ensure_connection()
        _cursor.execute(query, values)
        _conn.commit()
    except Exception as e:
        print(f"[uploadBD] Error al insertar en la base de datos: {e}")
        _conn.rollback()  # Deshacer cambios en caso de error
        mqtt.publish("db/status", f"Error al insertar en la base de datos: {e}")
        raise


def request(query: str):
    """Ejecuta una consulta (SELECT...) y devuelve los resultados como lista de tuplas."""
    _ensure_connection()
    _cursor.execute(query)
    return _cursor.fetchall()


def alter(table: str, columns: str, values: tuple, where: str):
    """Ejecuta una sentencia UPDATE en la base de datos usando parámetros para evitar inyecciones SQL."""
    if not columns or not columns.strip():
        raise ValueError("Las columnas no pueden estar vacías.")
    
    if not values:
        raise ValueError("Los valores no pueden estar vacíos.")
    
    if not isinstance(values, (tuple, list)):
        raise TypeError("Los valores deben ser una tupla o lista.")
    
    try:
        # Preparar placeholders seguros para los valores
        query = f"UPDATE {table} SET {columns} WHERE {where}"
        
        _ensure_connection()
        _cursor.execute(query, values)
        _conn.commit()
    except Exception as e:
        print(f"[alter] Error al actualizar la base de datos: {e}")
        _conn.rollback()  # Deshacer cambios en caso de error
        mqtt.publish("db/status", f"Error al actualizar la base de datos: {e}")
        raise
