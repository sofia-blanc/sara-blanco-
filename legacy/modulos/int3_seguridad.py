# TODO: Reemplazar con código real del Integrante 3 (Seguridad & Dispositivos)

def verificar_permiso(supabase, user_id: str, permiso: str) -> bool:
    """Verifica si un usuario tiene un permiso específico."""
    return True

def obtener_dispositivos(supabase) -> list[dict]:
    """Retorna la lista de dispositivos del vehículo."""
    return [
        {"id": 1, "nombre": "Motor", "tipo": "actuador", "estado": "activo"},
        {"id": 2, "nombre": "Frenos", "tipo": "actuador", "estado": "activo"},
        {"id": 3, "nombre": "GPS", "tipo": "sensor", "estado": "activo"},
        {"id": 4, "nombre": "A/C", "tipo": "actuador", "estado": "activo"},
        {"id": 5, "nombre": "Pantalla", "tipo": "actuador", "estado": "activo"},
        {"id": 6, "nombre": "Sensores Parking", "tipo": "sensor", "estado": "inactivo"},
        {"id": 7, "nombre": "Cámara Trasera", "tipo": "sensor", "estado": "inactivo"},
        {"id": 8, "nombre": "Antena V2X", "tipo": "comunicacion", "estado": "activo"}
    ]

def obtener_bateria(supabase) -> float:
    """Retorna el nivel de batería simulado."""
    return 78.5

def obtener_eventos_criticos(supabase) -> list[dict]:
    """Retorna eventos críticos (actualmente vacío para simular luz verde)."""
    return []

def validar_rol_para_accion(supabase, user_id: str, accion: str) -> bool:
    """Valida si el rol del usuario puede ejecutar una acción."""
    return True
