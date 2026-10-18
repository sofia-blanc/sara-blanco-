"""
====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Dashboard Principal de Control e Integración
====================================================================
"""

import sys
import os
from pathlib import Path

# Configurar ruta absoluta al módulo Auto para compatibilidad total con Streamlit Cloud
AUTO_DIR = Path(__file__).resolve().parent
if str(AUTO_DIR) not in sys.path:
    sys.path.insert(0, str(AUTO_DIR))

try:
    os.chdir(str(AUTO_DIR))
except Exception:
    pass

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configuración de página de Streamlit
st.set_page_config(
    page_title="AutoOS - Sistema Operativo Vehicular",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar módulos del sistema
from config import get_db, get_supabase_client
from modules.auth_security import (
    obtener_usuario_actual, cambiar_usuario_activo, tiene_permiso,
    validar_accion, obtener_auditoria, obtener_matriz_permisos, ROLES_INFO
)
from modules.devices import (
    obtener_dispositivos, obtener_dispositivo, obtener_resumen_dispositivos,
    cambiar_estado_dispositivo, calibrar_dispositivo
)
from modules.telemetry_battery import (
    obtener_estado_bateria, calcular_semaforo_general,
    obtener_eventos_criticos_activos, actualizar_bateria
)
from modules.incidents import (
    ESCENARIOS_DISPONIBLES, ejecutar_escenario_falla, restablecer_sistema_a_normal
)
from modules.processes import (
    obtener_procesos, crear_proceso, cambiar_estado_proceso,
    finalizar_proceso, calcular_uso_cpu_total
)
from modules.memory_storage import (
    obtener_uso_memoria, obtener_sistema_archivos, obtener_logs_sistema
)
from modules.ui_components import (
    aplicar_estilos_cockpit, render_banner_semaforo,
    render_card_telemetria, render_tarjeta_dispositivo,
    render_acceso_denegado, obtener_paleta, render_reloj_en_vivo, render_menu_herramientas_interactivas, render_reproductor_spotify
)

# Mapeo de identificadores de procesos a nombres descriptivos automotrices
MAPA_NOMBRES_PROCESOS = {
    "bms_thermal_monitor": "Monitor Térmico BMS",
    "adas_collision_avoidance": "Sistema Anticolisión ADAS",
    "can_bus_gateway_daemon": "Gateway de Comunicación CAN",
    "gnss_navigation_engine": "Motor de Navegación GPS",
    "telemetry_cloud_sync": "Telemetría y Enlace Nube",
    "hvac_thermal_controller": "Control Climatización HVAC",
    "infotainment_media_player": "Audio e Infoentretenimiento",
    "voice_assistant_agent": "Asistente de Voz en Cabina"
}

def formatear_nombre_proceso(nombre: str) -> str:
    """Convierte el identificador técnico de proceso a un nombre descriptivo automotriz legible."""
    if nombre in MAPA_NOMBRES_PROCESOS:
        return MAPA_NOMBRES_PROCESOS[nombre]
    return nombre.replace("_", " ").title()

# ====================================================================
# BARRA LATERAL (CONTROL DE SESIÓN Y CREDENCIALES)
# ====================================================================
with st.sidebar:
    st.markdown("### AutoOS")
    st.caption("Sistema Operativo para Vehículo Inteligente")

    # ====================================================================
    # SELECTOR DE MODO CLARO / OSCURO / SISTEMA INTERACTIVO (STREAMLIT POPUP & SIDEBAR)
    # ====================================================================
    st.markdown("#### Apariencia y Tema")
    if "modo_tema_seleccionado" not in st.session_state:
        st.session_state["modo_tema_seleccionado"] = "System"

    cols_tema = st.columns(3)
    with cols_tema[0]:
        if st.button("◐ System", key="btn_theme_sys", use_container_width=True,
                     type="primary" if st.session_state["modo_tema_seleccionado"] == "System" else "secondary"):
            st.session_state["modo_tema_seleccionado"] = "System"
            st.rerun()
    with cols_tema[1]:
        if st.button("☀ Light", key="btn_theme_light", use_container_width=True,
                     type="primary" if st.session_state["modo_tema_seleccionado"] == "Light" else "secondary"):
            st.session_state["modo_tema_seleccionado"] = "Light"
            st.rerun()
    with cols_tema[2]:
        if st.button("☾ Dark", key="btn_theme_dark", use_container_width=True,
                     type="primary" if st.session_state["modo_tema_seleccionado"] == "Dark" else "secondary"):
            st.session_state["modo_tema_seleccionado"] = "Dark"
            st.rerun()

    tema_actual = st.session_state.get("modo_tema_seleccionado", "System")
    if tema_actual == "Light":
        modo_tema = "claro"
    elif tema_actual == "Dark":
        modo_tema = "oscuro"
    else:
        modo_tema = "auto"

    # Acciones Interactivas: Imprimir y Grabar Pantalla
    st.markdown("#### Herramientas")
    col_tools1, col_tools2 = st.columns(2)
    with col_tools1:
        if st.button("🖨️ Print", key="btn_tools_print", use_container_width=True):
            st.toast("Iniciando diálogo de impresión...", icon="🖨️")
            components.html("<script>window.parent.print();</script>", height=0)
    with col_tools2:
        if st.button("📹 Record screen", key="btn_tools_rec", use_container_width=True):
            st.session_state["abrir_grabador"] = not st.session_state.get("abrir_grabador", False)
            st.rerun()

    if st.session_state.get("abrir_grabador", False):
        st.info("🔴 Grabador de Pantalla Activo: Pulsa el control interactivo para capturar la sesión de AutoOS.")
        render_menu_herramientas_interactivas, render_reproductor_spotify(modo_tema)

    st.caption("Made with Streamlit v1.66.0 · AutoOS Edition")

    # Aplicar estilos dinámicos para el tema seleccionado
    aplicar_estilos_cockpit(modo_tema)
    paleta = obtener_paleta("claro" if modo_tema == "claro" else "oscuro")

    # Estado del sistema
    usuario_actual = obtener_usuario_actual()
    rol_actual     = usuario_actual.get("rol", "guest")
    semaforo       = calcular_semaforo_general()
    db             = get_db()
    bateria        = obtener_estado_bateria()
    resumen_dev    = obtener_resumen_dispositivos()
    cpu_total      = calcular_uso_cpu_total()
    memoria_info   = obtener_uso_memoria()
    info_rol       = ROLES_INFO.get(rol_actual, {})

    # Helpers de permisos por rol
    es_admin     = rol_actual == "admin"
    es_conductor = rol_actual == "user"
    es_pasajero  = rol_actual == "guest"

    st.markdown("---")
    st.markdown("#### Control de Usuario Activo")
    st.caption("Cambia de usuario para alternar permisos y verificar la interfaz según cada rol:")

    opciones_usuarios = {
        "usr_mecanico_01": "Carlos Vélez — Mecánico / Admin",
        "usr_conductor_01": "Laura Gómez — Conductora",
        "usr_pasajero_01": "Andrés Rivera — Pasajero"
    }

    id_seleccionado = st.selectbox(
        "Autenticar como:",
        options=list(opciones_usuarios.keys()),
        format_func=lambda x: opciones_usuarios[x],
        index=list(opciones_usuarios.keys()).index(usuario_actual["id"]) if usuario_actual["id"] in opciones_usuarios else 1
    )

    if id_seleccionado != usuario_actual["id"]:
        cambiar_usuario_activo(id_seleccionado)
        st.rerun()

    st.markdown(f"""
        <div class="rol-card">
            <div class="rol-label">Rol Asignado</div>
            <div class="rol-name">{info_rol.get('etiqueta')}</div>
            <div class="rol-nivel">Privilegio Kernel: Nivel {info_rol.get('nivel')}/10</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Conectividad Backend")
    cliente_sb = get_supabase_client()
    if cliente_sb:
        st.success("Supabase Cloud: Conectado")
    else:
        st.warning("Motor Local / Simulado Activo")
        st.caption("AutoOS opera en modo memoria sincronizada.")

    if es_admin:
        st.markdown("---")
        st.markdown("#### Acción de Mantenimiento")
        if st.button("Restablecer Sistema a Normal", use_container_width=True):
            ok, msg = restablecer_sistema_a_normal(usuario_actual)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)


# ====================================================================
# ENCABEZADO Y HUD VEHICULAR
# ====================================================================
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("AutoOS")
    st.caption("Plataforma de Simulación del Sistema Operativo Vehicular & Control de Seguridad")
with col_head2:
    render_reloj_en_vivo(modo_tema)

# Renderizar el Semáforo General de AutoOS
render_banner_semaforo(semaforo, modo_tema)


# ====================================================================
# PESTAÑAS BASE (TODAS DISPONIBLES EN LA BASE)
# ====================================================================
tab_cockpit, tab_seguridad, tab_dispositivos, tab_bateria, tab_incidentes, tab_procesos, tab_memoria = st.tabs([
    "Cockpit",
    "Seguridad",
    "Dispositivos",
    "Batería",
    "Escenarios",
    "Procesos",
    "Memoria"
])


# --------------------------------------------------------------------
# 1. COCKPIT GENERAL
# --------------------------------------------------------------------
with tab_cockpit:
    st.subheader("Indicadores de Telemetría en Tiempo Real")

    # Indicadores circulares SVG elegantes (sin recorte de texto)
    col_g1, col_g2, col_g3, col_g4 = st.columns(4)
    with col_g1:
        # CPU: verde cuando bajo (disponible), rojo cuando alto (saturado)
        if cpu_total < 40:
            color_cpu = "#22c55e"   # verde — disponible
        elif cpu_total < 70:
            color_cpu = "#f59e0b"   # amarillo — moderado
        else:
            color_cpu = "#ef4444"   # rojo — saturado
        render_card_telemetria(
            titulo="Uso Total de CPU",
            valor=cpu_total,
            unidad="%",
            subtexto="4 Cores activos · RTOS",
            color_acento=color_cpu,
            max_val=100.0,
            modo=modo_tema
        )
    with col_g2:
        # RAM: verde cuando baja (disponible), rojo cuando alta (saturada)
        ram_pct = memoria_info["pct_usado"]
        if ram_pct < 40:
            color_ram = "#22c55e"   # verde — disponible
        elif ram_pct < 70:
            color_ram = "#f59e0b"   # amarillo — moderado
        else:
            color_ram = "#ef4444"   # rojo — saturado
        render_card_telemetria(
            titulo="Uso de Memoria RAM",
            valor=ram_pct,
            unidad="%",
            subtexto=f"{memoria_info['procesos_mb']} MB / 16 GB",
            color_acento=color_ram,
            max_val=100.0,
            modo=modo_tema
        )
    with col_g3:
        color_bat = paleta['success'] if bateria["soc_pct"] > 25 else (paleta['warning'] if bateria["soc_pct"] > 12 else paleta['danger'])
        render_card_telemetria(
            titulo="Batería HV (BMS)",
            valor=bateria["soc_pct"],
            unidad="%",
            subtexto=f"{bateria.get('autonomia_km', 357.0)} km · Modo {bateria.get('modo_conduccion', 'Normal')}",
            color_acento=color_bat,
            max_val=100.0,
            modo=modo_tema
        )
    with col_g4:
        color_salud = paleta['success'] if resumen_dev["salud_promedio"] >= 90 else paleta['warning']
        render_card_telemetria(
            titulo="Salud Dispositivos",
            valor=resumen_dev["salud_promedio"],
            unidad="%",
            subtexto=f"{resumen_dev['operativos']}/{resumen_dev['total']} Sensores Operativos",
            color_acento=color_salud,
            max_val=100.0,
            modo=modo_tema
        )

    st.write("") # Espaciador

    st.markdown("#### Estado General del Sistema Vehicular")

    # --- Fila 1: GPS / Navegación · Cámara y Visión · Sensores · Comunicación ---
    col_sys1, col_sys2, col_sys3, col_sys4 = st.columns(4)

    # GPS y Navegación
    _gps = next((d for d in db["dispositivos"] if d["codigo"] == "DEV_GPS_01"), {})
    _nav_proc = next((p for p in db["procesos"] if p["nombre"] == "gnss_navigation_engine"), {})
    _gps_ok = _gps.get("estado") == "operativo"
    with col_sys1:
        st.markdown(f"""
            <div class="auto-card">
                <h4>GPS y Navegación</h4>
                <div style="color: {'#22c55e' if _gps_ok else '#ef4444'};">
                    Receptor: <b>{'Operativo' if _gps_ok else 'Fallo'}</b>
                </div>
                <div>Satelites: <b>{_gps.get('datos_telemetria', {}).get('satelites', '—')}</b></div>
                <div>HDOP: <b>{_gps.get('datos_telemetria', {}).get('hdop', '—')}</b></div>
                <div>Motor Nav: <b>{_nav_proc.get('estado', '—').capitalize()}</b></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Ver GPS & Ruta", key="btn_sys_gps", use_container_width=True):
            st.session_state["cockpit_sub_activo"] = "GPS & Navegación"
            st.session_state["selector_subsistema_cockpit"] = "GPS & Navegación"
            st.rerun()

    # Cámara y Visión Artificial
    _cam = next((d for d in db["dispositivos"] if d["codigo"] == "DEV_CAM_FRONT"), {})
    _cam_ok = _cam.get("estado") == "operativo"
    _cam_tel = _cam.get("datos_telemetria", {})
    with col_sys2:
        st.markdown(f"""
            <div class="auto-card">
                <h4>Cámara y Visión ADAS</h4>
                <div style="color: {'#22c55e' if _cam_ok else '#ef4444'};">
                    Estado: <b>{'Operativa' if _cam_ok else 'Fallo'}</b>
                </div>
                <div>Resolución: <b>{_cam_tel.get('resolucion', '—')}</b></div>
                <div>FPS: <b>{_cam_tel.get('fps', '—')}</b></div>
                <div>Oclusión: <b>{'No' if not _cam_tel.get('oclusion') else 'Detectada'}</b></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Ver Cámara ADAS", key="btn_sys_cam", use_container_width=True):
            st.session_state["cockpit_sub_activo"] = "Cámara & Visión ADAS"
            st.session_state["selector_subsistema_cockpit"] = "Cámara & Visión ADAS"
            st.rerun()

    # Sensores (LiDAR + Radar)
    _lidar = next((d for d in db["dispositivos"] if d["codigo"] == "DEV_LIDAR_01"), {})
    _radar = next((d for d in db["dispositivos"] if d["codigo"] == "DEV_RADAR_01"), {})
    _lidar_ok = _lidar.get("estado") == "operativo"
    _radar_ok = _radar.get("estado") == "operativo"
    with col_sys3:
        st.markdown(f"""
            <div class="auto-card">
                <h4>Sensores de Percepción</h4>
                <div style="color: {'#22c55e' if _lidar_ok else '#ef4444'};">
                    LiDAR 360°: <b>{'Operativo' if _lidar_ok else 'Fallo'}</b>
                </div>
                <div>Puntos/seg: <b>{_lidar.get('datos_telemetria', {}).get('puntos_seg', '—'):,}</b></div>
                <div style="color: {'#22c55e' if _radar_ok else '#ef4444'};">
                    Radar 77GHz: <b>{'Operativo' if _radar_ok else 'Fallo'}</b>
                </div>
                <div>Objetos: <b>{_radar.get('datos_telemetria', {}).get('objetos_trackeados', '—')} rastreados</b></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Radar LiDAR 360°", key="btn_sys_lidar", use_container_width=True):
            st.session_state["cockpit_sub_activo"] = "Sensores (LiDAR/Radar)"
            st.session_state["selector_subsistema_cockpit"] = "Sensores (LiDAR/Radar)"
            st.rerun()

    # Comunicación V2X / 5G
    _com = next((d for d in db["dispositivos"] if d["codigo"] == "DEV_COM_V2X"), {})
    _com_ok = _com.get("estado") == "operativo"
    _com_tel = _com.get("datos_telemetria", {})
    with col_sys4:
        st.markdown(f"""
            <div class="auto-card">
                <h4>Comunicación 5G / V2X</h4>
                <div style="color: {'#22c55e' if _com_ok else '#ef4444'};">
                    Enlace: <b>{'Activo' if _com_ok else 'Desconectado'}</b>
                </div>
                <div>Latencia: <b>{_com_tel.get('latencia_ms', '—')} ms</b></div>
                <div>Señal: <b>{_com_tel.get('senal_dbm', '—')} dBm</b></div>
                <div>Backend: <b>{_com_tel.get('enlace', '—')}</b></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Diagnóstico 5G", key="btn_sys_com", use_container_width=True):
            st.session_state["cockpit_sub_activo"] = "Comunicación 5G"
            st.session_state["selector_subsistema_cockpit"] = "Comunicación 5G"
            st.rerun()

    # --- Fila 2: Multimedia · Batería · Procesos Críticos · Hardware general ---
    col_sys5, col_sys6, col_sys7, col_sys8 = st.columns(4)

    # Multimedia / Infoentretenimiento
    _info = next((d for d in db["dispositivos"] if d["codigo"] == "DEV_INFOTAINMENT"), {})
    _info_ok = _info.get("estado") == "operativo"
    _info_tel = _info.get("datos_telemetria", {})
    _media_proc = next((p for p in db["procesos"] if p["nombre"] == "infotainment_media_player"), {})
    with col_sys5:
        st.markdown(f"""
            <div class="auto-card">
                <h4>Multimedia e Infoentretenimiento</h4>
                <div style="color: {'#22c55e' if _info_ok else '#ef4444'};">
                    Pantalla: <b>{'Operativa' if _info_ok else 'Fallo'}</b>
                </div>
                <div>Brillo: <b>{_info_tel.get('brillo_pct', '—')}%</b></div>
                <div>Audio: <b>{_info_tel.get('audio_vol_pct', '—')}%</b></div>
                <div>Proceso: <b>{_media_proc.get('estado', '—').capitalize()}</b></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Control Multimedia", key="btn_sys_media", use_container_width=True):
            st.session_state["cockpit_sub_activo"] = "Multimedia & Audio"
            st.session_state["selector_subsistema_cockpit"] = "Multimedia & Audio"
            st.rerun()

    # Batería BMS
    _bms_dev = next((d for d in db["dispositivos"] if d["codigo"] == "DEV_BATTERY_BMS"), {})
    _bms_ok = _bms_dev.get("estado") == "operativo"
    with col_sys6:
        color_bat_icon = "#22c55e" if bateria["soc_pct"] > 25 else ("#f59e0b" if bateria["soc_pct"] > 12 else "#ef4444")
        st.markdown(f"""
            <div class="auto-card">
                <h4>Batería HV (BMS)</h4>
                <div style="color: {'#22c55e' if _bms_ok else '#ef4444'};">
                    BMS: <b>{'Operativo' if _bms_ok else 'Fallo'}</b>
                </div>
                <div style="color: {color_bat_icon};">SoC: <b>{bateria['soc_pct']}%</b></div>
                <div>Tensión: <b>{bateria['voltaje_v']} V</b></div>
                <div>Temperatura: <b>{bateria['temp_c']} °C</b></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Diagnóstico Batería", key="btn_sys_bat", use_container_width=True):
            st.session_state["cockpit_sub_activo"] = "Batería & Celdas"
            st.session_state["selector_subsistema_cockpit"] = "Batería & Celdas"
            st.rerun()

    # Procesos Críticos (ASIL-D)
    _criticos = [p for p in db["procesos"] if p.get("critico")]
    _criticos_ok = all(p["estado"] in ("ejecutando", "listo") for p in _criticos)
    with col_sys7:
        st.markdown(f"""
            <div class="auto-card">
                <h4>Procesos Críticos ASIL-D</h4>
                <div style="color: {'#22c55e' if _criticos_ok else '#ef4444'};">
                    Estado general: <b>{'Nominal' if _criticos_ok else 'Alerta'}</b>
                </div>
                {"".join(f'<div>{formatear_nombre_proceso(p["nombre"])}: <b>{p["estado"].capitalize()}</b></div>' for p in _criticos[:2])}
                <div>CPU RTOS: <b>{cpu_total}%</b></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Procesos ASIL-D", key="btn_sys_proc", use_container_width=True):
            st.session_state["cockpit_sub_activo"] = "Procesos Críticos"
            st.session_state["selector_subsistema_cockpit"] = "Procesos Críticos"
            st.rerun()

    # Hardware General
    with col_sys8:
        st.markdown(f"""
            <div class="auto-card">
                <h4>Hardware y Periféricos</h4>
                <div>Total: <b>{resumen_dev['total']} dispositivos</b></div>
                <div style="color: #22c55e;">Operativos: <b>{resumen_dev['operativos']}</b></div>
                <div style="color: #f59e0b;">Degradados: <b>{resumen_dev['degradados']}</b></div>
                <div style="color: #ef4444;">Fallas: <b>{resumen_dev['fallas'] + resumen_dev['desconectados']}</b></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Hardware General", key="btn_sys_hw", use_container_width=True):
            st.session_state["cockpit_sub_activo"] = "Red CAN & Hardware"
            st.session_state["selector_subsistema_cockpit"] = "Red CAN & Hardware"
            st.rerun()

    # ================================================================
    # CONSOLA DE INSPECCIÓN INTERACTIVA (CLICK-DRIVEN Y ÚTIL DE VERDAD)
    # ================================================================
    st.markdown("---")
    st.subheader("Consola de Inspección Interactiva")
    st.caption("Inspecciona y opera cada subsistema automotriz con mapas, cámaras, radar y telemetría en tiempo real:")

    lista_subsistemas = [
        "GPS & Navegación",
        "Cámara & Visión ADAS",
        "Sensores (LiDAR/Radar)",
        "Multimedia & Audio",
        "Comunicación 5G",
        "Batería & Celdas",
        "Procesos Críticos",
        "Red CAN & Hardware"
    ]

    sub_activo_actual = st.session_state.get("cockpit_sub_activo", "GPS & Navegación")
    sub_elegido = st.radio(
        "Subsistema Activo en Consola:",
        options=lista_subsistemas,
        index=lista_subsistemas.index(sub_activo_actual) if sub_activo_actual in lista_subsistemas else 0,
        horizontal=True,
        key="selector_subsistema_cockpit"
    )
    st.session_state["cockpit_sub_activo"] = sub_elegido

    # ------------------------------------------------------------
    # 1. CONSOLA: GPS Y NAVEGACIÓN
    # ------------------------------------------------------------
    if sub_elegido == "GPS & Navegación":
        col_gps1, col_gps2 = st.columns([3, 2])
        rutas_gps = {
            "Campus Universitario Central (Origen)": {"lat": 4.6097, "lon": -74.0817, "dist_km": 0.0, "tiempo_min": 0},
            "Estación de Carga Rápida 150 kW (Autopista Norte)": {"lat": 4.6850, "lon": -74.0520, "dist_km": 11.4, "tiempo_min": 18},
            "Taller y Laboratorio Mecánico Automotriz": {"lat": 4.6480, "lon": -74.0930, "dist_km": 5.8, "tiempo_min": 12},
            "Centro de Distribución Logística (Occidente)": {"lat": 4.6950, "lon": -74.1350, "dist_km": 16.2, "tiempo_min": 26}
        }

        with col_gps1:
            st.markdown("##### Mapa de Navegación Vehicular y Trayectoria")
            dest_elegido = st.selectbox(
                "Fijar Destino de Navegación:",
                options=list(rutas_gps.keys()),
                index=1
            )
            info_dest = rutas_gps[dest_elegido]

            df_mapa = pd.DataFrame([
                {"lat": 4.6097, "lon": -74.0817, "nombre": "Posición Actual Vehículo"},
                {"lat": info_dest["lat"], "lon": info_dest["lon"], "nombre": dest_elegido}
            ])
            st.map(df_mapa, zoom=11)

        with col_gps2:
            st.markdown("##### Computadora de Ruta GNSS")
            consumo_est_kwh = (info_dest["dist_km"] * bateria.get("consumo_kwh_100km", 16.5)) / 100.0
            soc_consumo_pct = (consumo_est_kwh / 75.0) * 100.0
            soc_llegada = max(0.0, round(bateria["soc_pct"] - soc_consumo_pct, 1))

            st.markdown(f"""
                <div class="auto-card">
                    <h4>Telemetría de Navegación RTK</h4>
                    <div>Coordenadas: <b>4.6097° N, -74.0817° W</b></div>
                    <div>Distancia a destino: <b>{info_dest['dist_km']} km</b></div>
                    <div>Tiempo estimado (ETA): <b>~{info_dest['tiempo_min']} min</b></div>
                    <div>Consumo previsto: <b>~{consumo_est_kwh:.2f} kWh ({soc_consumo_pct:.1f}% SoC)</b></div>
                    <div>Batería estimada al llegar: <b style="color: {'#22c55e' if soc_llegada > 20 else '#ef4444'};">{soc_llegada}%</b></div>
                    <div>Rumbo vehicular: <b>142° (Sureste)</b></div>
                    <div>Velocidad actual: <b>48.5 km/h</b></div>
                </div>
            """, unsafe_allow_html=True)

            col_bnav1, col_bnav2 = st.columns(2)
            with col_bnav1:
                if st.button("Iniciar Guía GPS", type="primary", use_container_width=True):
                    st.success(f"Trayectoria hacia '{dest_elegido}' sincronizada con el bus CAN.")
            with col_bnav2:
                if st.button("Recalibrar RTK", use_container_width=True):
                    st.info("Calibración diferencial completada (14 satélites).")

    # ------------------------------------------------------------
    # 2. CONSOLA: CÁMARA Y VISIÓN ARTIFICIAL ADAS
    # ------------------------------------------------------------
    elif sub_elegido == "Cámara & Visión ADAS":
        col_cam1, col_cam2 = st.columns([3, 2])
        with col_cam1:
            st.markdown("##### HUD de Visión Artificial ADAS Frontal")
            modo_cam = st.radio(
                "Filtro del Sensor Óptico:",
                ["Luz Visible (RGB)", "Visión Térmica / Nocturna", "Segmentación Semántica ADAS"],
                horizontal=True
            )

            bg_sky = "#0b132b" if modo_cam != "Visión Térmica / Nocturna" else "#000000"
            bg_road = "#1c2541" if modo_cam != "Visión Térmica / Nocturna" else "#1a1a1a"
            line_color = "#34d399" if modo_cam != "Segmentación Semántica ADAS" else "#BF40FA"

            fig_cam = go.Figure()
            # Líneas guía de carril LKA
            fig_cam.add_trace(go.Scatter(
                x=[20, 42, None, 80, 58],
                y=[0, 60, None, 0, 60],
                mode="lines",
                line=dict(color=line_color, width=4),
                name="Líneas de Carril LKA"
            ))
            # Vehículo líder detectado
            fig_cam.add_trace(go.Scatter(
                x=[45, 55, 55, 45, 45],
                y=[38, 38, 55, 55, 38],
                mode="lines",
                line=dict(color="#ef4444", width=3),
                fill="toself",
                fillcolor="rgba(239, 68, 68, 0.2)",
                name="Vehículo Líder [ACC 35m]"
            ))
            # Peatón detectado
            fig_cam.add_trace(go.Scatter(
                x=[76, 80, 80, 76, 76],
                y=[15, 15, 30, 30, 15],
                mode="lines",
                line=dict(color="#f59e0b", width=2),
                fill="toself",
                fillcolor="rgba(245, 158, 11, 0.2)",
                name="Peatón Acera [12m]"
            ))

            fig_cam.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(range=[0, 100], showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(range=[0, 70], showgrid=False, zeroline=False, showticklabels=False),
                paper_bgcolor=bg_sky,
                plot_bgcolor=bg_road,
                font=dict(family="Playfair Display", color="#FFFFFF"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_cam, use_container_width=True)

        with col_cam2:
            st.markdown("##### Inferencia de Red Neuronal en Tiempo Real")
            st.markdown(f"""
                <div class="auto-card">
                    <h4>Cámara Estereoscópica Frontal</h4>
                    <div>Resolución activa: <b>1920x1080p @ 60 FPS</b></div>
                    <div>Latencia de procesamiento: <b>14.2 ms (ASIL-D)</b></div>
                    <div>Oclusión de lente: <b style="color: #22c55e;">0% (Lente despejado)</b></div>
                    <div>Temperatura de sensor: <b>42.5 °C</b></div>
                    <div>Frenado Autónomo (AEB): <b style="color: #22c55e;">Armado y Listo</b></div>
                </div>
            """, unsafe_allow_html=True)

            if st.button("Ejecutar Snapshot & Detección IA", type="primary", use_container_width=True):
                st.toast("Inferencia ejecutada en la NPU automotriz (14.2 ms).")

            df_obj = pd.DataFrame([
                {"Objeto": "Vehículo Líder", "Distancia": "35.4 m", "TTC (Colisión)": "4.8 s", "Confianza": "98.4%"},
                {"Objeto": "Peatón en Acera", "Distancia": "12.8 m", "TTC (Colisión)": "Seguro", "Confianza": "94.2%"},
                {"Objeto": "Señal Límite 60", "Distancia": "45.0 m", "TTC (Colisión)": "N/A", "Confianza": "99.1%"}
            ])
            st.dataframe(df_obj, hide_index=True, use_container_width=True)

    # ------------------------------------------------------------
    # 3. CONSOLA: SENSORES DE PERCEPCIÓN (LIDAR / RADAR)
    # ------------------------------------------------------------
    elif sub_elegido == "Sensores (LiDAR/Radar)":
        col_sen1, col_sen2 = st.columns([3, 2])
        with col_sen1:
            st.markdown("##### Radar Polar 360° — Fusión LiDAR + Radar")
            angulos = [0, 25, 45, 90, 135, 180, 225, 270, 315]
            distancias = [35.4, 48.0, 18.2, 8.5, 42.0, 28.0, 4.2, 9.8, 22.0]
            tipos = ["Auto", "Eco", "Obstáculo", "Muro", "Auto", "Eco", "Guardarraíl", "Poste", "Eco"]
            colores_radar = ["#ef4444" if d < 10 else ("#f59e0b" if d < 25 else "#22c55e") for d in distancias]

            fig_polar = go.Figure()
            fig_polar.add_trace(go.Scatterpolar(
                r=[0], theta=[0], mode="markers",
                marker=dict(size=14, color="#BF40FA", symbol="triangle-up"),
                name="Vehículo Propio"
            ))
            fig_polar.add_trace(go.Scatterpolar(
                r=distancias, theta=angulos, mode="markers+text",
                text=tipos, textposition="top center",
                marker=dict(size=10, color=colores_radar),
                name="Ecos Detectados"
            ))

            fig_polar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 60]),
                    angularaxis=dict(direction="clockwise")
                ),
                height=320,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Playfair Display", color=paleta['text_primary']),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_polar, use_container_width=True)

        with col_sen2:
            st.markdown("##### Parámetros de Escaneo Solid-State")
            st.slider("Rango de Cobertura Activo (m):", 10, 150, 60)
            st.markdown(f"""
                <div class="auto-card">
                    <h4>Telemetría de Percepción</h4>
                    <div>Frecuencia de muestreo: <b>600 RPM (10 Hz)</b></div>
                    <div>Puntos de nube por segundo: <b>1,200,000 pts/s</b></div>
                    <div>Precisión de alcance: <b>± 2.5 cm</b></div>
                    <div>Radar de ondas milimétricas: <b>77 GHz Doppler</b></div>
                    <div>Zona ciega: <b>0.15 m (Cero punto ciego frontal)</b></div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Limpiar Lentes / Calibrar LiDAR", use_container_width=True):
                st.success("Ciclo de calentamiento y autolimpieza completado.")

    # ------------------------------------------------------------
    # 4. CONSOLA: MULTIMEDIA E INFOENTRETENIMIENTO
    # ------------------------------------------------------------
    elif sub_elegido == "Multimedia & Audio":
        col_med1, col_med2 = st.columns([3, 2])
        with col_med1:
            st.markdown("##### Pantalla Central y Reproductor de Cabina")
            PISTAS_MULTIMEDIA = [
                {
                    "titulo": "Conducción Nocturna (Synthwave 80s)",
                    "artista": "Kavinsky Style - AutoOS Master",
                    "duracion": "03:45",
                    "url": "https://cdn.freesound.org/previews/612/612610_5674468-lq.mp3"
                },
                {
                    "titulo": "Autobahn Electric Cruise",
                    "artista": "Electronic Beats RTOS",
                    "duracion": "04:12",
                    "url": "https://cdn.freesound.org/previews/536/536108_7037-lq.mp3"
                },
                {
                    "titulo": "Podcast Tecnologías de Vehículos Autónomos & RTOS",
                    "artista": "AutoOS Engineering Team",
                    "duracion": "05:30",
                    "url": "https://cdn.freesound.org/previews/682/682142_11861866-lq.mp3"
                },
                {
                    "titulo": "Radio Tráfico & Alertas en Vivo (FM 99.9)",
                    "artista": "Central de Tráfico Inteligente",
                    "duracion": "02:50",
                    "url": "https://cdn.freesound.org/previews/416/416529_5121236-lq.mp3"
                }
            ]
            titulos_pistas = [f"{p['titulo']} — {p['artista']}" for p in PISTAS_MULTIMEDIA]
            
            pista_idx = st.session_state.get("multimedia_pista_idx", 0)
            if pista_idx >= len(PISTAS_MULTIMEDIA):
                pista_idx = 0
                st.session_state["multimedia_pista_idx"] = 0

            sel_pista = st.selectbox("Pista en Reproducción:", titulos_pistas, index=pista_idx, key="sb_pista_multimedia")
            if titulos_pistas.index(sel_pista) != pista_idx:
                st.session_state["multimedia_pista_idx"] = titulos_pistas.index(sel_pista)
                st.session_state["multimedia_reproduciendo"] = True
                pista_idx = st.session_state["multimedia_pista_idx"]

            reproduciendo = st.session_state.get("multimedia_reproduciendo", False)
            silenciado = st.session_state.get("multimedia_silenciado", False)
            volumen_actual = st.session_state.get("multimedia_volumen", 65)

            col_c1, col_c2, col_c3, col_c4 = st.columns(4)
            with col_c1:
                if st.button("Anterior", use_container_width=True, key="btn_med_prev"):
                    st.session_state["multimedia_pista_idx"] = (pista_idx - 1) % len(PISTAS_MULTIMEDIA)
                    st.session_state["multimedia_reproduciendo"] = True
                    st.rerun()
            with col_c2:
                label_play = "Pausar" if reproduciendo else "Reproducir"
                if st.button(label_play, type="primary" if reproduciendo else "secondary", use_container_width=True, key="btn_med_play"):
                    st.session_state["multimedia_reproduciendo"] = not reproduciendo
                    st.rerun()
            with col_c3:
                if st.button("Siguiente", use_container_width=True, key="btn_med_next"):
                    st.session_state["multimedia_pista_idx"] = (pista_idx + 1) % len(PISTAS_MULTIMEDIA)
                    st.session_state["multimedia_reproduciendo"] = True
                    st.rerun()
            with col_c4:
                label_mute = "Desmutear" if silenciado else "Silenciar"
                if st.button(label_mute, use_container_width=True, key="btn_med_mute"):
                    st.session_state["multimedia_silenciado"] = not silenciado
                    st.rerun()

            pista_actual = PISTAS_MULTIMEDIA[pista_idx]
            st.progress(0.45 if reproduciendo else 0.0, text=f"Duración: {pista_actual['duracion']}")

            col_sl1, col_sl2 = st.columns(2)
            with col_sl1:
                vol = st.slider("Volumen Cabina:", 0, 100, volumen_actual, key="slider_vol_cabina")
                st.session_state["multimedia_volumen"] = vol
            with col_sl2:
                brillo = st.slider("Brillo Pantalla OLED:", 10, 100, 75, key="slider_brillo_oled")

            # Reproductor Funcional Real
            render_reproductor_spotify(modo_tema, pista=pista_actual, reproduciendo=reproduciendo, volumen=vol, silenciado=silenciado)

        with col_med2:
            st.markdown("##### Confort Acústico & Climatización")
            st.radio("Perfil de Ecualizador:", ["Voz & Podcasts", "Bajos Dinámicos", "Sonido Espacial 3D"], horizontal=True)
            st.markdown(f"""
                <div class="auto-card">
                    <h4>Gestión de Cabina</h4>
                    <div>Fuente de audio: <b>LIN-Bus Confort · Automotive DSP</b></div>
                    <div>Volumen actual: <b>{vol}%</b></div>
                    <div>Brillo de pantalla: <b>{brillo}%</b></div>
                    <div>Temperatura de cabina: <b>21.5 °C</b></div>
                    <div>Compresor HVAC: <b>30% carga</b></div>
                </div>
            """, unsafe_allow_html=True)
            st.slider("Ajustar Climatizador (°C):", 16.0, 28.0, 21.0, 0.5)

    # ------------------------------------------------------------
    # 5. CONSOLA: COMUNICACIÓN 5G / V2X
    # ------------------------------------------------------------
    elif sub_elegido == "Comunicación 5G":
        col_v1, col_v2 = st.columns([3, 2])
        with col_v1:
            st.markdown("##### Telemetría de Enlace Celular y V2X Cloud")
            st.markdown(f"""
                <div class="auto-card">
                    <h4>Módem 5G Automotriz & V2X</h4>
                    <div>Proveedor / Red: <b>AutoOS Automotive Telecom (5G SA)</b></div>
                    <div>Latencia de enlace actual: <b style="color: #22c55e;">19 ms</b></div>
                    <div>Potencia de señal: <b>-67 dBm (Excelente cobertura)</b></div>
                    <div>Enlace de base de datos: <b>Supabase PostgreSQL / Cloud</b></div>
                    <div>Protocolo V2X: <b>C-V2X 3GPP Rel 16 (Direct SideLink)</b></div>
                    <div>Tráfico transmitido hoy: <b>142.8 MB</b></div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Enviar Ping de Prueba a Supabase", type="primary", use_container_width=True):
                st.success("Respuesta recibida: 200 OK en 18.4 ms (Packet ACK).")
        with col_v2:
            st.markdown("##### Estado de Transmisión de Telemetría")
            st.json({
                "dispositivo": "DEV_COM_V2X",
                "protocolo": "MQTT / TLS 1.3",
                "broker": "cloud.autoos.tech",
                "qos": 1,
                "keepalive_sec": 30,
                "paquetes_perdidos": "0.0%"
            })

    # ------------------------------------------------------------
    # 6. CONSOLA: BATERÍA Y CELDAS BMS
    # ------------------------------------------------------------
    elif sub_elegido == "Batería & Celdas":
        col_b1, col_b2 = st.columns([3, 2])
        with col_b1:
            st.markdown("##### Distribución de Tensión por Celda (16 Celdas LiFePO4)")
            celdas_nombres = [f"C{i+1}" for i in range(16)]
            voltajes = [3.31, 3.30, 3.32, 3.31, 3.29, 3.30, 3.31, 3.32, 3.30, 3.31, 3.29, 3.32, 3.31, 3.30, 3.31, 3.32]
            fig_celdas = px.bar(
                x=celdas_nombres, y=voltajes,
                labels={"x": "Celda", "y": "Tensión (V)"},
                color=voltajes,
                color_continuous_scale="Viridis"
            )
            fig_celdas.update_yaxes(range=[3.0, 3.5])
            fig_celdas.update_layout(
                height=260,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Playfair Display", color=paleta['text_primary']),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_celdas, use_container_width=True)
        with col_b2:
            st.markdown("##### Diagnóstico de Celda & Balanceador")
            st.markdown(f"""
                <div class="auto-card">
                    <h4>Balanceo de Paquete LiFePO4</h4>
                    <div>Tensión media: <b>3.308 V</b></div>
                    <div>Delta de tensión máx: <b style="color: #22c55e;">0.030 V (Óptimo)</b></div>
                    <div>Resistencia interna media: <b>0.45 mΩ</b></div>
                    <div>Salud de batería (SoH): <b>{bateria.get('salud_soh', 96.0)}%</b></div>
                    <div>Ciclos completos: <b>142 ciclos</b></div>
                </div>
            """, unsafe_allow_html=True)
            st.caption("Para calibración térmica y modo de conducción detallado, consulta la pestaña 'Batería'.")

    # ------------------------------------------------------------
    # 7. CONSOLA: PROCESOS CRÍTICOS ASIL-D
    # ------------------------------------------------------------
    elif sub_elegido == "Procesos Críticos":
        st.markdown("##### Monitoreo de Tareas de Tiempo Real (Watchdog Kernel)")
        df_crit = pd.DataFrame([
            {"PID": 101, "Nombre": "Monitor Térmico BMS", "Nivel ASIL": "ASIL-D", "Período (ms)": 10, "Margen Límite": "98.5%", "Watchdog": "OK"},
            {"PID": 102, "Nombre": "Sistema Anticolisión ADAS", "Nivel ASIL": "ASIL-D", "Período (ms)": 20, "Margen Límite": "94.2%", "Watchdog": "OK"},
            {"PID": 103, "Nombre": "Gateway de Comunicación CAN", "Nivel ASIL": "ASIL-B", "Período (ms)": 5, "Margen Límite": "99.1%", "Watchdog": "OK"}
        ])
        st.dataframe(df_crit, hide_index=True, use_container_width=True)
        st.caption("Para pausar, crear o terminar procesos con permisos de rol (RBAC), utiliza la pestaña 'Procesos'.")

    # ------------------------------------------------------------
    # 8. CONSOLA: RED CAN Y HARDWARE
    # ------------------------------------------------------------
    elif sub_elegido == "Red CAN & Hardware":
        st.markdown("##### Diagnóstico de Carga y Tráfico en Buses Automotrices")
        df_buses = pd.DataFrame([
            {"Bus": "CAN-Bus Principal", "Velocidad": "500 kbps", "Carga": "28.4%", "Tramas/s": "1,840", "Errores CRC": 0},
            {"Bus": "CAN-Bus ADAS", "Velocidad": "1.0 Mbps", "Carga": "42.1%", "Tramas/s": "3,420", "Errores CRC": 0},
            {"Bus": "Automotive Ethernet", "Velocidad": "100 Mbps", "Carga": "19.5%", "Tramas/s": "12,800", "Errores CRC": 0},
            {"Bus": "LIN-Bus Confort", "Velocidad": "19.2 kbps", "Carga": "15.0%", "Tramas/s": "120", "Errores CRC": 0}
        ])
        st.dataframe(df_buses, hide_index=True, use_container_width=True)
        st.caption("Para calibrar o inyectar fallos de hardware en laboratorio, accede a la pestaña 'Dispositivos'.")

    st.markdown("#### Alertas y Eventos Críticos Activos")
    eventos_criticos = obtener_eventos_criticos_activos()
    if eventos_criticos:
        for ev in eventos_criticos:
            st.error(f"[{ev['severidad'].upper()}] {ev['mensaje']} (Hora: {ev['creado_en']})")
    else:
        st.success("No hay eventos críticos activos. El vehículo opera con normalidad.")


# --------------------------------------------------------------------
# 2. SEGURIDAD Y ROLES
# --------------------------------------------------------------------
with tab_seguridad:
    st.header("Módulo de Seguridad y Control de Acceso")

    col_u1, col_u2 = st.columns([1, 2])
    with col_u1:
        st.subheader("Identidad del Usuario")
        st.write(f"**Nombre:** {usuario_actual['nombre_completo']}")
        st.write(f"**Correo:** `{usuario_actual['email']}`")
        st.write(f"**Rol:** {info_rol.get('etiqueta')}")
        st.write(f"**Nivel de Privilegio:** {info_rol.get('nivel')}/10")
        st.write(f"**Descripción:** {info_rol.get('descripcion')}")

    with col_u2:
        st.subheader("Simulador de Autorización en Vivo")
        if es_admin:
            st.caption("Prueba qué operaciones están permitidas para el rol activo:")

            permiso_a_probar = st.selectbox(
                "Selecciona una operación a probar:",
                options=[
                    ("proceso.crear", "Crear un nuevo proceso vehicular"),
                    ("proceso.finalizar", "Finalizar / Abortar un proceso"),
                    ("dispositivo.calibrar", "Calibrar sensor LiDAR o Cámara ADAS"),
                    ("dispositivo.desconectar", "Desconectar un actuador By-Wire"),
                    ("seguridad.admin_usuarios", "Modificar roles y usuarios del vehículo"),
                    ("telemetria.ver_bateria", "Consultar telemetría BMS")
                ],
                format_func=lambda x: f"{x[0]} — {x[1]}"
            )

            if st.button("Ejecutar Verificación de Autorización"):
                clave, desc = permiso_a_probar
                autorizado, motivo = validar_accion(usuario_actual, clave, recurso=f"recurso_test:{clave}")
                if autorizado:
                    st.success(f"AUTORIZADO: El rol '{usuario_actual['rol'].upper()}' tiene el permiso '{clave}'.")
                else:
                    st.error(f"DENEGADO (403): {motivo}")
                    st.toast("Intento no autorizado registrado en auditoría.")
        else:
            st.info("El simulador interactivo de inyección de permisos requiere privilegios de Mecánico / Administrador. Tu rol actual tiene acceso de consulta a la matriz.")

    st.markdown("---")
    st.subheader("Matriz de Control de Acceso por Rol (RBAC)")
    matriz_df = pd.DataFrame(obtener_matriz_permisos())
    st.dataframe(matriz_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    if es_admin:
        st.subheader("Registro de Auditoría de Accesos")
        st.caption("Cada intento de acceso queda registrado con su veredicto (Aprobado o Denegado).")
        auditoria_df = pd.DataFrame(obtener_auditoria(15))
        if not auditoria_df.empty:
            st.dataframe(
                auditoria_df[["hora", "usuario_email", "rol", "recurso", "accion", "autorizado", "motivo_rechazo"]],
                use_container_width=True,
                hide_index=True
            )
    else:
        render_acceso_denegado("Registro de Auditoría de Accesos", "Mecánico / Admin")


# --------------------------------------------------------------------
# 3. HARDWARE Y DISPOSITIVOS
# --------------------------------------------------------------------
with tab_dispositivos:
    st.header("Abstracción de Hardware y Periféricos Vehiculares")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_estado = st.selectbox("Filtrar por Estado:", ["Todos", "Operativo", "Degradado", "Falla", "Desconectado"])
    with col_f2:
        filtro_bus = st.selectbox("Filtrar por Bus:", ["Todos", "CAN-Bus Principal", "CAN-Bus ADAS", "Automotive Ethernet", "LIN-Bus Confort"])

    dispositivos_filtrados = obtener_dispositivos(filtro_estado=filtro_estado, filtro_bus=filtro_bus)

    cols_tarjetas = st.columns(2)
    for idx, dev in enumerate(dispositivos_filtrados):
        with cols_tarjetas[idx % 2]:
            render_tarjeta_dispositivo(dev, modo_tema)

    st.markdown("---")

    if es_admin:
        st.subheader("Panel de Intervención de Dispositivos")
        st.caption("Simula fallos de hardware, cortes de bus o calibración de sensores:")

        col_act1, col_act2, col_act3 = st.columns([2, 1, 1])
        with col_act1:
            dev_codigo_seleccionado = st.selectbox(
                "Seleccionar dispositivo para operar:",
                options=[d["codigo"] for d in db["dispositivos"]],
                format_func=lambda x: f"{x} — {obtener_dispositivo(x)['nombre']}"
            )
        with col_act2:
            accion_hardware = st.selectbox(
                "Acción de Hardware:",
                options=["Inyectar Fallo", "Desconectar del Bus", "Calibrar / Restaurar"]
            )
        with col_act3:
            st.write("")
            st.write("")
            if st.button("Ejecutar Acción", use_container_width=True):
                if accion_hardware == "Inyectar Fallo":
                    ok, msg = cambiar_estado_dispositivo(dev_codigo_seleccionado, "falla", usuario_actual, motivo="Inyección de fallo en laboratorio")
                elif accion_hardware == "Desconectar del Bus":
                    ok, msg = cambiar_estado_dispositivo(dev_codigo_seleccionado, "desconectado", usuario_actual, motivo="Corte físico de línea CAN simulado")
                else:
                    ok, msg = calibrar_dispositivo(dev_codigo_seleccionado, usuario_actual)

                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    else:
        render_acceso_denegado("Panel de Intervención de Hardware", "Mecánico / Admin")


# --------------------------------------------------------------------
# 4. BATERÍA Y ENERGÍA
# --------------------------------------------------------------------
with tab_bateria:
    st.header("Sistema de Gestión Térmica y Batería (BMS)")
    st.caption("Monitoreo de alta tensión, perfil dinámico de conducción y balanceo térmico de celdas.")

    col_bat1, col_bat2, col_bat3, col_bat4 = st.columns(4)
    with col_bat1:
        st.metric(
            "Estado de Carga (SoC)",
            f"{bateria['soc_pct']}%",
            delta=bateria.get("modo_actual", "Normal")
        )
    with col_bat2:
        delta_km_val = bateria.get('delta_autonomia', 0)
        delta_km_txt = f"{'+' if delta_km_val > 0 else ''}{delta_km_val} km vs Normal" if delta_km_val != 0 else "Referencia Nominal"
        st.metric(
            "Autonomía Estimada",
            f"{bateria.get('autonomia_km', 357.0)} km",
            delta=delta_km_txt
        )
    with col_bat3:
        st.metric(
            "Límite de Inversor",
            f"{bateria.get('limite_potencia_kw', 150.0)} kW",
            delta=f"Voltaje: {bateria['voltaje_v']} V"
        )
    with col_bat4:
        st.metric(
            "Temperatura BMS",
            f"{bateria['temp_c']} °C",
            delta=f"Máx tolerado: 55°C",
            delta_color="inverse"
        )

    st.markdown("---")

    # Panel de Perfil de Conducción Vehicular (Disponible para Conductor y Mecánico/Admin)
    st.subheader("Perfil de Conducción y Modo Energético")
    st.caption("Ajusta la respuesta del acelerador, regeneración de frenado y climatización vehicular:")

    modo_actual_sel = bateria.get("modo_conduccion", "Normal")

    col_perfil1, col_perfil2 = st.columns([3, 2])
    with col_perfil1:
        if es_admin or es_conductor:
            modo_elegido = st.radio(
                "Modo de conducción:",
                options=["Eco", "Normal", "Sport"],
                horizontal=True,
                index=["Eco", "Normal", "Sport"].index(modo_actual_sel) if modo_actual_sel in ["Eco", "Normal", "Sport"] else 1
            )
            if st.button("Aplicar Modo", use_container_width=True):
                actualizar_bateria(bateria["soc_pct"], bateria["temp_c"], modo_conduccion=modo_elegido)
                st.success(f"Modo '{modo_elegido}' activado y calibrado en el bus CAN.")
                st.rerun()
        else:
            st.info("Modo de consulta. El rol de Pasajero tiene acceso de solo lectura a la telemetría energética.")

    with col_perfil2:
        st.markdown(f"""
            <div class="auto-card" style="margin-bottom: 0;">
                <h4 style="margin-bottom: 8px;">Telemetría del Perfil Activo</h4>
                <div>Modo Actual: <b>{bateria.get('modo_actual', modo_actual_sel)}</b></div>
                <div>Consumo Estimado: <b>{bateria.get('consumo_kwh_100km', 16.5)} kWh / 100 km</b></div>
                <div>Regeneración de Frenado: <b>{bateria.get('regeneracion', 'Estándar')}</b></div>
                <div>Curva de Torque: <b>{bateria.get('curva_torque', 'Lineal')}</b></div>
                <div>Gestión Climatización: <b>{bateria.get('perfil_hvac', 'Automático')}</b></div>
                <div>Descarga Típica: <b>~{bateria.get('corriente_a', 42.0)} A ({bateria.get('potencia_kw', 16.7)} kW)</b></div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if es_admin:
        st.subheader("Simulador de Descarga y Estado de Batería")
        st.caption("Ajuste directo de parámetros del BMS de alta tensión (Laboratorio Mecánico):")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            nuevo_soc = st.slider("Ajustar Nivel de Carga (SoC %):", 0.0, 100.0, float(bateria["soc_pct"]))
        with col_s2:
            nueva_temp = st.slider("Ajustar Temperatura BMS (°C):", 15.0, 70.0, float(bateria["temp_c"]))
        with col_s3:
            st.write("")
            st.write("")
            if st.button("Actualizar Parámetros BMS", use_container_width=True):
                actualizar_bateria(nuevo_soc, nueva_temp, modo_conduccion=bateria.get("modo_conduccion", "Normal"))
                st.success("Parámetros de batería actualizados en el bus CAN.")
                st.rerun()
    elif not es_conductor:
        render_acceso_denegado("Ajuste Directo de Parámetros BMS", "Mecánico / Admin")


# --------------------------------------------------------------------
# 5. ESCENARIOS DE FALLA (BASE ACTIVA - ACCESO SEGÚN ROL)
# --------------------------------------------------------------------
with tab_incidentes:
    st.header("Escenarios Críticos de Falla en AutoOS")

    escenario_elegido = st.radio(
        "Selecciona el escenario crítico a inspeccionar:",
        options=list(ESCENARIOS_DISPONIBLES.keys()),
        format_func=lambda x: ESCENARIOS_DISPONIBLES[x]['titulo']
    )

    st.info(f"**Descripción:** {ESCENARIOS_DISPONIBLES[escenario_elegido]['descripcion']}")

    if es_admin:
        if st.button("Disparar Escenario Crítico (Simular Incidente)", type="primary"):
            resultado = ejecutar_escenario_falla(escenario_elegido, usuario_actual)
            st.session_state["ultimo_escenario_resultado"] = resultado
            st.rerun()
    else:
        st.caption("Modo de consulta de contingencias. La inyección y disparo de incidentes críticos en laboratorio requiere rol de Mecánico / Admin.")

    if "ultimo_escenario_resultado" in st.session_state:
        res = st.session_state["ultimo_escenario_resultado"]
        st.markdown(f"### Ejecución del Protocolo: *{res['titulo']}*")
        st.caption(f"Marca temporal: {res['hora_ejecucion']}")

        for paso in res["pasos"]:
            st.markdown(f"""
                <div class="fase-step">
                    <div style="font-weight: 700; color: {paleta['accent_primary']}; font-size: 14px;">{paso['fase']}</div>
                    <div style="color: {paleta['text_primary']}; font-size: 13px; margin-top: 4px;">{paso['accion']}</div>
                </div>
            """, unsafe_allow_html=True)

        st.info("Observa cómo el semáforo superior, el estado de los dispositivos y las prioridades de los procesos se adaptaron automáticamente.")


# --------------------------------------------------------------------
# 6. PROCESOS Y CPU
# --------------------------------------------------------------------
with tab_procesos:
    st.header("Gestión de Procesos Vehiculares y Scheduler")

    if es_admin:
        with st.expander("Iniciar Nuevo Proceso Vehicular", expanded=False):
            col_cp1, col_cp2, col_cp3 = st.columns(3)
            with col_cp1:
                nombre_proc = st.text_input("Nombre del Proceso:", value="carplay_audio_stream")
                mem_proc = st.number_input("Memoria (MB):", min_value=16, max_value=2048, value=128, step=16)
            with col_cp2:
                prio_proc = st.slider("Prioridad (0 = Tiempo Real, 10 = Idle):", 0, 10, 5)
                cpu_proc = st.number_input("Consumo CPU Estimado (%):", min_value=0.5, max_value=50.0, value=3.5, step=0.5)
            with col_cp3:
                es_critico = st.checkbox("Proceso Crítico de Seguridad (ASIL)", value=False)
                st.write("")
                if st.button("Crear Proceso"):
                    ok, msg = crear_proceso(nombre_proc, prio_proc, cpu_proc, mem_proc, es_critico, usuario_actual)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    st.markdown("---")
    st.subheader("Planificación de CPU y Resumen de Procesos")

    procesos_actuales = obtener_procesos()

    col_chart1, col_chart2 = st.columns([3, 2])
    with col_chart1:
        st.markdown("##### Diagrama Gantt — Planificación de CPU")
        ahora_gantt = datetime.datetime.now()
        datos_gantt = []
        for i, proc in enumerate(procesos_actuales):
            offset   = (len(procesos_actuales) - i) * 6
            duracion = 4 if proc["estado"] == "ejecutando" else 2
            nombre_legible = formatear_nombre_proceso(proc["nombre"])
            etiqueta_proc = f"PID {proc['pid']}: {nombre_legible}"
            datos_gantt.append({
                "Proceso": etiqueta_proc,
                "Inicio":  ahora_gantt - datetime.timedelta(seconds=offset + duracion),
                "Fin":     ahora_gantt - datetime.timedelta(seconds=offset),
                "Estado":  proc["estado"].capitalize(),
                "Prioridad": f"Prio {proc['prioridad']}"
            })
            if proc["estado"] == "ejecutando":
                datos_gantt.append({
                    "Proceso": etiqueta_proc,
                    "Inicio":  ahora_gantt - datetime.timedelta(seconds=3),
                    "Fin":     ahora_gantt,
                    "Estado":  "Ejecutando",
                    "Prioridad": f"Prio {proc['prioridad']}"
                })

        df_gantt = pd.DataFrame(datos_gantt)
        
        # Paleta de estados adaptativa con alto contraste y Playfair Display
        mapa_colores_gantt = {
            "Ejecutando": "#BF40FA",  # Hyper Magenta
            "Listo":      "#4928C2",  # Ultrasonic Blue
            "Bloqueado":  "#B8A8DC",  # Lavanda suave
            "Terminado":  "#6B7280"   # Gris Slate
        }
        grid_color = "rgba(168, 160, 150, 0.22)"

        fig_gantt = px.timeline(
            df_gantt,
            x_start="Inicio", x_end="Fin",
            y="Proceso", color="Estado",
            color_discrete_map=mapa_colores_gantt
        )
        fig_gantt.update_yaxes(
            autorange="reversed",
            tickfont=dict(size=12, family="Playfair Display"),
            title_font=dict(size=13, family="Playfair Display"),
            gridcolor=grid_color
        )
        fig_gantt.update_xaxes(
            tickfont=dict(size=11, family="Playfair Display"),
            title_font=dict(size=12, family="Playfair Display"),
            gridcolor=grid_color
        )
        fig_gantt.update_layout(
            height=290,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Playfair Display"),
            legend=dict(
                font=dict(family="Playfair Display", size=12),
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        st.plotly_chart(fig_gantt, use_container_width=True)

    with col_chart2:
        st.markdown("##### Distribución por Estado")
        df_proc = pd.DataFrame(procesos_actuales)
        if not df_proc.empty and "estado" in df_proc.columns:
            df_proc_copia = df_proc.copy()
            df_proc_copia["Estado"] = df_proc_copia["estado"].astype(str).str.capitalize()
            conteo_estados = df_proc_copia["Estado"].value_counts().reset_index()
            conteo_estados.columns = ["Estado", "Cantidad"]
            
            # Paleta circular de estados adaptativa con nombres capitalizados
            mapa_colores_pie = {
                "Ejecutando": "#BF40FA",  # Hyper Magenta
                "Listo":      "#4928C2",  # Ultrasonic Blue
                "Bloqueado":  "#B8A8DC",  # Lavanda suave
                "Terminado":  "#6B7280"   # Gris Slate
            }

            fig_pie = px.pie(
                conteo_estados,
                values="Cantidad", names="Estado",
                hole=0.48, color="Estado",
                color_discrete_map=mapa_colores_pie
            )
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent',
                textfont=dict(color="#FFFFFF", size=13, family="Playfair Display")
            )
            fig_pie.update_layout(
                height=290,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Playfair Display"),
                legend=dict(
                    font=dict(family="Playfair Display", size=12),
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5
                )
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.subheader("Tabla de Procesos en AutoOS")

    for p in procesos_actuales:
        col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns([2, 1, 1, 1, 2])
        with col_p1:
            critico_tag = "[ASIL-D]" if p.get("critico") else "[Estándar]"
            nombre_legible = formatear_nombre_proceso(p['nombre'])
            st.write(f"**PID {p['pid']}**: **{nombre_legible}** (`{p['nombre']}`) {critico_tag}")
        with col_p2:
            st.write(f"Prioridad: **{p['prioridad']}**")
        with col_p3:
            st.write(f"CPU: **{p['cpu']}%**")
        with col_p4:
            st.write(f"Estado: `{p['estado']}`")
        with col_p5:
            if es_admin:
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    nuevo_st = "bloqueado" if p["estado"] == "ejecutando" else "ejecutando"
                    label_st = "Pausar" if p["estado"] == "ejecutando" else "Reanudar"
                    if st.button(label_st, key=f"btn_st_{p['pid']}"):
                        ok, msg = cambiar_estado_proceso(p["pid"], nuevo_st, usuario_actual)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                with c_btn2:
                    if st.button("Terminar", key=f"btn_kill_{p['pid']}"):
                        ok, msg = finalizar_proceso(p["pid"], usuario_actual)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

            elif es_conductor:
                if not p.get("critico"):
                    nuevo_st = "bloqueado" if p["estado"] == "ejecutando" else "ejecutando"
                    label_st = "Pausar" if p["estado"] == "ejecutando" else "Reanudar"
                    if st.button(label_st, key=f"btn_st_{p['pid']}"):
                        ok, msg = cambiar_estado_proceso(p["pid"], nuevo_st, usuario_actual)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.caption("Proceso crítico protegido")

            else:
                st.caption("Solo lectura")


# --------------------------------------------------------------------
# 7. MEMORIA, ARCHIVOS Y LOGS
# --------------------------------------------------------------------
with tab_memoria:
    st.header("Memoria, Sistema de Archivos y Registros (Logs)")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.subheader("Uso de Memoria RAM")
        st.write(f"Total: **{memoria_info['total_mb']} MB (16 GB)**")
        st.write(f"Usada por Kernel: **{memoria_info['kernel_mb']} MB**")
        st.write(f"Usada por Procesos: **{memoria_info['procesos_mb']} MB**")
        st.write(f"Memoria Libre: **{memoria_info['libre_mb']} MB**")
        st.progress(memoria_info["pct_usado"] / 100.0)

        fig_mem = go.Figure()
        fig_mem.add_trace(go.Bar(
            name="Kernel (Reservado)",
            y=["Memoria RAM"], x=[memoria_info["kernel_mb"]],
            orientation="h", marker_color=paleta['danger']
        ))
        fig_mem.add_trace(go.Bar(
            name="Procesos",
            y=["Memoria RAM"], x=[memoria_info["procesos_mb"]],
            orientation="h", marker_color=paleta['accent_second']
        ))
        fig_mem.add_trace(go.Bar(
            name="Libre",
            y=["Memoria RAM"], x=[memoria_info["libre_mb"]],
            orientation="h", marker_color=paleta['accent_primary']
        ))
        fig_mem.update_layout(
            barmode="stack", height=160,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Playfair Display", color=paleta['text_primary']),
            legend=dict(
                font=dict(family="Playfair Display", color=paleta['text_primary']),
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            )
        )
        fig_mem.update_xaxes(tickfont=dict(family="Playfair Display", color=paleta['text_primary']))
        fig_mem.update_yaxes(tickfont=dict(family="Playfair Display", color=paleta['text_primary']))
        st.plotly_chart(fig_mem, use_container_width=True)

    with col_m2:
        st.subheader("Carpetas y Archivos Base del Vehículo")
        archivos_df = pd.DataFrame(obtener_sistema_archivos())
        st.dataframe(archivos_df[["ruta", "tipo", "tamano_kb", "permisos"]], hide_index=True)

    st.markdown("---")
    st.subheader("Visor de Logs del Sistema (Kernel Logs)")
    if es_admin:
        logs_data = obtener_logs_sistema(10)
        st.dataframe(pd.DataFrame(logs_data), hide_index=True, use_container_width=True)
    else:
        render_acceso_denegado("Visor de Logs del Kernel", "Mecánico / Admin")
