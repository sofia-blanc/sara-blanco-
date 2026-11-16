# TODO: Reemplazar con código real del Integrante 2 (Memoria & Archivos)

def uso_memoria(supabase) -> dict:
    """Retorna información del uso de memoria."""
    return {
        "total_mb": 2048,
        "usado_mb": 1200,
        "libre_mb": 848,
        "porcentaje": 58.6
    }

def registrar_log(supabase, mensaje: str, nivel: str, usuario: str) -> bool:
    """Registra un log en el sistema."""
    return True

def obtener_alertas_almacenamiento(supabase) -> list[str]:
    """Retorna alertas de almacenamiento simuladas."""
    return [
        "⚠️ El espacio del log del sistema está al 85% de capacidad.",
        "⚠️ Poco espacio en caché multimedia."
    ]

def liberar_memoria_proceso(supabase, proceso_id: int) -> bool:
    """Libera la memoria de un proceso específico."""
    return True
