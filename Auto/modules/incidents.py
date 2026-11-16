"""
====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Módulo: incidents.py
Responsable: Integrante 3 (Escenarios de Falla - Fase 10 del PDF)
====================================================================
Implementa rigurosamente los 3 escenarios críticos de AutoOS:
1. Sensor Defectuoso (LiDAR 360° / Cámara ADAS)
2. Batería Baja Crítica (BMS SoC < 8% y Sobrecalentamiento)
3. Proceso Crítico / Fallo en Actuador By-Wire

Cada escenario ejecuta estrictamente el ciclo de 5 fases exigido por el PDF:
1. Detectar -> 2. Registrar -> 3. Generar alerta -> 4. Priorizar procesos -> 5. Ejecutar una respuesta
"""

from typing import Dict, Any, List, Tuple
import datetime
import uuid
from config import get_db
from modules.devices import obtener_dispositivo
from modules.telemetry_battery import actualizar_bateria

ESCENARIOS_DISPONIBLES = {
    "sensor_defectuoso": {
        "id": "sensor_defectuoso",
        "titulo": "Escenario 1: Sensor LiDAR Frontal Defectuoso",
        "dispositivo_afectado": "DEV_LIDAR_01",
        "descripcion": "Fallo de comunicación en el bus Automotive Ethernet con lecturas de nube de puntos corruptas durante la conducción."
    },
    "bateria_baja": {
        "id": "bateria_baja",
        "titulo": "Escenario 2: Batería de Tracción Crítica (SoC 6% y Térmico)",
        "dispositivo_afectado": "DEV_BATTERY_BMS",
        "descripcion": "Caída severa de voltaje en celdas de alta tensión y elevación anómala de temperatura a 56°C."
    },
    "proceso_critico": {
        "id": "proceso_critico",
        "titulo": "Escenario 3: Fallo Crítico en Actuador de Dirección By-Wire",
        "dispositivo_afectado": "DEV_ACT_STEER",
        "descripcion": "Desfase anómalo de ángulo y sobrecorriente en actuador EPS de dirección asistida con pérdida de asistencia primaria."
    }
}


