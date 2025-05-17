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
    