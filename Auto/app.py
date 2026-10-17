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

# Configuración de página de Streamlit sin emojis
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
    crear_gauge_bateria, crear_gauge_circular, render_tarjeta_dispositivo,
    render_acceso_denegado
)

# Aplicar temas visuales (paleta personalizada para claro y oscuro)
aplicar_estilos_cockpit()

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


# ====================================================================
# BARRA LATERAL (CONTROL DE SESIÓN Y CREDENCIALES)
# ====================================================================
with st.sidebar:
    st.markdown("### AutoOS Cockpit v2.4")
    st.caption("Sistema Operativo para Vehículo Inteligente")

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
# ENCABEZADO Y SEMÁFORO GENERAL
# ====================================================================
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("AutoOS Dashboard")
    st.caption("Plataforma de Simulación del Sistema Operativo Vehicular & Control de Seguridad")
with col_head2:
    st.metric("Reloj de Sistema", datetime.datetime.now().strftime("%H:%M:%S"), delta="RTOS Synced")

render_banner_semaforo(semaforo)


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

    col_g1, col_g2, col_g3, col_g4 = st.columns(4)
    with col_g1:
        st.plotly_chart(crear_gauge_circular(cpu_total, "Uso Total de CPU", "%", 100.0, "#BF40FA"), use_container_width=True)
    with col_g2:
        st.plotly_chart(crear_gauge_circular(memoria_info["pct_usado"], "Uso de RAM", "%", 100.0, "#4928C2"), use_container_width=True)
    with col_g3:
        st.plotly_chart(crear_gauge_bateria(bateria["soc_pct"], bateria["temp_c"]), use_container_width=True)
    with col_g4:
        st.plotly_chart(crear_gauge_circular(resumen_dev["salud_promedio"], "Salud Dispositivos", "%", 100.0, "#34d399"), use_container_width=True)

    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.markdown(f"""
            <div class="auto-card">
                <h4>Hardware y Periféricos</h4>
                <div>Total dispositivos: <b>{resumen_dev['total']}</b></div>
                <div style="color: #34d399;">Operativos: <b>{resumen_dev['operativos']}</b></div>
                <div style="color: #fbbf24;">Degradados: <b>{resumen_dev['degradados']}</b></div>
                <div style="color: #f87171;">Fallas / Desconectados: <b>{resumen_dev['fallas'] + resumen_dev['desconectados']}</b></div>
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
                    <div style="color: var(--text-muted);">{info_rol.get('descripcion', '')[:60]}...</div>
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
            render_tarjeta_dispositivo(dev)

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

    col_bat1, col_bat2, col_bat3 = st.columns(3)
    with col_bat1:
        st.metric("Estado de Carga (SoC)", f"{bateria['soc_pct']}%", delta=bateria["modo_actual"])
    with col_bat2:
        st.metric("Voltaje del Paquete", f"{bateria['voltaje_v']} V", delta="398V Nominal")
    with col_bat3:
        st.metric("Temperatura de Celdas", f"{bateria['temp_c']} °C", delta="Máx tolerado: 55°C", delta_color="inverse")

    st.markdown("---")

    if es_admin:
        st.subheader("Simulador de Descarga y Estado de Batería")
        st.caption("Ajuste directo de parámetros del BMS de alta tensión:")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            nuevo_soc = st.slider("Ajustar Nivel de Carga (SoC %):", 0.0, 100.0, float(bateria["soc_pct"]))
        with col_s2:
            nueva_temp = st.slider("Ajustar Temperatura BMS (°C):", 15.0, 70.0, float(bateria["temp_c"]))
        with col_s3:
            st.write("")
            st.write("")
            if st.button("Actualizar Parámetros BMS", use_container_width=True):
                actualizar_bateria(nuevo_soc, nueva_temp)
                st.success("Parámetros de batería actualizados en el bus CAN.")
                st.rerun()

    elif es_conductor:
        st.subheader("Perfil de Conducción y Modo Energético")
        st.caption("Como conductor puedes alternar el perfil de conducción vehicular:")
        modo_elegido = st.radio(
            "Modo de conducción:",
            options=["Eco", "Normal", "Sport"],
            horizontal=True,
            index=["Eco", "Normal", "Sport"].index(bateria.get("modo_conduccion", "Normal")) if bateria.get("modo_conduccion") in ["Eco", "Normal", "Sport"] else 1
        )
        if st.button("Aplicar Modo"):
            actualizar_bateria(bateria["soc_pct"], bateria["temp_c"], modo_conduccion=modo_elegido)
            st.success(f"Modo '{modo_elegido}' activado.")
            st.rerun()

        st.markdown("---")
        render_acceso_denegado("Ajuste Directo de Parámetros BMS", "Mecánico / Admin")

    else:
        st.info("Modo de consulta. El rol de Pasajero tiene acceso de solo lectura a la telemetría energética.")


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
                    <div style="font-weight: 700; color: #BF40FA; font-size: 14px;">{paso['fase']}</div>
                    <div style="color: #E3D9FC; font-size: 13px; margin-top: 4px;">{paso['accion']}</div>
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
            datos_gantt.append({
                "Proceso": f"PID {proc['pid']}: {proc['nombre']}",
                "Inicio":  ahora_gantt - datetime.timedelta(seconds=offset + duracion),
                "Fin":     ahora_gantt - datetime.timedelta(seconds=offset),
                "Estado":  proc["estado"].capitalize(),
                "Prioridad": f"Prio {proc['prioridad']}"
            })
            if proc["estado"] == "ejecutando":
                datos_gantt.append({
                    "Proceso": f"PID {proc['pid']}: {proc['nombre']}",
                    "Inicio":  ahora_gantt - datetime.timedelta(seconds=3),
                    "Fin":     ahora_gantt,
                    "Estado":  "Ejecutando",
                    "Prioridad": f"Prio {proc['prioridad']}"
                })

        df_gantt = pd.DataFrame(datos_gantt)
        fig_gantt = px.timeline(
            df_gantt,
            x_start="Inicio", x_end="Fin",
            y="Proceso", color="Estado",
            color_discrete_map={
                "Ejecutando": "#BF40FA",
                "Listo":      "#4928C2",
                "Bloqueado":  "#fbbf24",
                "Terminado":  "#5B2A62"
            }
        )
        fig_gantt.update_yaxes(autorange="reversed")
        fig_gantt.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#E3D9FC"
        )
        st.plotly_chart(fig_gantt, use_container_width=True)

    with col_chart2:
        st.markdown("##### Distribución por Estado")
        df_proc = pd.DataFrame(procesos_actuales)
        if not df_proc.empty and "estado" in df_proc.columns:
            conteo_estados = df_proc["estado"].value_counts().reset_index()
            conteo_estados.columns = ["Estado", "Cantidad"]
            fig_pie = px.pie(
                conteo_estados,
                values="Cantidad", names="Estado",
                hole=0.45, color="Estado",
                color_discrete_map={
                    "ejecutando": "#BF40FA",
                    "listo":      "#4928C2",
                    "bloqueado":  "#fbbf24",
                    "terminado":  "#5B2A62"
                }
            )
            fig_pie.update_layout(
                height=280,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#E3D9FC"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.subheader("Tabla de Procesos en AutoOS")

    for p in procesos_actuales:
        col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns([2, 1, 1, 1, 2])
        with col_p1:
            critico_tag = "[ASIL-D]" if p.get("critico") else "[Estándar]"
            st.write(f"**PID {p['pid']}**: `{p['nombre']}` {critico_tag}")
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
                # El conductor solo puede pausar/reanudar procesos no críticos
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
            orientation="h", marker_color="#f87171"
        ))
        fig_mem.add_trace(go.Bar(
            name="Procesos",
            y=["Memoria RAM"], x=[memoria_info["procesos_mb"]],
            orientation="h", marker_color="#4928C2"
        ))
        fig_mem.add_trace(go.Bar(
            name="Libre",
            y=["Memoria RAM"], x=[memoria_info["libre_mb"]],
            orientation="h", marker_color="#BF40FA"
        ))
        fig_mem.update_layout(
            barmode="stack", height=160,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#E3D9FC",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
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
