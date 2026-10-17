"""
====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Módulo: processes.py
Responsable: Integración con Int. 1 y Validación de Seguridad Int. 3
====================================================================
Requisitos de la plantilla:
- Procesos: crear -> 'Permiso necesario para crear' (Int. 3)
- Procesos: cambiar estado -> 'Valida que el rol pueda hacerlo' (Int. 3)
- Procesos: finalizar -> 'Valida que el rol pueda hacerlo' (Int. 3)
- Demuestra control de acceso granular por rol (RBAC) en el ciclo de vida de procesos
"""

from typing import List, Dict, Any, Tuple, Optional
import datetime
import random
from config import get_db
from modules.auth_security import validar_accion, registrar_evento_seguridad

def obtener_procesos() -> List[Dict[str, Any]]:
    """Retorna la lista de procesos automotrices en el sistema"""
    db = get_db()
    return db["procesos"]


def obtener_proceso(pid: int) -> Optional[Dict[str, Any]]:
    """Busca un proceso por su PID"""
    db = get_db()
    for p in db["procesos"]:
        if p["pid"] == pid:
            return p
    return None


def crear_proceso(nombre: str, prioridad: int, cpu_est: float, mem_mb: int, es_critico: bool, usuario_actual: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Crea un nuevo proceso en AutoOS.
    Requisito estricto de Int. 3: 'Permiso necesario para crear'
    """
    autorizado, msg_rechazo = validar_accion(usuario_actual, "proceso.crear", recurso=f"proceso:{nombre}")
    if not autorizado:
        return False, msg_rechazo
        
    db = get_db()
    
    # Generar PID único
    pids_existentes = [p["pid"] for p in db["procesos"]]
    nuevo_pid = max(pids_existentes) + 1 if pids_existentes else 100
    
    # Validar si un no-mecánico intenta crear proceso de tiempo real 0
    if prioridad == 0 and not validar_accion(usuario_actual, "proceso.priorizar_tiempo_real", recurso="scheduler_rt")[0]:
        prioridad = 1  # Forzar a prioridad no-kernel
        
    nuevo_proceso = {
        "pid": nuevo_pid,
        "nombre": nombre,
        "estado": "listo",
        "prioridad": prioridad,
        "cpu": cpu_est,
        "mem_mb": mem_mb,
        "critico": es_critico,
        "creado_por": usuario_actual.get("id")
    }
    db["procesos"].append(nuevo_proceso)
    
    registrar_evento_seguridad(
        tipo="cambio_estado_so",
        severidad="info",
        mensaje=f"Proceso '{nombre}' (PID {nuevo_pid}) creado con éxito por {usuario_actual.get('nombre_completo')}."
    )
    
    return True, f"Proceso '{nombre}' (PID {nuevo_pid}) creado en estado 'Listo'."


def cambiar_estado_proceso(pid: int, nuevo_estado: str, usuario_actual: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Pausa o reanuda un proceso.
    Requisito estricto de Int. 3: 'Valida que el rol pueda hacerlo'
    """
    autorizado, msg_rechazo = validar_accion(usuario_actual, "proceso.cambiar_estado", recurso=f"proceso:pid_{pid}")
    if not autorizado:
        return False, msg_rechazo
        
    proc = obtener_proceso(pid)
    if not proc:
        return False, f"Proceso con PID {pid} no encontrado."
        
    if proc.get("critico") and usuario_actual.get("rol") != "admin":
        msg_denegado = f"Proceso crítico '{proc['nombre']}' solo puede ser alterado por un Mecánico (Admin)."
        validar_accion(usuario_actual, "seguridad.admin_usuarios", recurso=f"proceso_critico:{pid}")
        return False, msg_denegado
        
    estado_anterior = proc["estado"]
    proc["estado"] = nuevo_estado
    
    # Registro formal en procesos_historial (Int. 1)
    db = get_db()
    if "procesos_historial" not in db:
        db["procesos_historial"] = []
    db["procesos_historial"].append({
        "proceso_id": pid,
        "proceso_nombre": proc["nombre"],
        "estado_anterior": estado_anterior,
        "estado_nuevo": nuevo_estado,
        "cambiado_por": usuario_actual.get("id"),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Registro formal en logs (Int. 2)
    if "logs" not in db:
        db["logs"] = []
    db["logs"].append({
        "nivel": "INFO",
        "modulo": "PROCESSES",
        "mensaje": f"Transición de estado: PID {pid} ({proc['nombre']}) de [{estado_anterior.upper()}] a [{nuevo_estado.upper()}].",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })
    
    registrar_evento_seguridad(
        tipo="cambio_estado_so",
        severidad="info",
        mensaje=f"Proceso PID {pid} ({proc['nombre']}) cambió de [{estado_anterior.upper()}] a [{nuevo_estado.upper()}] por {usuario_actual.get('nombre_completo')}."
    )
    
    return True, f"Proceso PID {pid} ahora se encuentra en estado '{nuevo_estado}'."


def finalizar_proceso(pid: int, usuario_actual: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Termina un proceso automotriz (SIGKILL).
    Requisito estricto de Int. 3: 'Valida que el rol pueda hacerlo'
    Requisito de Int. 2: 'Libera la memoria del proceso'
    """
    autorizado, msg_rechazo = validar_accion(usuario_actual, "proceso.finalizar", recurso=f"proceso:pid_{pid}")
    if not autorizado:
        return False, msg_rechazo
        
    proc = obtener_proceso(pid)
    if not proc:
        return False, f"Proceso con PID {pid} no existe."
        
    if proc.get("critico") and usuario_actual.get("rol") != "admin":
        msg_critico = f"¡ACCESO DENEGADO! El proceso '{proc['nombre']}' es vital para la seguridad del vehículo (ASIL-D). Solo el Mecánico con credenciales de nivel 10 puede abortarlo."
        # Registrar violación en auditoría
        validar_accion(usuario_actual, "seguridad.admin_usuarios", recurso=f"kill_proceso_critico:{pid}")
        return False, msg_critico
        
    db = get_db()
    memoria_liberada_mb = proc.get("mem_mb", 0)
    
    # Remover proceso de la lista activa (libera CPU y RAM automáticamente)
    db["procesos"] = [p for p in db["procesos"] if p["pid"] != pid]
    
    # Registro formal en procesos_historial (Int. 1)
    if "procesos_historial" not in db:
        db["procesos_historial"] = []
    db["procesos_historial"].append({
        "proceso_id": pid,
        "proceso_nombre": proc["nombre"],
        "estado_anterior": proc["estado"],
        "estado_nuevo": "terminado",
        "cambiado_por": usuario_actual.get("id"),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Registro formal en logs y liberación de memoria (Int. 2)
    if "logs" not in db:
        db["logs"] = []
    db["logs"].append({
        "nivel": "WARN" if proc.get("critico") else "INFO",
        "modulo": "MEMORY",
        "mensaje": f"Proceso PID {pid} terminado. Se liberaron {memoria_liberada_mb} MB de RAM.",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })
    
    registrar_evento_seguridad(
        tipo="cambio_estado_so",
        severidad="advertencia" if proc.get("critico") else "info",
        mensaje=f"Proceso PID {pid} ({proc['nombre']}) finalizado (terminado) por {usuario_actual.get('nombre_completo')}. Memoria liberada: {memoria_liberada_mb} MB."
    )
    
    return True, f"Proceso PID {pid} ({proc['nombre']}) finalizado exitosamente. Se liberaron {memoria_liberada_mb} MB de memoria RAM."


def calcular_uso_cpu_total() -> float:
    """Calcula el uso acumulado de CPU de todos los procesos activos"""
    procesos = obtener_procesos()
    return round(sum(p["cpu"] for p in procesos if p["estado"] == "ejecutando"), 1)
