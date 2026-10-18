"""
====================================================================
AUTOOS - DASHBOARD DE CPU Y PLANIFICADOR DE PROCESOS
Responsable: Integrante 1 (CPU & Scheduling Engine)
====================================================================
Implementación visual completa en Python y Streamlit con estética de
cockpit automotriz, gráfica de Gantt reactiva y simuladores integrados.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from modulos.int1_cpu import simular_planificacion, PROCESOS_DEFECTO

def mostrar(supabase=None):
    """Renderiza la vista completa de CPU y Planificación de Procesos."""
    
    # Inyección de estilos CSS para réplica exacta de la interfaz vehicular
    st.markdown("""
    <style>
        .cpu-card {
            background: linear-gradient(135deg, rgba(15,23,42,0.9) 0%, rgba(30,41,59,0.8) 100%);
            border: 1px solid rgba(51,65,85,0.7);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
        }
        .metric-title {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #94a3b8;
            font-family: monospace;
        }
        .badge-critical {
            background-color: rgba(239, 68, 68, 0.2);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.4);
            border-radius: 6px;
            padding: 2px 8px;
            font-size: 0.75rem;
            font-weight: bold;
        }
        .badge-eco {
            background-color: rgba(245, 158, 11, 0.2);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.4);
            border-radius: 6px;
            padding: 2px 8px;
            font-size: 0.75rem;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; border-b: 1px solid #334155; padding-bottom: 8px; margin-bottom: 16px;">
        <div>
            <h2 style="margin: 0; color: #f8fafc; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em;">
                🖥️ AutoOS — Planificador de Procesos de CPU
            </h2>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.85rem;">
                Simulación visual interactiva de algoritmos de despacho (FCFS, Round Robin, Prioridad) y respuesta ante contingencias.
            </p>
        </div>
        <div>
            <span class="badge-critical">NÚCLEO RTOS ASIL-D</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # CONTROL DE ESTADO DE SESIÓN (SIMULADORES)
    # -------------------------------------------------------------
    if "sim_bateria_baja" not in st.session_state:
        st.session_state.sim_bateria_baja = False
    if "sim_nivel_bateria" not in st.session_state:
        st.session_state.sim_nivel_bateria = 85
    if "sim_proceso_critico" not in st.session_state:
        st.session_state.sim_proceso_critico = False

    # -------------------------------------------------------------
    # SECCIÓN 1: SELECTOR DE ALGORITMO Y PARÁMETROS
    # -------------------------------------------------------------
    col_alg, col_param = st.columns([3, 2])

    with col_alg:
        algoritmo_opcion = st.radio(
            "Seleccione el Algoritmo de Planificación:",
            options=[
                "Round Robin (RR)",
                "FCFS (First-Come, First-Served)",
                "Prioridad No Apropiativa",
                "Prioridad Apropiativa (Preemptive)"
            ],
            horizontal=True,
            index=0
        )

    # Mapeo a código interno
    if "Round Robin" in algoritmo_opcion:
        cod_algoritmo = "RR"
    elif "FCFS" in algoritmo_opcion:
        cod_algoritmo = "FCFS"
    elif "Apropiativa (Preemptive)" in algoritmo_opcion:
        cod_algoritmo = "PRIORITY_PREEMPTIVE"
    else:
        cod_algoritmo = "PRIORITY"

    with col_param:
        if cod_algoritmo == "RR":
            quantum = st.slider("Quantum de Tiempo (segundos):", min_value=1, max_value=6, value=2, step=1)
        else:
            quantum = 2
            st.info(f"📌 Algoritmo activo: **{algoritmo_opcion}** (No requiere quantum)")

    # -------------------------------------------------------------
    # SECCIÓN 2: SIMULADORES INTEGRADOS (BATERÍA BAJA & PROCESO CRÍTICO)
    # -------------------------------------------------------------
    st.markdown("### 🎛️ Simuladores Vehiculares en Vivo")
    col_sim_bat, col_sim_crit = st.columns(2)

    with col_sim_bat:
        st.markdown("""
        <div class="cpu-card">
            <h4 style="margin:0 0 8px 0; color: #fbbf24; font-size: 0.95rem;">
                🔋 Simulador: Batería Baja Vehicular
            </h4>
            <p style="font-size: 0.78rem; color: #94a3b8; margin-bottom: 8px;">
                Al activarse (<20%), el sistema suspende procesos no vitales (infoentretenimiento, clima) para priorizar seguridad.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        nivel_bat = st.slider(
            "Nivel de Carga Batería HV (%):",
            min_value=5,
            max_value=100,
            value=st.session_state.sim_nivel_bateria,
            step=1
        )
        st.session_state.sim_nivel_bateria = nivel_bat
        
        # Activar automáticamente si < 20%
        es_baja = nivel_bat <= 20
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🟡 Forzar Batería Baja (15%)", use_container_width=True):
                st.session_state.sim_nivel_bateria = 15
                st.session_state.sim_bateria_baja = True
                st.rerun()
        with c2:
            if st.button("🟢 Restaurar Batería (90%)", use_container_width=True):
                st.session_state.sim_nivel_bateria = 90
                st.session_state.sim_bateria_baja = False
                st.rerun()
        
        st.session_state.sim_bateria_baja = (nivel_bat <= 20)

    with col_sim_crit:
        st.markdown("""
        <div class="cpu-card">
            <h4 style="margin:0 0 8px 0; color: #f87171; font-size: 0.95rem;">
                🚨 Simulador: Inyección de Proceso Crítico (ASIL-D)
            </h4>
            <p style="font-size: 0.78rem; color: #94a3b8; margin-bottom: 8px;">
                Simula una emergencia vehicular inminente (ej. AEB) con Prioridad 1 y desalojo inmediato (preemption) de CPU.
            </p>
        </div>
        """, unsafe_allow_html=True)

        c_crit1, c_crit2 = st.columns(2)
        with c_crit1:
            if st.button("🚨 Inyectar Frenado AEB", use_container_width=True, type="primary"):
                st.session_state.sim_proceso_critico = True
                st.rerun()
        with c_crit2:
            if st.button("🔄 Normalizar Procesos", use_container_width=True):
                st.session_state.sim_proceso_critico = False
                st.rerun()

        if st.session_state.sim_proceso_critico:
            st.warning("⚠️ PROCESO CRÍTICO ACTIVO: 'Frenado Autónomo de Emergencia' inyectado en t=3s.")

    # -------------------------------------------------------------
    # SECCIÓN 3: EJECUCIÓN DE LA SIMULACIÓN Y MÉTRICAS
    # -------------------------------------------------------------
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
            <div class="metric-title">Tiempo Espera Promedio</div>
            <div class="metric-value" style="color: #38bdf8;">{resultado['espera_promedio']}s</div>
            <span style="font-size: 0.7rem; color: #64748b;">(T. medio en cola)</span>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="cpu-card" style="text-align: center;">
            <div class="metric-title">Tiempo Retorno Promedio</div>
            <div class="metric-value" style="color: #818cf8;">{resultado['retorno_promedio']}s</div>
            <span style="font-size: 0.7rem; color: #64748b;">(Turnaround Time)</span>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="cpu-card" style="text-align: center;">
            <div class="metric-title">Utilización de CPU</div>
            <div class="metric-value" style="color: #34d399;">{resultado['cpu_utilizacion']}%</div>
            <span style="font-size: 0.7rem; color: #64748b;">(Tiempo productivo)</span>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="cpu-card" style="text-align: center;">
            <div class="metric-title">Conmutaciones Contexto</div>
            <div class="metric-value" style="color: #f472b6;">{resultado['conmutaciones']}</div>
            <span style="font-size: 0.7rem; color: #64748b;">(Cambios de proceso)</span>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # SECCIÓN 4: DIAGRAMA DE GANTT REACTIVO Y VISUAL
    # -------------------------------------------------------------
    st.markdown("### 📈 Diagrama de Gantt — Trazabilidad Temporal de CPU")
    
    slots = resultado["gantt_slots"]
    if slots:
        df_gantt = pd.DataFrame(slots)
        
        # Asignar tiempo base para representación continua
        tiempo_base = pd.Timestamp.now()
        df_gantt["inicio_dt"] = df_gantt["inicio"].apply(lambda s: tiempo_base + pd.Timedelta(seconds=s))
        df_gantt["fin_dt"] = df_gantt["fin"].apply(lambda s: tiempo_base + pd.Timedelta(seconds=s))
        df_gantt["duracion_seg"] = df_gantt["fin"] - df_gantt["inicio"]
        df_gantt["rango_seg"] = df_gantt.apply(lambda r: f"{r['inicio']}s a {r['fin']}s ({r['duracion_seg']}s)", axis=1)

        # Mapa de colores idéntico al cockpit vehicular
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
            title=f"Planificación de CPU bajo política: {algoritmo_opcion} (Duración total: {resultado['tiempo_total']}s)"
        )

        fig.update_layout(
            paper_bgcolor="rgba(15,23,42,0.9)",
            plot_bgcolor="rgba(15,23,42,0.9)",
            font=dict(color="#f8fafc", family="JetBrains Mono"),
            showlegend=False,
            height=340,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(
                showgrid=True,
                gridcolor="#1e293b",
                tickformat="%M:%S",
                title="Eje Temporal de Despacho (Min:Seg)"
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#1e293b",
                autorange="reversed",
                title="Proceso en Ejecución"
            )
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos disponibles para el diagrama de Gantt.")

    # -------------------------------------------------------------
    # SECCIÓN 5: TABLA DE CONTROL DE PROCESOS (PCB)
    # -------------------------------------------------------------
    st.markdown("### 📋 Tabla de Bloques de Control de Proceso (PCB)")
    procs_df = pd.DataFrame([
        {
            "PID": f"P{p['id']}",
            "Nombre del Proceso": p["nombre"],
            "Categoría": p["categoria"].upper(),
            "Prioridad": "1 (Crítica)" if p["prioridad"] == 1 else p["prioridad"],
            "T. Llegada (AT)": f"{p['llegada']}s",
            "Ráfaga (BT)": f"{p['rafaga']}s",
            "T. Fin (CT)": f"{p['fin']}s" if p.get("fin") is not None else "-",
            "T. Retorno (TAT)": f"{p.get('retorno', '-')}s" if p.get("retorno") is not None else "-",
            "T. Espera (WT)": f"{p.get('espera', '-')}s" if p.get("espera") is not None else "-",
            "Estado": p["estado"]
        }
        for p in resultado["procesos"]
    ])
    st.dataframe(procs_df, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------
    # SECCIÓN 6: RESUMEN COMPARATIVO TEÓRICO
    # -------------------------------------------------------------
    with st.expander("📚 Comparativa Teórica de Algoritmos para AutoOS", expanded=False):
        st.markdown(f"""
        | Algoritmo | Tiempo de Espera | Cambios de Contexto | Aptitud para AutoOS |
        |---|---|---|---|
        | **FCFS** | Alto (Efecto Convoy) | Mínimo | No recomendado para tiempo real. Tareas críticas pueden quedar bloqueadas. |
        | **Round Robin (q={quantum}s)** | Equilibrado / Predecible | Medio/Alto | Ideal para interactividad y telemetría de usuario. |
        | **Prioridad No Apropiativa** | Bajo para tareas P1 | Bajo | Aceptable, pero un proceso largo no crítico puede retrasar un freno. |
        | **Prioridad Apropiativa** | Mínimo para seguridad | Medio | **Obligatorio para sistemas ASIL-D (Frenos, Dirección, Airbag).** |
        """)
