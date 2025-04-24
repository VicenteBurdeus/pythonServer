import psycopg2

# Configura tu conexión a PostgreSQL
DB_CONFIG = {
    'dbname': 'midb',
    'user': 'miusuario',
    'password': 'miclave',
    'host': 'localhost',
    'port': 5432
}

# Conexión global para mantenerla abierta
_conn = None
_cursor = None

def _ensure_connection():
    global _conn, _cursor
    if _conn is None or _conn.closed:
        _conn = psycopg2.connect(**DB_CONFIG)
        _cursor = _conn.cursor()

def uploadBD(table: str, columns: str, values: tuple):
    """Ejecuta una sentencia INSERT en la base de datos usando parámetros para evitar inyecciones SQL."""
    
    if not columns or not columns.strip():
        raise ValueError("Las columnas no pueden estar vacías.")
    
    if not values:
        raise ValueError("Los valores no pueden estar vacíos.")
    
    # Asegurarse de que 'values' sea una tupla o lista de valores
    if not isinstance(values, (tuple, list)):
        raise TypeError("Los valores deben ser una tupla o lista.")
    
    # Construcción segura de la consulta SQL usando parámetros
    query = f"INSERT INTO {table} ({columns}) VALUES ({', '.join(['%s'] * len(values))})"
    
    # Ejecutar la consulta de manera segura con parámetros
    _ensure_connection()  # Aseguramos la conexión
    _cursor.execute(query, values)  # Ejecutamos con los parámetros
    _conn.commit()  # Confirmamos la transacción


def request(query: str):
    """Ejecuta una consulta (SELECT...) y devuelve los resultados como lista de tuplas."""
    _ensure_connection()
    _cursor.execute(query)
    return _cursor.fetchall()

