"""====================================================================
AUTOOS - DASHBOARD DE CPU Y PLANIFICADOR DE PROCESOS
Responsable: Integrante 1 (CPU & Scheduling Engine)
====================================================================
Implementación visual completa en Python y Streamlit con estética de cockpit automotriz, gráfica de Gantt reactiva y simuladores integrados.
Soporte dinámico para Modo Oscuro (Purple Night) y Modo Claro (Soft Dove).
===================================================================="""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from modulos.int1_cpu import simular_planificacion, PROCESOS_DEFECTO

def mostrar(supabase=None):
    """Renderiza la vista completa de CPU y Planificación de Procesos con la estética de Cockpit AutoOS."""
    
    # Obtener tema global y rol desde session_state
    tema = st.session_state.get("autoos_theme", "dark")
    is_dark = (tema == "dark")
    rol_actual = st.session_state.get("autoos_user_role", "admin")

    # Colores dinámicos Cockpit AutoOS
    bg_card = "#180E24" if is_dark else "#E3DDD7"
    border_col = "#331E4D" if is_dark else "#A8A096"
    text_primary = "#E3D9FC" if is_dark else "#160F0C"
    text_muted = "#8D7AA8" if is_dark else "#52423D"
    accent_col = "#BF40FA" if is_dark else "#391214"
    plot_bg = "#0D0714" if is_dark else "#D5CFC9"
    paper_bg = "#180E24" if is_dark else "#E3DDD7"

    # Inyección de estilos CSS idénticos al Cockpit AutoOS
    st.markdown(f"""
    <style>
        .autoos-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid {border_col};
            padding-bottom: 12px;
            margin-bottom: 20px;
        }}
        .autoos-title {{
            margin: 0;
            color: {text_primary};
            font-family: 'Playfair Display', Georgia, serif;
            font-weight: 800;
            letter-spacing: 0.04em;
            font-size: 1.5rem;
        }}
        .autoos-subtitle {{
            margin: 4px 0 0 0;
            color: {text_muted};
            font-size: 0.85rem;
            font-family: 'Outfit', sans-serif;
        }}
        .cpu-card {{
            background-color: {bg_card};
            border: 1px solid {border_col};
            border-radius: 16px;
            padding: 18px;
            margin-bottom: 14px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            transition: all 0.2s ease;
        }}
        .metric-value {{
            font-size: 1.8rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            color: {accent_col};
        }}
        .metric-title {{
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {text_muted};
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
        }}
        .badge-critical {{
            background-color: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.35);
            border-radius: 8px;
            padding: 3px 10px;
            font-size: 0.75rem;
            font-family: 'JetBrains Mono', monospace;
            font-weight: bold;
        }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="autoos-header">
        <div>
            <h2 class="autoos-title">
                ⚡ AutoOS — Planificador de Procesos y Simuladores
            </h2>
            <p class="autoos-subtitle">
                Despacho de CPU multialgoritmo (FCFS, Round Robin, Prioridad) y simuladores de contingencia vehicular.
            </p>
        </div>
        <div>
            <span class="badge-critical">ASIL-D RTOS CORE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Verificación de Rol Pasajero
    if rol_actual == "guest":
        st.warning("⚠️ **Modo Solo Lectura (Pasajero):** El rol de pasajero no posee permisos para modificar los algoritmos del Kernel o disparar fallas críticas.")

    # Control de estado de sesión
    if "sim_bateria_baja" not in st.session_state:
        st.session_state.sim_bateria_baja = False
    if "sim_nivel_bateria" not in st.session_state:
        st.session_state.sim_nivel_bateria = 85
    if "sim_proceso_critico" not in st.session_state:
        st.session_state.sim_proceso_critico = False

    # 1. SELECTOR DE ALGORITMO Y QUANTUM
    col_alg, col_param = st.columns([3, 2])
    with col_alg:
        algoritmo_opcion = st.radio(
            "Algoritmo de Planificación:",
            options=[
                "Round Robin (RR)",
                "FCFS (Primero en Llegar)",
                "Prioridad No Apropiativa",
                "Prioridad Apropiativa (Preemptive)"
            ],
            horizontal=True,
            index=0,
            disabled=(rol_actual == "guest")
        )

    if "Round Robin" in algoritmo_opcion:
        cod_algoritmo = "RR"
    elif "FCFS" in algoritmo_opcion:
        cod_algoritmo = "FCFS"
    elif "Apropiativa" in algoritmo_opcion:
        cod_algoritmo = "PRIORITY_PREEMPTIVE"
    else:
        cod_algoritmo = "PRIORITY"

    with col_param:
        if cod_algoritmo == "RR":
            quantum = st.slider(
                "Quantum de Tiempo (segundos):",
                min_value=1,
                max_value=6,
                value=2,
                step=1,
                disabled=(rol_actual == "guest")
            )
        else:
            st.info(f"Política: {cod_algoritmo}. Despacho determinista para RTOS.")
            quantum = 2

    st.divider()

    # 2. SIMULADORES DE CONTINGENCIA (BATERÍA BAJA Y PROCESO CRÍTICO)
    st.markdown("### 🚨 Simuladores de Contingencia de Cockpit AutoOS")
    col_sim_bat, col_sim_crit = st.columns(2)

    with col_sim_bat:
        st.markdown(f"""
        <div class="cpu-card">
            <h4 style="margin:0 0 8px 0; color: #fbbf24; font-family: 'Playfair Display', serif; font-size: 1.05rem;">
                ⚡ Simulador: Batería de Tracción Baja (Limp-Mode)
            </h4>
            <p style="font-size: 0.8rem; color: {text_muted}; margin-bottom: 10px; font-family: 'Outfit', sans-serif;">
                Al descender por debajo del 20%, el BMS activa Limp-Mode: suspende confort/multimedia para reservar potencia al motor y frenos.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        nivel_bat = st.slider(
            "Nivel de Carga Batería HV (%):",
            min_value=5,
            max_value=100,
            value=st.session_state.sim_nivel_bateria,
            step=1,
            key="slider_bat",
            disabled=(rol_actual == "guest")
        )
        st.session_state.sim_nivel_bateria = nivel_bat
        st.session_state.sim_bateria_baja = (nivel_bat <= 20)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚨 Forzar Batería Baja (15%)", use_container_width=True, disabled=(rol_actual == "guest")):
                st.session_state.sim_nivel_bateria = 15
                st.session_state.sim_bateria_baja = True
                st.rerun()
        with c2:
            if st.button("🔋 Cargar Batería (90%)", use_container_width=True, disabled=(rol_actual == "guest")):
                st.session_state.sim_nivel_bateria = 90
                st.session_state.sim_bateria_baja = False
                st.rerun()

        if st.session_state.sim_bateria_baja:
            st.warning(f"⚡ [LIMP-MODE ACTIVO: {nivel_bat}%] Procesos de infoentretenimiento y confort suspendidos temporalmente.")

    with col_sim_crit:
        st.markdown(f"""
        <div class="cpu-card">
            <h4 style="margin:0 0 8px 0; color: #f87171; font-family: 'Playfair Display', serif; font-size: 1.05rem;">
                🚨 Simulador: Proceso Crítico (ASIL-D / ISO 26262)
            </h4>
            <p style="font-size: 0.8rem; color: {text_muted}; margin-bottom: 10px; font-family: 'Outfit', sans-serif;">
                Inyecta una falla crítica de hardware (Frenado AEB o Fallo de Dirección) con Prioridad 1 y desalojo preemptivo inmediato de CPU.
            </p>
        </div>
        """, unsafe_allow_html=True)

        c_crit1, c_crit2 = st.columns(2)
        with c_crit1:
            if st.button("💥 Inyectar Frenado AEB", use_container_width=True, type="primary", disabled=(rol_actual == "guest")):
                st.session_state.sim_proceso_critico = True
                st.rerun()
        with c_crit2:
            if st.button("✓ Normalizar Procesos", use_container_width=True, disabled=(rol_actual == "guest")):
                st.session_state.sim_proceso_critico = False
                st.rerun()

        if st.session_state.sim_proceso_critico:
            st.error("🚨 PROCESO CRÍTICO ACTIVO: 'Frenado Autónomo de Emergencia (AEB)' inyectado con Prioridad 1.")

    # 3. EJECUCIÓN DEL MOTOR DE SIMULACIÓN Y MÉTRICAS
    resultado = simular_planificacion(
        algoritmo=cod_algoritmo,
        quantum=quantum,
        bateria_baja=st.session_state.sim_bateria_baja,
        inyectar_critico=st.session_state.sim_proceso_critico
    )

    st.markdown("### 📊 Indicadores de Rendimiento del Despachador")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="cpu-card" style="text-align: center;">
            <div class="metric-title">T. Espera Promedio</div>
            <div class="metric-value">{resultado['espera_promedio']}s</div>
            <span style="font-size: 0.7rem; color: {text_muted}; font-family: monospace;">(Tiempo en cola)</span>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="cpu-card" style="text-align: center;">
            <div class="metric-title">T. Retorno Promedio</div>
            <div class="metric-value" style="color: {text_primary};">{resultado['retorno_promedio']}s</div>
            <span style="font-size: 0.7rem; color: {text_muted}; font-family: monospace;">(Turnaround Time)</span>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="cpu-card" style="text-align: center;">
            <div class="metric-title">Uso de CPU</div>
            <div class="metric-value" style="color: #34d399;">{resultado['cpu_utilizacion']}%</div>
            <span style="font-size: 0.7rem; color: {text_muted}; font-family: monospace;">(Tiempo productivo)</span>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="cpu-card" style="text-align: center;">
            <div class="metric-title">Conmutaciones Contexto</div>
            <div class="metric-value" style="color: #f472b6;">{resultado['conmutaciones']}</div>
            <span style="font-size: 0.7rem; color: {text_muted}; font-family: monospace;">(Desalojos / Cambios)</span>
        </div>
        """, unsafe_allow_html=True)

    # 4. DIAGRAMA DE GANTT REACTIVO CON ESTÉTICA COCKPIT
    st.markdown("### 📈 Diagrama de Gantt — Trazabilidad Temporal de CPU")
    slots = resultado["gantt_slots"]
    if slots:
        df_gantt = pd.DataFrame(slots)
        tiempo_base = pd.Timestamp.now()
        df_gantt["inicio_dt"] = df_gantt["inicio"].apply(lambda s: tiempo_base + pd.Timedelta(seconds=s))
        df_gantt["fin_dt"] = df_gantt["fin"].apply(lambda s: tiempo_base + pd.Timedelta(seconds=s))
        df_gantt["duracion_seg"] = df_gantt["fin"] - df_gantt["inicio"]
        df_gantt["rango_seg"] = df_gantt.apply(lambda r: f"{r['inicio']}s a {r['fin']}s ({r['duracion_seg']}s)", axis=1)

        color_map = {row["proceso"]: row["color"] for _, row in df_gantt.iterrows()}

        fig = px.timeline(
            df_gantt,
            x_start="inicio_dt",
            x_end="fin_dt",
            y="proceso",
            color="proceso",
            color_discrete_map=color_map,
            hover_data={
                "inicio_dt": False,
                "fin_dt": False,
                "proceso": True,
                "duracion_seg": True,
                "rango_seg": True,
                "prioridad": True
            },
            title=f"Planificación de CPU: {algoritmo_opcion} (Duración total: {resultado['tiempo_total']}s)"
        )
        fig.update_layout(
            paper_bgcolor=paper_bg,
            plot_bgcolor=plot_bg,
            font=dict(color=text_primary, family="JetBrains Mono"),
            showlegend=False,
            height=340,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(
                showgrid=True,
                gridcolor=border_col,
                tickformat="%M:%S",
                title="Eje Temporal de Despacho (Min:Seg)"
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=border_col,
                autorange="reversed",
                title="Proceso en Ejecución"
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Iniciando despacho temporal de procesos...")

    # 5. TABLA DE BLOQUES DE CONTROL DE PROCESO (PCB)
    st.markdown("### 📋 Tabla de Bloques de Control de Proceso (PCB)")
    procs_df = pd.DataFrame([
        {
            "PID": f"P{p['id']}",
            "Nombre del Proceso": p["nombre"],
            "Categoría": p["categoria"].upper(),
            "Prioridad": "1 (Crítica)" if p["prioridad"] == 1 else p["prioridad"],
            "T. Llegada (AT)": f"{p['llegada']}s",
            "Ráfaga (BT)": f"{p['rafaga']}s",
            "T. Fin (CT)": f"{p.get('fin', '-')}s" if p.get('fin') is not None else "-",
            "T. Retorno (TAT)": f"{p.get('retorno', '-')}s" if p.get('retorno') is not None else "-",
            "T. Espera (WT)": f"{p.get('espera', '-')}s" if p.get('espera') is not None else "-",
            "Estado": p["estado"]
        }
        for p in resultado["procesos"]
    ])
    st.dataframe(procs_df, use_container_width=True, hide_index=True)