def ejecutar_escenario_falla(clave_escenario: str, usuario_actual: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ejecuta el escenario crítico seleccionado y produce el informe paso a paso de las 5 fases.
    """
    db = get_db()
    timestamp_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if clave_escenario == "sensor_defectuoso":
        # 1. DETECTAR
        paso_1 = {
            "fase": "1. Detectar",
            "accion": "El módulo de diagnóstico del Kernel AutoOS detecta 87% de paquetes corruptos (Checksum CRC) en el bus Automotive Ethernet del LiDAR DEV_LIDAR_01.",
            "diagnostico": "Código DTC Automotriz: U0129-87 (Pérdida de comunicación con sensor LiDAR frontal).",
            "estado": "Alerta de I/O de Dispositivo"
        }
        
        # 2. REGISTRAR
        dev = obtener_dispositivo("DEV_LIDAR_01")
        if dev:
            dev["estado"] = "falla"
            dev["salud_porcentaje"] = 12
            
        evento_id = str(uuid.uuid4())
        evento = {
            "id": evento_id,
            "tipo_evento": "dispositivo_fallo",
            "severidad": "critico",
            "dispositivo_codigo": "DEV_LIDAR_01",
            "usuario": "Kernel AutoOS (Watchdog)",
            "mensaje": "Fallo crítico en Sensor LiDAR 360° Solid-State. Datos de telemetría fuera de tolerancia.",
            "detalles": {"dtc": "U0129-87", "crc_errors_sec": 420, "bus": "Automotive Ethernet"},
            "resuelto": False,
            "creado_en": timestamp_actual
        }
        db["eventos"].insert(0, evento)
        paso_2 = {
            "fase": "2. Registrar",
            "accion": "Se persiste el incidente en la tabla 'eventos' de Supabase y en la memoria no volátil del SO (NVM EPROM).",
            "evento_id": evento_id,
            "severidad": "CRÍTICO"
        }
        
        # 3. GENERAR ALERTA
        paso_3 = {
            "fase": "3. Generar Alerta",
            "accion": "Se envía señal CAN al Cockpit Digital para desplegar aviso ámbar/rojo en Head-Up Display: '¡Atención! LiDAR Inoperativo. Conducción autónoma restringida'.",
            "nivel_hud": "Visual y Sonoro (Chime 2.4 kHz)"
        }
        
        # 4. PRIORIZAR PROCESOS
        # Elevar adas_collision_avoidance a prioridad 0 e inhibir procesos menores
        for p in db["procesos"]:
            if p["nombre"] == "adas_collision_avoidance":
                p["prioridad"] = 0
                p["estado"] = "ejecutando"
                p["cpu"] = 28.0
            if p["nombre"] == "infotainment_media_player":
                p["cpu"] = 2.0  # Limitar cuota
        paso_4 = {
            "fase": "4. Priorizar Procesos",
            "accion": "El planificador de CPU (Scheduler) eleva el proceso 'adas_collision_avoidance' (PID 102) a tiempo real (Prioridad 0) para realizar fusión sensorial alternativa con Cámara y Radar.",
            "proceso_elevado": "PID 102 (adas_collision_avoidance) -> Prioridad 0"
        }
        
        # 5. EJECUTAR UNA RESPUESTA
        paso_5 = {
            "fase": "5. Ejecutar una Respuesta",
            "accion": "AutoOS conmuta automáticamente a 'Modo de Navegación por Visión y Radar ADAS (Fallback L2)'. Se limita la velocidad máxima a 60 km/h y se transfiere el mando activo al conductor humano.",
            "resultado": "Vehículo seguro y estabilizado sin riesgo de impacto."
        }
        
        titulo = "Fallo de Sensor LiDAR Frontal Controlado"

    elif clave_escenario == "bateria_baja":
        # 1. DETECTAR
        actualizar_bateria(soc_pct=6.5, temp_c=56.2, modo_conduccion="Limp-Mode")
        paso_1 = {
            "fase": "1. Detectar",
            "accion": "El módulo BMS (Battery Management System) reporta Estado de Carga (SoC) crítico del 6.5% con voltaje en celda 14 cayendo por debajo de 2.8V y temperatura a 56.2°C.",
            "diagnostico": "Código DTC: P0A7F-00 (Deterioro crítico de paquete de batería de alta tensión).",
            "estado": "Alerta Térmica y de Capacidad Eléctrica"
        }
        
        # 2. REGISTRAR
        dev = obtener_dispositivo("DEV_BATTERY_BMS")
        if dev:
            dev["estado"] = "degradado"
            dev["salud_porcentaje"] = 45
            
        evento_id = str(uuid.uuid4())
        evento = {
            "id": evento_id,
            "tipo_evento": "bateria_critica",
            "severidad": "emergencia",
            "dispositivo_codigo": "DEV_BATTERY_BMS",
            "usuario": "Kernel AutoOS (BMS Daemon)",
            "mensaje": "Batería de tracción en nivel crítico (6.5%). Activación inmediata de protocolo de preservación energética.",
            "detalles": {"soc_pct": 6.5, "temp_max_celda": 56.2, "voltaje_v": 325.5},
            "resuelto": False,
            "creado_en": timestamp_actual
        }
        db["eventos"].insert(0, evento)
        paso_2 = {
            "fase": "2. Registrar",
            "accion": "Registro del evento de emergencia en la tabla 'eventos' de Supabase y registro de telemetría de celdas en el log del vehículo.",
            "evento_id": evento_id,
            "severidad": "EMERGENCIA"
        }
        
        # 3. GENERAR ALERTA
        paso_3 = {
            "fase": "3. Generar Alerta",
            "accion": "Notificación emergente en el clúster de instrumentos: '¡Batería Crítica! Conduzca de inmediato a una estación de recarga rápida'.",
            "nivel_hud": "Icono Tortuga activado + Notificación en Tablero"
        }
        
        # 4. PRIORIZAR PROCESOS
        # Suspender multimedia y climatizador
        for p in db["procesos"]:
            if p["nombre"] in ["infotainment_media_player", "voice_assistant_agent"]:
                p["estado"] = "bloqueado"
                p["cpu"] = 0.0
            if p["nombre"] == "hvac_thermal_controller":
                p["cpu"] = 0.2
            if p["nombre"] == "bms_thermal_monitor":
                p["prioridad"] = 0
                p["cpu"] = 12.0
        paso_4 = {
            "fase": "4. Priorizar Procesos",
            "accion": "El Kernel suspende procesos de confort ('infotainment_media_player', 'voice_assistant_agent') y otorga CPU prioritaria a 'bms_thermal_monitor' para regular bombas de refrigeración líquida.",
            "procesos_suspendidos": "PID 107 (Infotainment), PID 108 (Voice Agent)"
        }
        
        # 5. EJECUTAR UNA RESPUESTA
        paso_5 = {
            "fase": "5. Ejecutar una Respuesta",
            "accion": "Se corta la alimentación de inversores auxiliares, se limita la entrega de potencia motriz al 25% y el motor de navegación recalcula la ruta al cargador CCS más próximo (distancia estimada: 2.1 km).",
            "resultado": "Batería protegida contra descarga profunda y vehículo en marcha hacia cargador."
        }
        
        titulo = "Protocolo de Emergencia por Batería Crítica Ejecutado"

    else:  # proceso_critico (Fallo en Dirección By-Wire)
        # 1. DETECTAR
        paso_1 = {
            "fase": "1. Detectar",
            "accion": "El proceso crítico de dirección reporta timeout de 80ms y desacople angular entre el encoder de dirección y el motor servo By-Wire (DEV_ACT_STEER).",
            "diagnostico": "Código DTC: C0051-4B (Error interno de actuador de dirección asistida electrónica).",
            "estado": "Fallo en Subsistema Crítico de Seguridad Dinámica"
        }
        
        # 2. REGISTRAR
        dev = obtener_dispositivo("DEV_ACT_STEER")
        if dev:
            dev["estado"] = "falla"
            dev["salud_porcentaje"] = 10
            
        evento_id = str(uuid.uuid4())
        evento = {
            "id": evento_id,
            "tipo_evento": "dispositivo_fallo",
            "severidad": "emergencia",
            "dispositivo_codigo": "DEV_ACT_STEER",
            "usuario": "Safety Integrity Monitor (ASIL-D)",
            "mensaje": "Fallo crítico en Actuador de Dirección Asistida (EPS By-Wire). Conmutando a redundancia.",
            "detalles": {"dtc": "C0051-4B", "redundancia": "Canal_B_Activado"},
            "resuelto": False,
            "creado_en": timestamp_actual
        }
        db["eventos"].insert(0, evento)
        paso_2 = {
            "fase": "2. Registrar",
            "accion": "El kernel registra el fallo ASIL-D en la base de datos de eventos y en la caja negra del vehículo.",
            "evento_id": evento_id,
            "severidad": "EMERGENCIA CRÍTICA"
        }
        
        # 3. GENERAR ALERTA
        paso_3 = {
            "fase": "3. Generar Alerta",
            "accion": "Alerta visual roja fija en pantalla con sonido continuo de advertencia y vibración en el aro del volante: '¡Fallo de Dirección! Sujete el volante firmemente'.",
            "nivel_hud": "HUD Rojo Parpadeante + Alarma Háptica"
        }
        
        # 4. PRIORIZAR PROCESOS
        for p in db["procesos"]:
            if p["nombre"] == "adas_collision_avoidance":
                p["prioridad"] = 0
                p["cpu"] = 35.0
            if p["critico"]:
                p["prioridad"] = 0
        paso_4 = {
            "fase": "4. Priorizar Procesos",
            "accion": "El Scheduler asigna prioridad absoluta (Prioridad 0) a las rutinas de frenado y dirección vectorial por control diferencial de neumáticos.",
            "politica": "Aislamiento de hilos no seguros e hiper-prioridad a actuadores de frenado"
        }
        
        # 5. EJECUTAR UNA RESPUESTA
        paso_5 = {
            "fase": "5. Ejecutar una Respuesta",
            "accion": "AutoOS activa el canal de dirección secundario de respaldo (Redundancia Fail-Operational) y aplica frenado selectivo ESC para mantener el vehículo centrado en el carril hasta una detención segura (Safe Stop).",
            "resultado": "Vehículo detenido de manera controlada y segura en la berma."
        }
        
        titulo = "Respuesta Fail-Safe en Dirección By-Wire Ejecutada"

    return {
        "clave": clave_escenario,
        "titulo": titulo,
        "pasos": [paso_1, paso_2, paso_3, paso_4, paso_5],
        "hora_ejecucion": timestamp_actual
    }


def restablecer_sistema_a_normal(usuario_actual: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Restaura todos los dispositivos, batería y procesos a su estado normal operativo.
    Requiere rol de Mecánico/Admin.
    """
    from modules.auth_security import validar_accion, registrar_evento_seguridad
    
    autorizado, msg_rechazo = validar_accion(usuario_actual, "seguridad.admin_usuarios", recurso="sistema_global")
    if not autorizado:
        return False, msg_rechazo
        
    db = get_db()
    # Restablecer dispositivos
    for dev in db["dispositivos"]:
        dev["estado"] = "operativo"
        dev["salud_porcentaje"] = 96
        
    # Restablecer batería
    actualizar_bateria(soc_pct=84.0, temp_c=31.5, modo_conduccion="Normal")
    
    # Marcar eventos críticos como resueltos
    for ev in db["eventos"]:
        ev["resuelto"] = True
        
    # Restablecer procesos
    for p in db["procesos"]:
        if p["estado"] == "bloqueado":
            p["estado"] = "ejecutando"
        if p["nombre"] == "infotainment_media_player":
            p["cpu"] = 8.4
        elif p["nombre"] == "voice_assistant_agent":
            p["cpu"] = 2.0
            p["estado"] = "listo"
            
    registrar_evento_seguridad(
        tipo="cambio_estado_so",
        severidad="info",
        mensaje=f"Sistema AutoOS totalmente restablecido a parámetros nominales por {usuario_actual.get('nombre_completo')}."
    )
    
    return True, "Sistema AutoOS restablecido con éxito. Todos los subsistemas operan en Verde."
