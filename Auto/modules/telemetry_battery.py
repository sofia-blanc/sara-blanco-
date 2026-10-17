"""
====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Módulo: telemetry_battery.py
Responsable: Integrante 3 (Batería, Telemetría y Eventos Críticos)
====================================================================
Requisito de la plantilla (Fila 10):
'Dashboard: estado general -> Aporta batería y eventos críticos'
'Integrante 4: Calcula y dibuja el semáforo verde, amarillo o rojo'
"""

from typing import Dict, Any, List, Tuple
from config import get_db
from modules.devices import obtener_resumen_dispositivos

def obtener_estado_bateria() -> Dict[str, Any]:
    """Retorna los parámetros de telemetría del sistema BMS de alta tensión"""
    db = get_db()
    bateria = db["bateria"]
    
    # Determinar modo según SoC
    soc = bateria["soc_pct"]
    if soc > 25:
        modo = "Normal"
        color_modo = "NORMAL"
    elif soc > 12:
        modo = "Ahorro Energético (ECO)"
        color_modo = "ECO"
    else:
        modo = "BATERÍA CRÍTICA (Limp Mode)"
        color_modo = "CRÍTICO"
        
    bateria["modo_actual"] = modo
    bateria["color_modo"] = color_modo
    return bateria


def actualizar_bateria(soc_pct: float, temp_c: float, modo_conduccion: str = "Normal") -> Dict[str, Any]:
    """Actualiza los parámetros de batería para simulaciones en vivo"""
    db = get_db()
    bateria = db["bateria"]
    bateria["soc_pct"] = max(0.0, min(100.0, soc_pct))
    bateria["temp_c"] = temp_c
    bateria["modo_conduccion"] = modo_conduccion
    
    # Calcular voltaje proporcional
    bateria["voltaje_v"] = round(320.0 + (bateria["soc_pct"] / 100.0) * 85.0, 1)
    return bateria


def obtener_eventos_criticos_activos() -> List[Dict[str, Any]]:
    """
    Retorna los eventos no resueltos de severidad 'critico' o 'emergencia'.
    Aporte directo de Integrante 3 para el semáforo del Dashboard.
    """
    db = get_db()
    eventos = db["eventos"]
    return [e for e in eventos if not e.get("resuelto", False) and e.get("severidad") in ["critico", "emergencia"]]


def calcular_semaforo_general() -> Dict[str, Any]:
    """
    Calcula el estado general del vehículo inteligente (Semáforo Verde / Amarillo / Rojo).
    Fórmula ponderada que integra:
    1. Salud y estado del BMS de batería (Aporte Int. 3)
    2. Eventos críticos no resueltos (Aporte Int. 3)
    3. Estado y salud de sensores/actuadores (Aporte Int. 3)
    """
    bateria = obtener_estado_bateria()
    resumen_dev = obtener_resumen_dispositivos()
    eventos_criticos = obtener_eventos_criticos_activos()
    
    soc = bateria["soc_pct"]
    temp_bat = bateria["temp_c"]
    num_criticos = len(eventos_criticos)
    hay_dev_critico_falla = resumen_dev["hay_falla_critica"]
    
    # Evaluación de Estado Semáforo
    if num_criticos > 0 or hay_dev_critico_falla or soc <= 10.0 or temp_bat >= 55.0:
        color = "ROJO"
        titulo = "ESTADO CRÍTICO / EMERGENCIA"
        icono = ""
        mensaje = f"Se detectaron {num_criticos} alertas críticas o fallos de hardware críticos. Procedimiento Fail-Safe activado."
        codigo_color = "#dc2626"
    elif soc <= 25.0 or resumen_dev["degradados"] > 0 or resumen_dev["fallas"] > 0 or temp_bat >= 45.0:
        color = "AMARILLO"
        titulo = "ESTADO DE ADVERTENCIA / DEGRADADO"
        icono = ""
        mensaje = "Vehículo operando en modo de advertencia o ahorro de energía. Ciertas funciones pueden estar limitadas."
        codigo_color = "#f59e0b"
    else:
        color = "VERDE"
        titulo = "SISTEMA TOTALMENTE OPERATIVO"
        icono = ""
        mensaje = "Todos los subsistemas de AutoOS se encuentran dentro de los parámetros nominales de seguridad."
        codigo_color = "#10b981"
        
    return {
        "color": color,
        "titulo": titulo,
        "icono": icono,
        "mensaje": mensaje,
        "codigo_hex": codigo_color,
        "bateria_soc": soc,
        "temperatura_bat": temp_bat,
        "eventos_criticos_count": num_criticos,
        "eventos_criticos": eventos_criticos,
        "dispositivos_en_falla_count": resumen_dev["fallas"] + resumen_dev["desconectados"]
    }
