"""
====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Dashboard Principal de Control e Integración
====================================================================
"""

import streamlit as st
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
    render_acceso_denegado, obtener_paleta, render_reloj_en_vivo
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
    st.markdown("### AutoOS Cockpit v2.4")
    st.caption("Sistema Operativo para Vehículo Inteligente")

    # Aplicar estilos con sincronización nativa de Streamlit (Light / Dark)
    aplicar_estilos_cockpit()
    modo_tema = "auto"
    paleta = obtener_paleta("oscuro")

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
    st.title("AutoOS Dashboard")
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
        render_card_telemetria(
            titulo="Uso Total de CPU",
            valor=cpu_total,
            unidad="%",
            subtexto="4 Cores activos · RTOS",
            color_acento="#BF40FA",
            max_val=100.0,
            modo=modo_tema
        )
    with col_g2:
        render_card_telemetria(
            titulo="Uso de Memoria RAM",
            valor=memoria_info["pct_usado"],
            unidad="%",
            subtexto=f"{memoria_info['procesos_mb']} MB / 16 GB",
            color_acento="#4928C2",
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

    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.markdown(f"""
            <div class="auto-card">
                <h4>Hardware y Periféricos</h4>
                <div>Total dispositivos: <b>{resumen_dev['total']}</b></div>
                <div style="color: {paleta['success']};">Operativos: <b>{resumen_dev['operativos']}</b></div>
                <div style="color: {paleta['warning']};">Degradados: <b>{resumen_dev['degradados']}</b></div>
                <div style="color: {paleta['danger']};">Fallas / Desconectados: <b>{resumen_dev['fallas'] + resumen_dev['desconectados']}</b></div>
            </div>
        """, unsafe_allow_html=True)
    with col_res2:
        st.markdown(f"""
            <div class="auto-card">
                <h4>Procesos Vehiculares</h4>
                <div>Procesos totales: <b>{len(db['procesos'])}</b></div>
                <div>Ejecutando: <b>{sum(1 for p in db['procesos'] if p['estado'] == 'ejecutando')}</b></div>
                <div>Críticos (ASIL): <b>{sum(1 for p in db['procesos'] if p.get('critico'))}</b></div>
                <div>Carga CPU: <b>{cpu_total}%</b></div>
            </div>
        """, unsafe_allow_html=True)
    with col_res3:
        if es_admin:
            st.markdown(f"""
                <div class="auto-card">
                    <h4>Seguridad y Acceso</h4>
                    <div>Usuario: <b>{usuario_actual['nombre_completo']}</b></div>
                    <div>Rol: <b>{info_rol.get('etiqueta')}</b></div>
                    <div>Bloqueados hoy: <b>{sum(1 for a in db['auditoria'] if not a['autorizado'])}</b></div>
                    <div>Políticas RLS: <b>100% activas</b></div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="auto-card">
                    <h4>Sesión Activa</h4>
                    <div>Usuario: <b>{usuario_actual['nombre_completo']}</b></div>
                    <div>Rol: <b>{info_rol.get('etiqueta')}</b></div>
                    <div>Nivel de acceso: <b>{info_rol.get('nivel')}/10</b></div>
                    <div style="color: {paleta['text_muted']};">{info_rol.get('descripcion', '')[:60]}...</div>
                </div>
            """, unsafe_allow_html=True)

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
