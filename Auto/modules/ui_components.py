"""
====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Módulo: ui_components.py
Responsable: Componentes Visuales de Alta Fidelidad para Cockpit
====================================================================
Paleta Modo Claro — Soft Dove:
  #C0BAB3  Soft Dove      — fondo base
  #52423D  Spiced Choco   — texto principal / sidebar
  #887D77  Moon Rock      — texto secundario
  #391214  Dark Sienna    — acentos / headers
  #160F0C  Black Raspberry— texto oscuro

Paleta Modo Oscuro — Purple Night:
  #E3D9FC  Periwinkle     — texto claro / highlights
  #BF40FA  Hyper Magenta  — acento primario
  #4928C2  Ultrasonic Blue— acento secundario
  #5B2A62  Velvet Purple  — contenedores / cards
  #040607  Black          — fondo base
====================================================================
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any


def aplicar_estilos_cockpit():
    """Aplica el sistema de diseño dual (claro/oscuro) usando las paletas personalizadas."""
    st.markdown("""
        <style>
        /* ============================================================
           VARIABLES DE TEMA — MODO OSCURO (por defecto en Streamlit)
           ============================================================ */
        :root {
            --bg-base:        #040607;
            --bg-surface:     #0e0a1a;
            --bg-card:        #150e24;
            --bg-card-hover:  #1e1535;
            --border-subtle:  #2a1f40;
            --border-accent:  #4928C2;
            --accent-primary: #BF40FA;
            --accent-second:  #4928C2;
            --accent-third:   #5B2A62;
            --text-primary:   #E3D9FC;
            --text-secondary: #a89cc8;
            --text-muted:     #6b5f8a;
            --success:        #34d399;
            --warning:        #fbbf24;
            --danger:         #f87171;
            --info:           #BF40FA;
            --radius-sm:      8px;
            --radius-md:      14px;
            --radius-lg:      20px;
            --shadow:         0 4px 24px rgba(191, 64, 250, 0.12);
            --shadow-hover:   0 8px 32px rgba(191, 64, 250, 0.25);
        }

        /* ============================================================
           VARIABLES DE TEMA — MODO CLARO
           ============================================================ */
        @media (prefers-color-scheme: light) {
            :root {
                --bg-base:        #C0BAB3;
                --bg-surface:     #d6d0c9;
                --bg-card:        #ede8e3;
                --bg-card-hover:  #f5f1ee;
                --border-subtle:  #b0a89e;
                --border-accent:  #391214;
                --accent-primary: #391214;
                --accent-second:  #52423D;
                --accent-third:   #887D77;
                --text-primary:   #160F0C;
                --text-secondary: #52423D;
                --text-muted:     #887D77;
                --success:        #166534;
                --warning:        #92400e;
                --danger:         #991b1b;
                --info:           #391214;
                --shadow:         0 4px 20px rgba(57, 18, 20, 0.15);
                --shadow-hover:   0 8px 32px rgba(57, 18, 20, 0.28);
            }
        }

        /* ============================================================
           RESET Y BASE
           ============================================================ */
        .stApp {
            background-color: var(--bg-base) !important;
        }
        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3, h4 {
            color: var(--text-primary) !important;
            font-weight: 700 !important;
            letter-spacing: -0.3px;
        }
        p, li, span, label {
            color: var(--text-secondary);
        }

        /* ============================================================
           SIDEBAR
           ============================================================ */
        [data-testid="stSidebar"] {
            background: var(--bg-surface) !important;
            border-right: 1px solid var(--border-subtle) !important;
        }
        [data-testid="stSidebar"] * {
            color: var(--text-primary) !important;
        }

        /* ============================================================
           TABS — barra de pestañas
           ============================================================ */
        [data-testid="stTabs"] [role="tablist"] {
            background: var(--bg-surface);
            border-radius: var(--radius-md);
            padding: 4px;
            gap: 4px;
            border: 1px solid var(--border-subtle);
        }
        [data-testid="stTabs"] [role="tab"] {
            background: transparent;
            color: var(--text-muted) !important;
            border-radius: var(--radius-sm);
            font-size: 13px;
            font-weight: 600;
            padding: 8px 16px;
            border: none !important;
            transition: all 0.2s ease;
        }
        [data-testid="stTabs"] [role="tab"]:hover {
            color: var(--text-primary) !important;
            background: var(--border-subtle);
        }
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
            background: var(--accent-primary) !important;
            color: #ffffff !important;
            box-shadow: var(--shadow);
        }

        /* ============================================================
           TARJETAS AUTOMOTRICES
           ============================================================ */
        .auto-card {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 18px 20px;
            margin-bottom: 14px;
            box-shadow: var(--shadow);
            transition: all 0.25s ease;
            position: relative;
            overflow: hidden;
        }
        .auto-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 3px; height: 100%;
            background: linear-gradient(to bottom, var(--accent-primary), var(--accent-second));
            border-radius: 3px 0 0 3px;
        }
        .auto-card:hover {
            border-color: var(--accent-primary);
            transform: translateY(-3px);
            box-shadow: var(--shadow-hover);
        }
        .auto-card h4 {
            margin: 0 0 10px 0;
            font-size: 14px;
            color: var(--text-primary) !important;
        }
        .auto-card div {
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.8;
        }

        /* ============================================================
           SEMÁFORO VEHICULAR
           ============================================================ */
        .semaforo-banner {
            border-radius: var(--radius-md);
            padding: 18px 24px;
            margin-bottom: 24px;
            font-weight: 600;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border: 1px solid transparent;
        }
        .semaforo-verde {
            background: linear-gradient(120deg, #052e16 0%, #064e3b 100%);
            border-color: #065f46;
            box-shadow: 0 0 0 1px #059669, 0 4px 20px rgba(16, 185, 129, 0.2);
            color: #d1fae5;
        }
        .semaforo-amarillo {
            background: linear-gradient(120deg, #451a03 0%, #78350f 100%);
            border-color: #92400e;
            box-shadow: 0 0 0 1px #d97706, 0 4px 20px rgba(245, 158, 11, 0.2);
            color: #fef3c7;
        }
        .semaforo-rojo {
            background: linear-gradient(120deg, #3b0014 0%, #7f1d1d 100%);
            border-color: #991b1b;
            box-shadow: 0 0 0 1px #dc2626, 0 4px 20px rgba(239, 68, 68, 0.3);
            color: #fee2e2;
            animation: pulse-red 2.5s ease-in-out infinite;
        }
        @keyframes pulse-red {
            0%, 100% { box-shadow: 0 0 0 1px #dc2626, 0 4px 20px rgba(239,68,68,0.3); }
            50%       { box-shadow: 0 0 0 1px #dc2626, 0 8px 32px rgba(239,68,68,0.5); }
        }

        /* ============================================================
           BADGES DE ESTADO
           ============================================================ */
        .badge-operativo {
            background: rgba(16, 185, 129, 0.12);
            color: #34d399;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
            border: 1px solid rgba(16, 185, 129, 0.3);
            text-transform: uppercase;
        }
        .badge-degradado {
            background: rgba(245, 158, 11, 0.12);
            color: #fbbf24;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
            border: 1px solid rgba(245, 158, 11, 0.3);
            text-transform: uppercase;
        }
        .badge-falla {
            background: rgba(248, 113, 113, 0.12);
            color: #f87171;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
            border: 1px solid rgba(248, 113, 113, 0.3);
            text-transform: uppercase;
        }
        .badge-desconectado {
            background: rgba(107, 114, 128, 0.12);
            color: #9ca3af;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
            border: 1px solid rgba(107, 114, 128, 0.3);
            text-transform: uppercase;
        }

        /* ============================================================
           FASES / PASOS DE INCIDENTES
           ============================================================ */
        .fase-step {
            border-left: 3px solid var(--accent-primary);
            padding: 12px 16px;
            margin-bottom: 10px;
            background: var(--bg-card);
            border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
            box-shadow: var(--shadow);
        }
        .fase-step:hover {
            border-color: var(--accent-second);
            background: var(--bg-card-hover);
        }

        /* ============================================================
           BLOQUE DE ACCESO DENEGADO
           ============================================================ */
        .access-denied-block {
            background: linear-gradient(135deg, var(--bg-surface) 0%, var(--bg-card) 100%);
            border: 1px dashed var(--border-accent);
            border-radius: var(--radius-lg);
            padding: 48px 32px;
            text-align: center;
            color: var(--text-muted);
        }
        .access-denied-block .denied-icon {
            font-size: 52px;
            display: block;
            margin-bottom: 16px;
            opacity: 0.6;
        }
        .access-denied-block h3 {
            color: var(--text-secondary) !important;
            font-size: 18px;
            margin-bottom: 8px;
        }
        .access-denied-block p {
            font-size: 13px;
            color: var(--text-muted) !important;
            max-width: 360px;
            margin: 0 auto;
        }

        /* ============================================================
           TARJETAS DE INFO DEL ROL (sidebar)
           ============================================================ */
        .rol-card {
            background: var(--bg-card);
            padding: 12px 14px;
            border-radius: var(--radius-sm);
            border-left: 4px solid var(--accent-primary);
            margin-top: 10px;
        }
        .rol-card .rol-label {
            font-size: 11px;
            text-transform: uppercase;
            color: var(--text-muted);
            letter-spacing: 0.8px;
        }
        .rol-card .rol-name {
            font-size: 15px;
            font-weight: 700;
            color: var(--text-primary);
            margin: 4px 0 2px;
        }
        .rol-card .rol-nivel {
            font-size: 11px;
            color: var(--text-secondary);
        }

        /* ============================================================
           BOTONES STREAMLIT
           ============================================================ */
        .stButton > button {
            border-radius: var(--radius-sm) !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            transition: all 0.2s ease !important;
            border: 1px solid var(--border-subtle) !important;
        }
        .stButton > button:hover {
            border-color: var(--accent-primary) !important;
            box-shadow: 0 0 0 2px rgba(191, 64, 250, 0.2) !important;
            transform: translateY(-1px) !important;
        }
        [data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-second) 100%) !important;
            border-color: transparent !important;
            color: white !important;
        }

        /* ============================================================
           MÉTRICAS STREAMLIT
           ============================================================ */
        [data-testid="stMetric"] {
            background: var(--bg-card);
            border-radius: var(--radius-md);
            padding: 16px 18px;
            border: 1px solid var(--border-subtle);
        }
        [data-testid="stMetricLabel"] > div {
            color: var(--text-muted) !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        [data-testid="stMetricValue"] > div {
            color: var(--text-primary) !important;
            font-size: 28px !important;
            font-weight: 700 !important;
        }

        /* ============================================================
           DATAFRAMES / TABLAS
           ============================================================ */
        [data-testid="stDataFrame"] {
            border-radius: var(--radius-md);
            overflow: hidden;
            border: 1px solid var(--border-subtle);
        }

        /* ============================================================
           EXPANDERS
           ============================================================ */
        [data-testid="stExpander"] {
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            background: var(--bg-card) !important;
        }

        /* ============================================================
           INPUTS / SELECTBOX
           ============================================================ */
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div {
            border-radius: var(--radius-sm) !important;
            border-color: var(--border-subtle) !important;
            background: var(--bg-surface) !important;
        }

        /* ============================================================
           DIVIDER
           ============================================================ */
        hr {
            border-color: var(--border-subtle) !important;
            opacity: 0.5;
        }
        </style>
    """, unsafe_allow_html=True)


def render_banner_semaforo(semaforo_data: Dict[str, Any]):
    """Renderiza el semáforo vehicular de estado general en el encabezado"""
    color = semaforo_data["color"]
    css_class = f"semaforo-{color.lower()}"

    st.markdown(f"""
        <div class="semaforo-banner {css_class}">
            <div>
                <span style="font-size: 19px; font-weight: 700; letter-spacing: 0.3px;">{semaforo_data['titulo']}</span>
                <div style="font-size: 13px; opacity: 0.85; margin-top: 5px; font-weight: 400;">{semaforo_data['mensaje']}</div>
            </div>
            <div style="text-align: right; min-width: 170px;">
                <div style="font-size: 12px; text-transform: uppercase; opacity: 0.8; letter-spacing: 0.5px; margin-bottom: 4px;">
                    Batería BMS: <b>{semaforo_data['bateria_soc']}%</b>
                </div>
                <div style="font-size: 12px; text-transform: uppercase; opacity: 0.8; letter-spacing: 0.5px;">
                    Eventos Críticos: <b>{semaforo_data['eventos_criticos_count']}</b>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def crear_gauge_bateria(soc_pct: float, temp_c: float) -> go.Figure:
    """Genera medidor tipo tacómetro para el estado de carga de la batería"""
    color_bar = "#34d399" if soc_pct > 25 else ("#fbbf24" if soc_pct > 12 else "#f87171")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=soc_pct,
        number={'suffix': "%", 'font': {'size': 26, 'color': '#E3D9FC'}},
        title={'text': f"Batería HV · {temp_c}°C", 'font': {'size': 13, 'color': '#a89cc8'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#5B2A62"},
            'bar': {'color': color_bar, 'thickness': 0.28},
            'bgcolor': "#0e0a1a",
            'borderwidth': 1,
            'bordercolor': "#2a1f40",
            'steps': [
                {'range': [0, 12],  'color': 'rgba(248, 113, 113, 0.15)'},
                {'range': [12, 25], 'color': 'rgba(251, 191, 36, 0.15)'},
                {'range': [25, 100],'color': 'rgba(52, 211, 153, 0.1)'}
            ],
            'threshold': {
                'line': {'color': "#f87171", 'width': 3},
                'thickness': 0.75,
                'value': 10
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=15, r=15, t=30, b=15),
        height=170
    )
    return fig


def crear_gauge_circular(valor: float, titulo: str, unidad: str = "%", max_val: float = 100.0, color_hex: str = "#BF40FA") -> go.Figure:
    """Genera medidor circular estilizado para CPU y Memoria"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=valor,
        number={'suffix': unidad, 'font': {'size': 24, 'color': '#E3D9FC'}},
        title={'text': titulo, 'font': {'size': 13, 'color': '#a89cc8'}},
        gauge={
            'axis': {'range': [0, max_val], 'tickcolor': "#5B2A62"},
            'bar': {'color': color_hex, 'thickness': 0.26},
            'bgcolor': "#0e0a1a",
            'borderwidth': 1,
            'bordercolor': "#2a1f40"
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=15, r=15, t=30, b=15),
        height=160
    )
    return fig


def render_tarjeta_dispositivo(dev: Dict[str, Any]):
    """Renderiza tarjeta individual para un periférico o sensor de AutoOS"""
    badge_map = {
        "operativo":    ('<span class="badge-operativo">Operativo</span>',   "#34d399"),
        "degradado":    ('<span class="badge-degradado">Degradado</span>',   "#fbbf24"),
        "falla":        ('<span class="badge-falla">Falla</span>',           "#f87171"),
        "desconectado": ('<span class="badge-desconectado">Desc.</span>',    "#6b7280")
    }
    badge_html, color = badge_map.get(dev["estado"], ('<span class="badge-operativo">Operativo</span>', "#34d399"))

    nivel_color_map = {
        "critico":   "#f87171",
        "esencial":  "#fbbf24",
        "estandar":  "#BF40FA"
    }
    critico_color = nivel_color_map.get(dev["nivel_critico"], "#a89cc8")

    st.markdown(f"""
        <div class="auto-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-weight: 700; color: var(--text-primary); font-size: 15px;">{dev['nombre']}</span>
                {badge_html}
            </div>
            <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px;">
                <code style="background: rgba(191,64,250,0.1); padding: 2px 6px; border-radius: 4px; color: #BF40FA;">{dev['codigo']}</code>
                &nbsp;·&nbsp; Bus: <b style="color: var(--text-secondary);">{dev['puerto_bus']}</b>
                &nbsp;·&nbsp; {dev['sub_sistema']}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px;">
                <span>Salud: <b style="color: {color};">{dev['salud_porcentaje']}%</b></span>
                <span style="color: {critico_color}; text-transform: uppercase; font-weight: 700; font-size: 10px;
                             background: rgba(0,0,0,0.2); padding: 2px 8px; border-radius: 20px;
                             border: 1px solid {critico_color}44;">
                    {dev['nivel_critico']}
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_acceso_denegado(seccion: str, rol_requerido: str = "Mecánico / Admin"):
    """Renderiza un bloque elegante de acceso denegado para secciones restringidas"""
    st.markdown(f"""
        <div class="access-denied-block">
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: var(--border-accent); margin-bottom: 8px; font-weight: 700;">ACCESO RESTRINGIDO</div>
            <h3>Permisos Insuficientes</h3>
            <p>La sección <b>{seccion}</b> requiere privilegios de <b>{rol_requerido}</b>.
            Tu perfil actual no posee autorización para modificar ni ejecutar acciones en este módulo.</p>
        </div>
    """, unsafe_allow_html=True)
