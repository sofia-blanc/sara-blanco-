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
    """
    Retorna los parámetros de telemetría del sistema BMS de alta tensión.
    Integra el perfil de conducción vehicular (Eco, Normal, Sport) y
    calcula autonomía en km, límite de potencia del inversor, consumo y perfil térmico.
    """
    db = get_db()
    bateria = db["bateria"]
    
    soc = float(bateria.get("soc_pct", 78.5))
    temp_c = float(bateria.get("temp_c", 31.5))
    modo_sel = bateria.get("modo_conduccion", "Normal")
    
    # Paquete de 75 kWh nominal
    capacidad_kwh = 75.0
    energia_disponible_kwh = (soc / 100.0) * capacidad_kwh
    
    # Si la batería está en nivel crítico (<= 12%), se activa Limp Mode de emergencia
    if soc <= 12.0:
        modo_activo = "CRÍTICO (Limp Mode Forzado)"
        color_modo = "CRÍTICO"
        consumo_kwh_100km = 12.0
        limite_potencia_kw = 45.0
        corriente_tipica_a = 16.0
        perfil_hvac = "Desactivado (Solo Ventilación de Emergencia)"
        curva_torque = "Restringida al 30% (Protección de Celdas)"
        regeneracion = "Máxima (Frenado Regenerativo Forzado)"
    elif modo_sel == "Eco":
        modo_activo = "ECO (Ahorro Energético)"
        color_modo = "ECO"
        consumo_kwh_100km = 13.5
        limite_potencia_kw = 75.0
        corriente_tipica_a = 24.5
        perfil_hvac = "Modo Ahorro (0.8 kW - Confort Térmico Eco)"
        curva_torque = "Suave / Progresiva (Ahorro de Carga)"
        regeneracion = "Alta (One-Pedal Drive +25% Regeneración)"
    elif modo_sel == "Sport":
        modo_activo = "SPORT (Alto Rendimiento)"
        color_modo = "SPORT"
        consumo_kwh_100km = 22.0
        limite_potencia_kw = 240.0
        corriente_tipica_a = 78.0
        perfil_hvac = "Prioridad Refrigeración de Inversor y Batería"
        curva_torque = "Agresiva / Dynamic Boost (100% Par Inmediato)"
        regeneracion = "Baja (Inercia Dinámica para Pista)"
    else:  # Normal
        modo_activo = "NORMAL (Balance Dinámico)"
        color_modo = "NORMAL"
        consumo_kwh_100km = 16.5
        limite_potencia_kw = 150.0
        corriente_tipica_a = 42.0
        perfil_hvac = "Automático / Confort Equilibrado (1.5 kW)"
        curva_torque = "Lineal Equilibrada"
        regeneracion = "Estándar (Nivel 2 de Regeneración)"

    autonomia_km = round((energia_disponible_kwh / consumo_kwh_100km) * 100.0, 1)
    autonomia_nominal = round(((soc / 100.0) * capacidad_kwh / 16.5) * 100.0, 1)
    delta_autonomia = round(autonomia_km - autonomia_nominal, 1)

    bateria["modo_actual"] = modo_activo
    bateria["color_modo"] = color_modo
    bateria["modo_conduccion"] = modo_sel
    bateria["autonomia_km"] = autonomia_km
    bateria["delta_autonomia"] = delta_autonomia
    bateria["limite_potencia_kw"] = limite_potencia_kw
    bateria["consumo_kwh_100km"] = consumo_kwh_100km
    bateria["corriente_a"] = corriente_tipica_a
    bateria["perfil_hvac"] = perfil_hvac
    bateria["curva_torque"] = curva_torque
    bateria["regeneracion"] = regeneracion
    bateria["voltaje_v"] = round(320.0 + (soc / 100.0) * 85.0, 1)
    bateria["potencia_kw"] = round((bateria["voltaje_v"] * corriente_tipica_a) / 1000.0, 1)
    return bateria


def actualizar_bateria(soc_pct: float, temp_c: float, modo_conduccion: str = "Normal") -> Dict[str, Any]:
    """Actualiza los parámetros de batería para simulaciones en vivo y perfiles de conducción"""
    db = get_db()
    bateria = db["bateria"]
    bateria["soc_pct"] = max(0.0, min(100.0, float(soc_pct)))
    bateria["temp_c"] = float(temp_c)
    if modo_conduccion:
        bateria["modo_conduccion"] = modo_conduccion
    
    return obtener_estado_bateria()


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
