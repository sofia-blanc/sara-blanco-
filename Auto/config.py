"""
====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Módulo de Configuración y Conexión a Base de Datos (Supabase / Mock Engine)
Responsable: Integrante 3 (Seguridad, Dispositivos y RLS)
====================================================================
"""

import os
import streamlit as st
from typing import Dict, Any, List, Optional
import datetime
import uuid

# Intentar importar cliente oficial de Supabase
try:
    from supabase import create_client, Client
    HAS_SUPABASE_LIB = True
except ImportError:
    HAS_SUPABASE_LIB = False
    Client = Any

# Inicialización de estado en Streamlit
def _inicializar_mock_db():
    if "autoos_db" not in st.session_state:
        # Semillas iniciales en memoria
        roles_data = [
            {"id": "11111111-1111-1111-1111-111111111111", "nombre": "admin", "descripcion": "Mecánico / Ingeniero de Servicio (Acceso Total)", "nivel_privilegio": 10},
            {"id": "22222222-2222-2222-2222-222222222222", "nombre": "user", "descripcion": "Conductor Autorizado (Control de Conducción y Rutas)", "nivel_privilegio": 5},
            {"id": "33333333-3333-3333-3333-333333333333", "nombre": "guest", "descripcion": "Pasajero / Invitado en Cabina (Acceso Restringido)", "nivel_privilegio": 1}
        ]
        
        permisos_data = [
            {"id": "p01", "clave": "proceso.crear", "modulo": "procesos", "descripcion": "Iniciar nuevos procesos vehiculares"},
            {"id": "p02", "clave": "proceso.listar", "modulo": "procesos", "descripcion": "Listar procesos del sistema"},
            {"id": "p03", "clave": "proceso.cambiar_estado", "modulo": "procesos", "descripcion": "Pausar o reanudar procesos"},
            {"id": "p04", "clave": "proceso.finalizar", "modulo": "procesos", "descripcion": "Terminar procesos en ejecución"},
            {"id": "p05", "clave": "proceso.priorizar_tiempo_real", "modulo": "procesos", "descripcion": "Elevar a prioridad Real-Time 0"},
            {"id": "p06", "clave": "dispositivo.consultar", "modulo": "dispositivos", "descripcion": "Consultar estado de sensores y actuadores"},
            {"id": "p07", "clave": "dispositivo.calibrar", "modulo": "dispositivos", "descripcion": "Calibrar sensores LiDAR / Cámaras ADAS"},
            {"id": "p08", "clave": "dispositivo.desconectar", "modulo": "dispositivos", "descripcion": "Desconectar periférico del bus CAN"},
            {"id": "p09", "clave": "dispositivo.inyectar_fallo", "modulo": "dispositivos", "descripcion": "Inyectar fallo de hardware en pruebas"},
            {"id": "p10", "clave": "seguridad.admin_usuarios", "modulo": "seguridad", "descripcion": "Administrar usuarios y roles"},
            {"id": "p11", "clave": "seguridad.ver_auditoria", "modulo": "seguridad", "descripcion": "Ver logs de intentos no autorizados"},
            {"id": "p12", "clave": "telemetria.ver_bateria", "modulo": "energia", "descripcion": "Monitorear estado BMS y celdas"},
            {"id": "p13", "clave": "telemetria.modo_eco", "modulo": "energia", "descripcion": "Modificar perfiles de ahorro energético"}
        ]
        
        roles_permisos = {
            "admin": [p["clave"] for p in permisos_data],
            "user": [
                "proceso.crear", "proceso.listar", "proceso.cambiar_estado", "proceso.finalizar",
                "dispositivo.consultar", "telemetria.ver_bateria", "telemetria.modo_eco"
            ],
            "guest": [
                "proceso.listar", "dispositivo.consultar", "telemetria.ver_bateria"
            ]
        }
        
        perfiles_data = [
            {"id": "usr_mecanico_01", "email": "mecanico@autoos.tech", "nombre_completo": "Carlos Vélez (Ing. Mecánico)", "rol": "admin", "activo": True},
            {"id": "usr_conductor_01", "email": "conductor@autoos.tech", "nombre_completo": "Laura Gómez (Conductora Principal)", "rol": "user", "activo": True},
            {"id": "usr_pasajero_01", "email": "pasajero@autoos.tech", "nombre_completo": "Andrés Rivera (Pasajero Cabina Trasera)", "rol": "guest", "activo": True}
        ]
        
        dispositivos_data = [
            {
                "id": "dev_01", "codigo": "DEV_GPS_01", "nombre": "Receptor GNSS / GPS Diferencial",
                "tipo": "sensor", "sub_sistema": "Navegación", "estado": "operativo", "salud_porcentaje": 98,
                "puerto_bus": "CAN-Bus Principal", "nivel_critico": "esencial",
                "datos_telemetria": {"satelites": 14, "hdop": 0.8, "lat": 4.6097, "lon": -74.0817, "frecuencia_hz": 10}
            },
            {
                "id": "dev_02", "codigo": "DEV_CAM_FRONT", "nombre": "Cámara Estereoscópica ADAS Frontal",
                "tipo": "sensor", "sub_sistema": "Visión Artificial", "estado": "operativo", "salud_porcentaje": 95,
                "puerto_bus": "Automotive Ethernet", "nivel_critico": "critico",
                "datos_telemetria": {"fps": 60, "resolucion": "1080p", "temp_c": 42.5, "oclusion": False}
            },
            {
                "id": "dev_03", "codigo": "DEV_LIDAR_01", "nombre": "Sensor LiDAR 360° Solid-State",
                "tipo": "sensor", "sub_sistema": "Detección Obstáculos", "estado": "operativo", "salud_porcentaje": 99,
                "puerto_bus": "Automotive Ethernet", "nivel_critico": "critico",
                "datos_telemetria": {"puntos_seg": 1200000, "rango_max_m": 200, "rpm": 600}
            },
            {
                "id": "dev_04", "codigo": "DEV_RADAR_01", "nombre": "Radar Milimétrico 77GHz (ACC)",
                "tipo": "sensor", "sub_sistema": "Control Crucero ADAS", "estado": "operativo", "salud_porcentaje": 94,
                "puerto_bus": "CAN-Bus ADAS", "nivel_critico": "critico",
                "datos_telemetria": {"objetos_trackeados": 8, "distancia_m": 35.4, "vel_relativa_kmh": -2.1}
            },
            {
                "id": "dev_05", "codigo": "DEV_BATTERY_BMS", "nombre": "BMS - Batería LiFePO4 Alta Tensión",
                "tipo": "potencia", "sub_sistema": "Tren Motriz", "estado": "operativo", "salud_porcentaje": 92,
                "puerto_bus": "CAN-Bus Principal", "nivel_critico": "critico",
                "datos_telemetria": {"soc_pct": 82, "voltaje_v": 398.2, "corriente_a": 42.0, "temp_c": 31.5, "soh_pct": 96}
            },
            {
                "id": "dev_06", "codigo": "DEV_ACT_BRAKE", "nombre": "Actuador Frenado By-Wire EBS",
                "tipo": "actuador", "sub_sistema": "Seguridad Dinámica", "estado": "operativo", "salud_porcentaje": 100,
                "puerto_bus": "CAN-Bus ADAS", "nivel_critico": "critico",
                "datos_telemetria": {"presion_bar": 0.0, "latencia_ms": 12, "redundancia": "dual_activa"}
            },
            {
                "id": "dev_07", "codigo": "DEV_ACT_STEER", "nombre": "Actuador Dirección Eléctrica EPS",
                "tipo": "actuador", "sub_sistema": "Seguridad Dinámica", "estado": "operativo", "salud_porcentaje": 97,
                "puerto_bus": "CAN-Bus ADAS", "nivel_critico": "critico",
                "datos_telemetria": {"angulo_deg": 0.4, "torque_nm": 1.1, "asistencia": "activa"}
            },
            {
                "id": "dev_08", "codigo": "DEV_COM_V2X", "nombre": "Módulo Telemetría 5G / V2X Cloud",
                "tipo": "comunicacion", "sub_sistema": "Conectividad", "estado": "operativo", "salud_porcentaje": 91,
                "puerto_bus": "Automotive Ethernet", "nivel_critico": "esencial",
                "datos_telemetria": {"latencia_ms": 19, "senal_dbm": -67, "enlace": "supabase_cloud"}
            },
            {
                "id": "dev_09", "codigo": "DEV_HVAC_CLIMA", "nombre": "Climatización y Gestión Térmica",
                "tipo": "actuador", "sub_sistema": "Confort Cabina", "estado": "operativo", "salud_porcentaje": 88,
                "puerto_bus": "LIN-Bus Confort", "nivel_critico": "confort",
                "datos_telemetria": {"temp_cabina_c": 21.5, "setpoint_c": 21.0, "compresor_pct": 30}
            },
            {
                "id": "dev_10", "codigo": "DEV_INFOTAINMENT", "nombre": "Pantalla Central Cockpit & Audio",
                "tipo": "multimedia", "sub_sistema": "Infoentretenimiento", "estado": "operativo", "salud_porcentaje": 96,
                "puerto_bus": "LIN-Bus Confort", "nivel_critico": "confort",
                "datos_telemetria": {"brillo_pct": 75, "audio_vol_pct": 35, "reproduciendo": "Nav & Podcast"}
            }
        ]
        
        procesos_data = [
            {"pid": 101, "nombre": "bms_thermal_monitor", "estado": "ejecutando", "prioridad": 0, "cpu": 4.2, "mem_mb": 128, "critico": True, "creado_por": "usr_mecanico_01"},
            {"pid": 102, "nombre": "adas_collision_avoidance", "estado": "ejecutando", "prioridad": 0, "cpu": 18.5, "mem_mb": 512, "critico": True, "creado_por": "usr_mecanico_01"},
            {"pid": 103, "nombre": "can_bus_gateway_daemon", "estado": "ejecutando", "prioridad": 1, "cpu": 3.1, "mem_mb": 96, "critico": True, "creado_por": "usr_mecanico_01"},
            {"pid": 104, "nombre": "gnss_navigation_engine", "estado": "listo", "prioridad": 3, "cpu": 5.0, "mem_mb": 256, "critico": False, "creado_por": "usr_conductor_01"},
            {"pid": 105, "nombre": "telemetry_cloud_sync", "estado": "listo", "prioridad": 4, "cpu": 2.8, "mem_mb": 180, "critico": False, "creado_por": "usr_conductor_01"},
            {"pid": 106, "nombre": "hvac_thermal_controller", "estado": "ejecutando", "prioridad": 6, "cpu": 1.5, "mem_mb": 64, "critico": False, "creado_por": "usr_conductor_01"},
            {"pid": 107, "nombre": "infotainment_media_player", "estado": "ejecutando", "prioridad": 7, "cpu": 8.4, "mem_mb": 420, "critico": False, "creado_por": "usr_conductor_01"},
            {"pid": 108, "nombre": "voice_assistant_agent", "estado": "bloqueado", "prioridad": 8, "cpu": 2.0, "mem_mb": 310, "critico": False, "creado_por": "usr_conductor_01"}
        ]
        
        eventos_data = [
            {
                "id": str(uuid.uuid4()), "tipo_evento": "cambio_estado_so", "severidad": "info",
                "dispositivo_codigo": None, "usuario": "Sistema",
                "mensaje": "Kernel AutoOS 2.4 arrancado exitosamente en ECU principal.",
                "detalles": {"boot_time_ms": 420, "kernel": "AutoOS-RT-2.4.1"},
                "resuelto": True, "creado_en": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": str(uuid.uuid4()), "tipo_evento": "seguridad", "severidad": "info",
                "dispositivo_codigo": None, "usuario": "Sistema",
                "mensaje": "Políticas de seguridad RLS inicializadas y validadas con 3 roles.",
                "detalles": {"roles": 3, "permisos": 13},
                "resuelto": True, "creado_en": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
        
        auditoria_data = [
            {
                "id": str(uuid.uuid4()), "usuario_email": "mecanico@autoos.tech", "rol": "admin",
                "recurso": "dispositivos", "accion": "dispositivo.calibrar", "autorizado": True,
                "motivo_rechazo": None, "hora": datetime.datetime.now().strftime("%H:%M:%S")
            },
            {
                "id": str(uuid.uuid4()), "usuario_email": "conductor@autoos.tech", "rol": "user",
                "recurso": "procesos", "accion": "proceso.crear", "autorizado": True,
                "motivo_rechazo": None, "hora": datetime.datetime.now().strftime("%H:%M:%S")
            },
            {
                "id": str(uuid.uuid4()), "usuario_email": "pasajero@autoos.tech", "rol": "guest",
                "recurso": "procesos", "accion": "proceso.finalizar", "autorizado": False,
                "motivo_rechazo": "Rol GUEST no tiene permiso para terminar procesos del SO vehicular (403 Forbidden)",
                "hora": datetime.datetime.now().strftime("%H:%M:%S")
            }
        ]
        
        st.session_state["autoos_db"] = {
            "roles": roles_data,
            "permisos": permisos_data,
            "roles_permisos": roles_permisos,
            "perfiles": perfiles_data,
            "dispositivos": dispositivos_data,
            "procesos": procesos_data,
            "procesos_historial": [
                {
                    "proceso_id": 101, "proceso_nombre": "bms_thermal_monitor",
                    "estado_anterior": "nuevo", "estado_nuevo": "ejecutando",
                    "cambiado_por": "usr_mecanico_01", "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    "proceso_id": 102, "proceso_nombre": "adas_collision_avoidance",
                    "estado_anterior": "listo", "estado_nuevo": "ejecutando",
                    "cambiado_por": "usr_mecanico_01", "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            ],
            "memoria_config": {
                "ram_total_mb": 16384,
                "kernel_reservado_mb": 2048,
                "algoritmo_asignacion": "First-Fit Dinámico"
            },
            "almacenamiento_config": {
                "capacidad_total_gb": 512,
                "tipo": "NVMe SSD Automotriz ASIL",
                "sistema_archivos": "ext4-automotive"
            },
            "memoria_bloques": [
                {"bloque_num": 1, "tamano_mb": 2048, "ocupado": True, "proceso": "Kernel RTOS", "tipo": "Reservado"},
                {"bloque_num": 2, "tamano_mb": 512, "ocupado": True, "proceso": "adas_collision_avoidance", "tipo": "Usuario"},
                {"bloque_num": 3, "tamano_mb": 420, "ocupado": True, "proceso": "infotainment_media_player", "tipo": "Usuario"}
            ],
            "logs": [
                {"nivel": "INFO", "modulo": "KERNEL", "mensaje": "Inicialización de subsistema de memoria RAM 16GB completa.", "timestamp": datetime.datetime.now().strftime("%H:%M:%S")},
                {"nivel": "INFO", "modulo": "SCHEDULER", "mensaje": "Planificador de procesos por prioridad arrancado.", "timestamp": datetime.datetime.now().strftime("%H:%M:%S")},
                {"nivel": "WARN", "modulo": "STORAGE", "mensaje": "Espacio en /logs alcanzando 65% de capacidad rotativa.", "timestamp": datetime.datetime.now().strftime("%H:%M:%S")}
            ],
            "eventos": eventos_data,
            "auditoria": auditoria_data,
            "bateria": {
                "soc_pct": 82.0,
                "voltaje_v": 398.2,
                "corriente_a": 42.0,
                "temp_c": 31.5,
                "potencia_kw": 16.7,
                "modo_conduccion": "Normal",
                "salud_soh": 96.0
            }
        }


def get_supabase_client() -> Optional[Client]:
    """
    Intenta obtener cliente oficial Supabase si hay credenciales configuradas
    en st.secrets o en variables de entorno.
    """
    url = None
    key = None
    
    # Revisar st.secrets
    try:
        if "SUPABASE_URL" in st.secrets:
            url = st.secrets["SUPABASE_URL"]
        elif "NEXT_PUBLIC_SUPABASE_URL" in st.secrets:
            url = st.secrets["NEXT_PUBLIC_SUPABASE_URL"]

        if "SUPABASE_KEY" in st.secrets:
            key = st.secrets["SUPABASE_KEY"]
        elif "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY" in st.secrets:
            key = st.secrets["NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY"]
        elif "SUPABASE_ANON_KEY" in st.secrets:
            key = st.secrets["SUPABASE_ANON_KEY"]
    except Exception:
        pass
        
    # Revisar variables de entorno
    if not url:
        url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    if not key:
        key = os.environ.get("SUPABASE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
        
    if url and key and HAS_SUPABASE_LIB:
        try:
            return create_client(url, key)
        except Exception:
            return None
    return None



def get_db():
    """Retorna la base de datos en sesión (emulada / sincronizada)"""
    _inicializar_mock_db()
    return st.session_state["autoos_db"]
