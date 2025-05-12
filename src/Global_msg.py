import PostSQTcom as SQL

import LBmqtt
import Parses as P

def global_to_bbdd():
    """Sube los datos globales a la base de datos."""
    # Conexión a la base de datos
    SQL._ensure_connection()
    
    # Obtener los datos globales
    global_data = P.get_global_data()
    
    # Subir los datos a la base de datos
    for table, data in global_data.items():
        for record in data:
            columns = ', '.join(record.keys())
            values = tuple(record.values())
            SQL.uploadBD(table, columns, values)
    
    # Cerrar la conexión a la base de datos
