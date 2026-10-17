"""
====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Módulo: ui_components.py
Diseño y Componentes Visuales de Alta Fidelidad
====================================================================
Paleta Modo Claro (Soft Dove / Engie Designs):
  Base:           #C0BAB3 (Soft Dove)
  Superficie:     #D5CFC9 (Superficie elevada suave)
  Cards:          #E3DDD7 (Contenedores)
  Texto Primario: #160F0C (Black Raspberry)
  Texto Secundario:#52423D (Spiced Hot Chocolate)
  Texto Muted:    #887D77 (Moon Rock)
  Acento Primario:#391214 (Dark Sienna)
  Bordes:         #B5ADA4

Paleta Modo Oscuro (Purple Night / NYNÄ):
  Base:           #040607 (Black OLED)
  Superficie:     #0D0714 (Superficie profunda)
  Cards:          #180E24 (Velvet Purple oscuro)
  Texto Primario: #E3D9FC (Periwinkle)
  Texto Secundario:#B8A8DC (Lavanda suave)
  Texto Muted:    #7A6A9C (Púrpura cenizo)
  Acento Primario:#BF40FA (Hyper Magenta)
  Acento Secundario:#4928C2 (Ultrasonic Blue)
  Bordes:         #2E1B46
====================================================================
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any


def obtener_paleta(modo: str = "oscuro") -> Dict[str, str]:
    """Retorna el diccionario de colores según el tema activo."""
    if modo == "claro":
        return {
            "bg_base":        "#C0BAB3",
            "bg_surface":     "#D5CFC9",
            "bg_card":        "#E3DDD7",
            "bg_card_hover":  "#ECE6E0",
            "border":         "#B5ADA4",
            "border_accent":  "#391214",
            "accent_primary": "#391214",
            "accent_second":  "#52423D",
            "text_primary":   "#160F0C",
            "text_secondary": "#52423D",
            "text_muted":     "#887D77",
            "success":        "#15803d",
            "warning":        "#b45309",
            "danger":         "#b91c1c",
            "tab_active_bg":  "#391214",
            "tab_active_text":"#FFFFFF",
            "gauge_bg":       "#D5CFC9",
            "gauge_text":     "#160F0C",
            "shadow":         "0 4px 16px rgba(57, 18, 20, 0.08)"
        }
    else:
        return {
            "bg_base":        "#040607",
            "bg_surface":     "#0D0714",
            "bg_card":        "#180E24",
            "bg_card_hover":  "#231435",
            "border":         "#2E1B46",
            "border_accent":  "#BF40FA",
            "accent_primary": "#BF40FA",
            "accent_second":  "#4928C2",
            "text_primary":   "#E3D9FC",
            "text_secondary": "#B8A8DC",
            "text_muted":     "#7A6A9C",
            "success":        "#34d399",
            "warning":        "#fbbf24",
            "danger":         "#f87171",
            "tab_active_bg":  "linear-gradient(135deg, #BF40FA 0%, #4928C2 100%)",
            "tab_active_text":"#FFFFFF",
            "gauge_bg":       "#120A1C",
            "gauge_text":     "#E3D9FC",
            "shadow":         "0 4px 24px rgba(191, 64, 250, 0.15)"
        }


def aplicar_estilos_cockpit(modo: str = "oscuro"):
    """
    Inyecta CSS global altamente pulido con tipografía automotriz,
    solucionando el bug de la barra blanca superior en modo claro y oscuro.
    """
    p = obtener_paleta(modo)

    st.markdown(f"""
        <style>
        /* ============================================================
           RESET GLOBAL Y HEADER DE STREAMLIT (BUGFIX BARRA BLANCA)
           ============================================================ */
        header[data-testid="stHeader"],
        [data-testid="stHeader"] {{
            background: transparent !important;
            background-color: transparent !important;
            color: {p['text_primary']} !important;
        }}
        [data-testid="stToolbar"] {{
            color: {p['text_primary']} !important;
        }}
        .stApp {{
            background-color: {p['bg_base']} !important;
            color: {p['text_primary']} !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }}
        .main .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 1400px;
        }}

        /* ============================================================
           SIDEBAR
           ============================================================ */
        [data-testid="stSidebar"] {{
            background-color: {p['bg_surface']} !important;
            border-right: 1px solid {p['border']} !important;
        }}
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4 {{
            color: {p['text_primary']} !important;
            letter-spacing: -0.2px;
        }}
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label {{
            color: {p['text_secondary']} !important;
        }}

        /* ============================================================
           TIPOGRAFÍA Y ENCABEZADOS
           ============================================================ */
        h1, h2, h3, h4, h5 {{
            color: {p['text_primary']} !important;
            font-weight: 700 !important;
            letter-spacing: -0.4px;
        }}
        p, span, label, li {{
            color: {p['text_secondary']};
        }}
        code {{
            background: rgba(191, 64, 250, 0.12) !important;
            color: {p['accent_primary']} !important;
            padding: 2px 6px !important;
            border-radius: 4px !important;
            font-family: "SF Mono", Consolas, "Liberation Mono", Menlo, Courier, monospace !important;
            font-size: 12px !important;
        }}

        /* ============================================================
           PESTAÑAS (TABS) MODERNAS
           ============================================================ */
        [data-testid="stTabs"] [role="tablist"] {{
            background-color: {p['bg_surface']};
            border-radius: 12px;
            padding: 6px;
            gap: 6px;
            border: 1px solid {p['border']};
            margin-bottom: 22px;
        }}
        [data-testid="stTabs"] [role="tab"] {{
            background: transparent !important;
            color: {p['text_muted']} !important;
            border-radius: 8px !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            padding: 8px 18px !important;
            border: none !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        [data-testid="stTabs"] [role="tab"]:hover {{
            color: {p['text_primary']} !important;
            background: rgba(191, 64, 250, 0.08) !important;
        }}
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
            background: {p['tab_active_bg']} !important;
            color: {p['tab_active_text']} !important;
            box-shadow: {p['shadow']} !important;
        }}

        /* ============================================================
           TARJETAS DEL COCKPIT (CARDS)
           ============================================================ */
        .auto-card {{
            background: {p['bg_card']};
            border: 1px solid {p['border']};
            border-radius: 14px;
            padding: 20px 22px;
            margin-bottom: 16px;
            box-shadow: {p['shadow']};
            transition: transform 0.2s ease, border-color 0.2s ease;
            position: relative;
        }}
        .auto-card:hover {{
            border-color: {p['accent_primary']};
            transform: translateY(-2px);
        }}
        .auto-card h4 {{
            margin: 0 0 12px 0 !important;
            font-size: 15px !important;
            font-weight: 700 !important;
            color: {p['text_primary']} !important;
        }}
        .auto-card div {{
            font-size: 13px;
            color: {p['text_secondary']};
            line-height: 1.85;
        }}

        /* ============================================================
           TARJETA TELEMETRÍA ULTRA-ESTÉTICA (SIN RECORTE DE TEXTO)
           ============================================================ */
        .gauge-card {{
            background: {p['bg_card']};
            border: 1px solid {p['border']};
            border-radius: 16px;
            padding: 18px 16px;
            text-align: center;
            box-shadow: {p['shadow']};
            transition: all 0.25s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            min-height: 210px;
        }}
        .gauge-card:hover {{
            border-color: {p['accent_primary']};
            transform: translateY(-2px);
        }}
        .gauge-header {{
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: {p['text_muted']};
            margin-bottom: 10px;
        }}
        .gauge-ring-container {{
            position: relative;
            width: 110px;
            height: 110px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .gauge-center-text {{
            position: absolute;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        .gauge-center-value {{
            font-size: 24px;
            font-weight: 800;
            color: {p['text_primary']};
            line-height: 1;
            font-feature-settings: "tnum";
        }}
        .gauge-center-unit {{
            font-size: 11px;
            font-weight: 600;
            color: {p['text_muted']};
            margin-top: 2px;
        }}
        .gauge-subtext {{
            font-size: 11px;
            color: {p['text_secondary']};
            margin-top: 8px;
            font-weight: 500;
        }}

        /* ============================================================
           SEMÁFORO VEHICULAR ELEGANTE (BARRA HUD)
           ============================================================ */
        .semaforo-hud {{
            background: {p['bg_card']};
            border: 1px solid {p['border']};
            border-radius: 14px;
            padding: 18px 24px;
            margin-bottom: 22px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: {p['shadow']};
            position: relative;
            overflow: hidden;
        }}
        .semaforo-hud-left {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .semaforo-beacon {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
        }}
        .beacon-verde {{
            background-color: {p['success']};
            box-shadow: 0 0 12px {p['success']};
        }}
        .beacon-amarillo {{
            background-color: {p['warning']};
            box-shadow: 0 0 12px {p['warning']};
        }}
        .beacon-rojo {{
            background-color: {p['danger']};
            box-shadow: 0 0 14px {p['danger']};
            animation: pulse-hud 1.8s infinite;
        }}
        @keyframes pulse-hud {{
            0%, 100% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.3); opacity: 0.7; }}
        }}
        .semaforo-title {{
            font-size: 16px;
            font-weight: 700;
            color: {p['text_primary']};
            letter-spacing: 0.2px;
        }}
        .semaforo-msg {{
            font-size: 12px;
            color: {p['text_secondary']};
            margin-top: 3px;
        }}
        .semaforo-hud-right {{
            display: flex;
            gap: 16px;
            align-items: center;
        }}
        .semaforo-pill {{
            background: rgba(0, 0, 0, 0.15);
            border: 1px solid {p['border']};
            border-radius: 8px;
            padding: 6px 14px;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: {p['text_muted']};
        }}
        .semaforo-pill b {{
            color: {p['text_primary']};
            font-weight: 700;
        }}

        /* ============================================================
           BADGES DE ESTADO (HARDWARE)
           ============================================================ */
        .badge-operativo {{
            background: rgba(34, 197, 94, 0.12);
            color: {p['success']};
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.4px;
            border: 1px solid rgba(34, 197, 94, 0.25);
            text-transform: uppercase;
        }}
        .badge-degradado {{
            background: rgba(245, 158, 11, 0.12);
            color: {p['warning']};
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.4px;
            border: 1px solid rgba(245, 158, 11, 0.25);
            text-transform: uppercase;
        }}
        .badge-falla {{
            background: rgba(239, 68, 68, 0.12);
            color: {p['danger']};
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.4px;
            border: 1px solid rgba(239, 68, 68, 0.25);
            text-transform: uppercase;
        }}
        .badge-desconectado {{
            background: rgba(120, 120, 120, 0.12);
            color: {p['text_muted']};
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.4px;
            border: 1px solid {p['border']};
            text-transform: uppercase;
        }}

        /* ============================================================
           CONTENEDORES DE ROL Y SIDEBAR
           ============================================================ */
        .rol-card {{
            background: {p['bg_card']};
            padding: 14px 16px;
            border-radius: 10px;
            border-left: 4px solid {p['accent_primary']};
            border: 1px solid {p['border']};
            border-left-width: 4px;
            border-left-color: {p['accent_primary']};
            margin-top: 12px;
        }}
        .rol-card .rol-label {{
            font-size: 10px;
            text-transform: uppercase;
            color: {p['text_muted']};
            letter-spacing: 1px;
            font-weight: 700;
        }}
        .rol-card .rol-name {{
            font-size: 15px;
            font-weight: 700;
            color: {p['text_primary']};
            margin: 4px 0 2px;
        }}
        .rol-card .rol-nivel {{
            font-size: 11px;
            color: {p['text_secondary']};
        }}

        /* ============================================================
           FASES DE INCIDENTES
           ============================================================ */
        .fase-step {{
            border-left: 3px solid {p['accent_primary']};
            padding: 12px 18px;
            margin-bottom: 12px;
            background: {p['bg_card']};
            border-radius: 0 10px 10px 0;
            border-top: 1px solid {p['border']};
            border-right: 1px solid {p['border']};
            border-bottom: 1px solid {p['border']};
        }}

        /* ============================================================
           BLOQUE ACCESO RESTRINGIDO
           ============================================================ */
        .access-denied-block {{
            background: {p['bg_card']};
            border: 1px dashed {p['border_accent']};
            border-radius: 14px;
            padding: 36px 28px;
            text-align: center;
            margin-top: 12px;
            margin-bottom: 16px;
        }}
        .access-denied-block h3 {{
            color: {p['text_primary']} !important;
            font-size: 16px;
            margin-bottom: 6px;
        }}
        .access-denied-block p {{
            font-size: 13px;
            color: {p['text_muted']};
            max-width: 420px;
            margin: 0 auto;
        }}

        /* ============================================================
           WIDGET RELOJ DIGITAL DE SISTEMA (HEADER)
           ============================================================ */
        .reloj-hud {{
            background: {p['bg_card']};
            border: 1px solid {p['border']};
            border-radius: 12px;
            padding: 10px 16px;
            text-align: right;
            box-shadow: {p['shadow']};
        }}
        .reloj-label {{
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: {p['text_muted']};
            font-weight: 700;
        }}
        .reloj-time {{
            font-size: 22px;
            font-weight: 800;
            color: {p['text_primary']};
            font-feature-settings: "tnum";
            line-height: 1.2;
        }}
        .reloj-tag {{
            font-size: 10px;
            color: {p['success']};
            font-weight: 600;
        }}

        /* ============================================================
           STREAMLIT FORM CONTROLS & TABLES
           ============================================================ */
        .stButton > button {{
            border-radius: 8px !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            border: 1px solid {p['border']} !important;
            background-color: {p['bg_card']} !important;
            color: {p['text_primary']} !important;
            transition: all 0.2s ease !important;
        }}
        .stButton > button:hover {{
            border-color: {p['accent_primary']} !important;
            box-shadow: 0 0 0 2px rgba(191, 64, 250, 0.2) !important;
            transform: translateY(-1px) !important;
        }}
        [data-testid="baseButton-primary"] {{
            background: {p['tab_active_bg']} !important;
            border-color: transparent !important;
            color: #FFFFFF !important;
        }}
        [data-testid="stDataFrame"] {{
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid {p['border']} !important;
            background: {p['bg_card']} !important;
        }}
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div {{
            border-radius: 8px !important;
            border-color: {p['border']} !important;
            background-color: {p['bg_surface']} !important;
            color: {p['text_primary']} !important;
        }}
        hr {{
            border-color: {p['border']} !important;
            opacity: 0.4;
            margin: 20px 0 !important;
        }}
        </style>
    """, unsafe_allow_html=True)


def render_banner_semaforo(semaforo_data: Dict[str, Any], modo: str = "oscuro"):
    """Renderiza el semáforo vehicular de estado general con diseño HUD moderno."""
    color = semaforo_data.get("color", "VERDE").upper()
    beacon_class = "beacon-verde" if color == "VERDE" else ("beacon-amarillo" if color == "AMARILLO" else "beacon-rojo")

    st.markdown(f"""
        <div class="semaforo-hud">
            <div class="semaforo-hud-left">
                <div class="semaforo-beacon {beacon_class}"></div>
                <div>
                    <div class="semaforo-title">{semaforo_data['titulo']}</div>
                    <div class="semaforo-msg">{semaforo_data['mensaje']}</div>
                </div>
            </div>
            <div class="semaforo-hud-right">
                <div class="semaforo-pill">Batería BMS: <b>{semaforo_data['bateria_soc']}%</b></div>
                <div class="semaforo-pill">Eventos Críticos: <b>{semaforo_data['eventos_criticos_count']}</b></div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_card_telemetria(
    titulo: str,
    valor: float,
    unidad: str = "%",
    subtexto: str = "",
    color_acento: str = "#BF40FA",
    max_val: float = 100.0,
    modo: str = "oscuro"
):
    """
    Renderiza un indicador circular en vector SVG limpio y nítido.
    Resuelve 100% el bug del texto cortado de Plotly.
    """
    p = obtener_paleta(modo)
    # Cálculo para anillo de circunferencia 2 * PI * 42 ≈ 263.9
    radio = 42
    circunferencia = 2 * 3.14159 * radio
    pct_val = max(0.0, min(float(valor) / max_val, 1.0))
    offset = circunferencia * (1.0 - pct_val)

    color_stroke = color_acento if modo == "oscuro" else (
        "#391214" if color_acento in ["#BF40FA", "#4928C2"] else color_acento
    )

    st.markdown(f"""
        <div class="gauge-card">
            <div class="gauge-header">{titulo}</div>
            <div class="gauge-ring-container">
                <svg width="110" height="110" viewBox="0 0 110 110" style="transform: rotate(-90deg);">
                    <circle cx="55" cy="55" r="{radio}"
                            stroke="{p['gauge_bg']}" stroke-width="8" fill="none" />
                    <circle cx="55" cy="55" r="{radio}"
                            stroke="{color_stroke}" stroke-width="8" fill="none"
                            stroke-dasharray="{circunferencia:.1f}"
                            stroke-dashoffset="{offset:.1f}"
                            stroke-linecap="round"
                            style="transition: stroke-dashoffset 0.8s ease;" />
                </svg>
                <div class="gauge-center-text">
                    <span class="gauge-center-value">{valor}</span>
                    <span class="gauge-center-unit">{unidad}</span>
                </div>
            </div>
            <div class="gauge-subtext">{subtexto}</div>
        </div>
    """, unsafe_allow_html=True)


def render_tarjeta_dispositivo(dev: Dict[str, Any], modo: str = "oscuro"):
    """Renderiza tarjeta individual para un periférico o sensor de AutoOS."""
    badge_map = {
        "operativo":    '<span class="badge-operativo">Operativo</span>',
        "degradado":    '<span class="badge-degradado">Degradado</span>',
        "falla":        '<span class="badge-falla">Falla</span>',
        "desconectado": '<span class="badge-desconectado">Desc.</span>'
    }
    badge_html = badge_map.get(dev["estado"], '<span class="badge-operativo">Operativo</span>')

    p = obtener_paleta(modo)
    critico_color = p['danger'] if dev["nivel_critico"] == "critico" else (
        p['warning'] if dev["nivel_critico"] == "esencial" else p['accent_primary']
    )

    st.markdown(f"""
        <div class="auto-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-weight: 700; color: {p['text_primary']}; font-size: 15px;">{dev['nombre']}</span>
                {badge_html}
            </div>
            <div style="font-size: 12px; color: {p['text_muted']}; margin-bottom: 10px;">
                <code>{dev['codigo']}</code> &nbsp;&bull;&nbsp; Bus: <b style="color: {p['text_secondary']};">{dev['puerto_bus']}</b> &nbsp;&bull;&nbsp; {dev['sub_sistema']}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px;">
                <span>Salud: <b style="color: {p['text_primary']};">{dev['salud_porcentaje']}%</b></span>
                <span style="color: {critico_color}; text-transform: uppercase; font-weight: 700; font-size: 10px;
                             background: rgba(0,0,0,0.06); padding: 2px 8px; border-radius: 12px;
                             border: 1px solid {critico_color}44;">
                    Nivel: {dev['nivel_critico']}
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_acceso_denegado(seccion: str, rol_requerido: str = "Mecánico / Admin"):
    """Renderiza un bloque elegante de acceso denegado sin emojis."""
    st.markdown(f"""
        <div class="access-denied-block">
            <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.7; margin-bottom: 6px; font-weight: 700;">ACCESO RESTRINGIDO</div>
            <h3>Permisos Insuficientes</h3>
            <p>La sección <b>{seccion}</b> requiere privilegios de <b>{rol_requerido}</b>. Tu rol actual tiene acceso de solo lectura en este subsistema.</p>
        </div>
    """, unsafe_allow_html=True)
