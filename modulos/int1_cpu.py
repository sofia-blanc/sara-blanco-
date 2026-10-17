from datetime import datetime, timedelta

# TODO: Reemplazar con código real del Integrante 1 (CPU & Processes)

def obtener_procesos(supabase) -> list[dict]:
    """Retorna la lista de procesos simulados del OS del auto."""
    return [
        {"id": 1, "nombre": "Control del Motor", "prioridad": "crítica", "estado": "ejecutando", "cpu_porcentaje": 25, "memoria_mb": 128, "creado_por": "sistema", "created_at": "2023-10-01T10:00:00"},
        {"id": 2, "nombre": "Sistema de Frenos ABS", "prioridad": "crítica", "estado": "ejecutando", "cpu_porcentaje": 15, "memoria_mb": 64, "creado_por": "sistema", "created_at": "2023-10-01T10:00:01"},
        {"id": 3, "nombre": "Navegación GPS", "prioridad": "alta", "estado": "listo", "cpu_porcentaje": 10, "memoria_mb": 256, "creado_por": "usuario1", "created_at": "2023-10-01T10:00:02"},
        {"id": 4, "nombre": "Climatización", "prioridad": "media", "estado": "ejecutando", "cpu_porcentaje": 8, "memoria_mb": 32, "creado_por": "usuario1", "created_at": "2023-10-01T10:00:03"},
        {"id": 5, "nombre": "Infoentretenimiento", "prioridad": "baja", "estado": "bloqueado", "cpu_porcentaje": 0, "memoria_mb": 512, "creado_por": "usuario1", "created_at": "2023-10-01T10:00:04"},
        {"id": 6, "nombre": "Sensores Estacionamiento", "prioridad": "alta", "estado": "suspendido", "cpu_porcentaje": 0, "memoria_mb": 16, "creado_por": "sistema", "created_at": "2023-10-01T10:00:05"},
        {"id": 7, "nombre": "Cámaras de Seguridad", "prioridad": "alta", "estado": "ejecutando", "cpu_porcentaje": 20, "memoria_mb": 128, "creado_por": "sistema", "created_at": "2023-10-01T10:00:06"},
        {"id": 8, "nombre": "Comunicación V2X", "prioridad": "media", "estado": "listo", "cpu_porcentaje": 5, "memoria_mb": 64, "creado_por": "sistema", "created_at": "2023-10-01T10:00:07"}
    ]

def uso_cpu(supabase) -> list[dict]:
    """Retorna datos del diagrama de Gantt del uso de CPU de los últimos 60 segundos."""
    ahora = datetime.now()
    inicio_base = ahora - timedelta(seconds=60)
    
    return [
        {"proceso": "Control del Motor", "inicio": inicio_base, "fin": ahora, "estado": "ejecutando", "prioridad": "crítica"},
        {"proceso": "Sistema de Frenos ABS", "inicio": inicio_base, "fin": ahora, "estado": "ejecutando", "prioridad": "crítica"},
        {"proceso": "Cámaras de Seguridad", "inicio": inicio_base + timedelta(seconds=10), "fin": ahora - timedelta(seconds=5), "estado": "ejecutando", "prioridad": "alta"},
        {"proceso": "Climatización", "inicio": inicio_base + timedelta(seconds=20), "fin": ahora, "estado": "ejecutando", "prioridad": "media"}
    ]

def uso_cpu_total(supabase) -> float:
    """Retorna el uso total de CPU (suma de procesos activos)."""
    return 68.0

def crear_proceso(supabase, datos: dict, usuario: str) -> dict:
    """Simula la creación de un nuevo proceso."""
    nuevo_proceso = datos.copy()
    nuevo_proceso["id"] = 999
    nuevo_proceso["created_at"] = datetime.now().isoformat()
    nuevo_proceso["creado_por"] = usuario
    nuevo_proceso["estado"] = "nuevo"
    return nuevo_proceso

def listar_procesos(supabase) -> list[dict]:
    """Retorna todos los procesos, equivalente a obtener_procesos."""
    return obtener_procesos(supabase)

def cambiar_estado_proceso(supabase, proceso_id: int, nuevo_estado: str, usuario: str) -> bool:
    """Simula el cambio de estado de un proceso."""
    return True

def finalizar_proceso(supabase, proceso_id: int, usuario: str) -> bool:
    """Simula la finalización de un proceso."""
    return True
