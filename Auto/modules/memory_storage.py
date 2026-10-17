"""
====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Módulo: memory_storage.py
Responsable: Integración con Int. 2 (Memoria, Archivos y Logs)
====================================================================
Implementa los requisitos asignados a Int. 2 en la matriz:
- RAM total simulada (16 GB), bloques asignados y liberados
- Carpetas base del vehículo (/config, /logs, /media, /maps, /telemetry)
- Registro y consulta de logs de sistema (DEBUG, INFO, WARN, ERROR, FATAL)
"""

from typing import Dict, Any, List
import datetime
from config import get_db

MEMORIA_TOTAL_MB = 16384  # 16 GB de RAM simulada
ALMACENAMIENTO_TOTAL_GB = 512  # SSD automotriz de 512 GB

def obtener_uso_memoria() -> Dict[str, Any]:
    """Retorna métricas de memoria RAM del vehículo inteligente"""
    db = get_db()
    procesos = db["procesos"]
    
    memoria_usada_procesos = sum(p["mem_mb"] for p in procesos if p["estado"] in ["ejecutando", "listo", "bloqueado"])
    memoria_kernel = 2048  # 2 GB reservados para Kernel y RTOS
    memoria_usada_total = memoria_usada_procesos + memoria_kernel
    memoria_libre = max(0, MEMORIA_TOTAL_MB - memoria_usada_total)
    pct_usado = round((memoria_usada_total / MEMORIA_TOTAL_MB) * 100, 1)
    
    return {
        "total_mb": MEMORIA_TOTAL_MB,
        "usado_mb": memoria_usada_total,
        "libre_mb": memoria_libre,
        "kernel_mb": memoria_kernel,
        "procesos_mb": memoria_usada_procesos,
        "pct_usado": pct_usado
    }


def obtener_sistema_archivos() -> List[Dict[str, Any]]:
    """Estructura de archivos y directorios del vehículo inteligente"""
    return [
        {"ruta": "/config/vehicle_params.json", "carpeta": "/config", "tipo": "Configuración", "tamano_kb": 12, "permisos": "0600 (Mecánico)", "descripcion": "Constantes de calibración de dirección, frenado y torque"},
        {"ruta": "/config/adas_network_weights.bin", "carpeta": "/config", "tipo": "Modelo IA", "tamano_kb": 184000, "permisos": "0444 (Lectura)", "descripcion": "Pesos de la red neuronal convolucional de visión artificial"},
        {"ruta": "/maps/bogota_hd_map.osm", "carpeta": "/maps", "tipo": "Cartografía HD", "tamano_kb": 42000, "permisos": "0644 (Conductor)", "descripcion": "Nube de carriles y geometría vial de alta resolución"},
        {"ruta": "/media/playlist_roadtrip.flac", "carpeta": "/media", "tipo": "Multimedia", "tamano_kb": 28000, "permisos": "0777 (Todos)", "descripcion": "Música y podcasts en streaming para pasajeros"},
        {"ruta": "/logs/can_bus_traffic.log", "carpeta": "/logs", "tipo": "Log de Red", "tamano_kb": 8400, "permisos": "0640 (Admin/User)", "descripcion": "Trazas de tramas de comunicación CAN-Bus"},
        {"ruta": "/logs/safety_events.bin", "carpeta": "/logs", "tipo": "Caja Negra", "tamano_kb": 1500, "permisos": "0400 (Solo Root)", "descripcion": "Registro inmutable de aceleraciones y eventos pre-colisión"}
    ]


def obtener_logs_sistema(limite: int = 20) -> List[Dict[str, Any]]:
    """Genera y retorna trazas de log del sistema operativo vehicular"""
    db = get_db()
    logs = [
        {"hora": "23:00:01", "nivel": "INFO", "modulo": "KERNEL", "mensaje": "Inicializando capas de seguridad vehicular AutoOS v2.4."},
        {"hora": "23:00:03", "nivel": "INFO", "modulo": "DISPOSITIVOS", "mensaje": "Enumerando buses CAN 2.0B y Automotive Ethernet 100BASE-T1."},
        {"hora": "23:00:04", "nivel": "INFO", "modulo": "BMS", "mensaje": "Batería LiFePO4 detectada: 96 celdas balanceadas a 3.98V."},
        {"hora": "23:01:12", "nivel": "WARN", "modulo": "HVAC", "mensaje": "Presión diferencial en cabina detecta filtro de habitáculo al 70%."},
        {"hora": "23:02:45", "nivel": "INFO", "modulo": "SEGURIDAD", "mensaje": "Autenticación satisfactoria de usuario con rol Conductor."},
        {"hora": "23:04:10", "nivel": "DEBUG", "modulo": "SCHEDULER", "mensaje": "Asignando quantum de 4ms a proceso adas_collision_avoidance."}
    ]
    
    # Concatenar con los eventos recientes de la BD
    for ev in db["eventos"][:5]:
        nivel_map = {"info": "INFO", "advertencia": "WARN", "critico": "ERROR", "emergencia": "FATAL"}
        logs.insert(0, {
            "hora": ev.get("creado_en", "")[-8:],
            "nivel": nivel_map.get(ev.get("severidad"), "INFO"),
            "modulo": "EVENT_ENGINE",
            "mensaje": ev.get("mensaje", "")
        })
    return logs[:limite]
