"""
====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Módulo: ui_components.py
Diseño y Componentes Visuales con Tipografía Playfair Display
====================================================================
Paleta Modo Claro (Soft Dove):
  Base:           #C0BAB3 (Soft Dove)
  Superficie:     #D5CFC9 (Superficie suave)
  Cards:          #E3DDD7 (Contenedores)
  Texto Primario: #160F0C (Black Raspberry - máximo contraste)
  Texto Secundario:#391214 (Dark Sienna)
  Texto Muted:    #52423D (Spiced Hot Chocolate)
  Acento Primario:#391214 (Dark Sienna)
  Bordes:         #A8A096

Paleta Modo Oscuro (Purple Night):
  Base:           #040607 (Black OLED)
  Superficie:     #0D0714 (Superficie profunda)
  Cards:          #180E24 (Velvet Purple)
  Texto Primario: #E3D9FC (Periwinkle - máximo contraste)
  Texto Secundario:#B8A8DC (Lavanda suave)
  Texto Muted:    #7A6A9C (Púrpura cenizo)
  Acento Primario:#BF40FA (Hyper Magenta)
  Acento Secundario:#4928C2 (Ultrasonic Blue)
  Bordes:         #331E4D
====================================================================
"""

import streamlit as st
import streamlit.components.v1 as components
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
            "bg_card_hover":  "#EDE7E1",
            "border":         "#A8A096",
            "border_accent":  "#391214",
            "accent_primary": "#391214",
            "accent_second":  "#52423D",
            "text_primary":   "#160F0C",
            "text_secondary": "#391214",
            "text_muted":     "#52423D",
            "success":        "#15803d",
            "warning":        "#b45309",
            "danger":         "#b91c1c",
            "tab_active_bg":  "#391214",
            "tab_active_text":"#FFFFFF",
            "gauge_bg":       "#D0C9C2",
            "gauge_text":     "#160F0C",
            "shadow":         "0 4px 16px rgba(57, 18, 20, 0.12)"
        }
    else:
        return {
            "bg_base":        "#040607",
            "bg_surface":     "#0D0714",
            "bg_card":        "#180E24",
            "bg_card_hover":  "#241438",
            "border":         "#331E4D",
            "border_accent":  "#BF40FA",
            "accent_primary": "#BF40FA",
            "accent_second":  "#4928C2",
            "text_primary":   "#E3D9FC",
            "text_secondary": "#B8A8DC",
            "text_muted":     "#8D7AA8",
            "success":        "#34d399",
            "warning":        "#fbbf24",
            "danger":         "#f87171",
            "tab_active_bg":  "linear-gradient(135deg, #BF40FA 0%, #4928C2 100%)",
            "tab_active_text":"#FFFFFF",
            "gauge_bg":       "#12091C",
            "gauge_text":     "#E3D9FC",
            "shadow":         "0 4px 24px rgba(191, 64, 250, 0.18)"
        }


def aplicar_estilos_cockpit(modo: str = "auto"):
    """
    Inyecta CSS con fuente Playfair Display para todo el sitio,
    utiliza CSS variables para soportar de forma nativa e inmediata el selector
    de Modo Claro / Modo Oscuro de Streamlit (menú de 3 puntos), y
    proporciona pestañas anchas y elegantes con amplio espacio horizontal.
    """
    # Si el usuario eligió forzar explícitamente un tema en el sidebar
    override_css = ""
    if modo == "claro":
        override_css = """
        :root, .stApp {
            --bg-base: #C0BAB3 !important;
            --bg-surface: #D5CFC9 !important;
            --bg-card: #E3DDD7 !important;
            --bg-card-hover: #EDE7E1 !important;
            --border: #A8A096 !important;
            --border-accent: #391214 !important;
            --accent-primary: #391214 !important;
            --accent-second: #52423D !important;
            --text-primary: #160F0C !important;
            --text-secondary: #391214 !important;
            --text-muted: #52423D !important;
            --success: #15803d !important;
            --warning: #b45309 !important;
            --danger: #b91c1c !important;
            --tab-active-bg: linear-gradient(135deg, #391214 0%, #52423D 100%) !important;
            --tab-active-text: #FFFFFF !important;
            --gauge-bg: #D0C9C2 !important;
            --gauge-text: #160F0C !important;
            --shadow: 0 4px 18px rgba(57, 18, 20, 0.14) !important;
        }
        """
    elif modo == "oscuro":
        override_css = """
        :root, .stApp {
            --bg-base: #040607 !important;
            --bg-surface: #0D0714 !important;
            --bg-card: #180E24 !important;
            --bg-card-hover: #241438 !important;
            --border: #331E4D !important;
            --border-accent: #BF40FA !important;
            --accent-primary: #BF40FA !important;
            --accent-second: #4928C2 !important;
            --text-primary: #E3D9FC !important;
            --text-secondary: #B8A8DC !important;
            --text-muted: #8D7AA8 !important;
            --success: #34d399 !important;
            --warning: #fbbf24 !important;
            --danger: #f87171 !important;
            --tab-active-bg: linear-gradient(135deg, #BF40FA 0%, #4928C2 100%) !important;
            --tab-active-text: #FFFFFF !important;
            --gauge-bg: #12091C !important;
            --gauge-text: #E3D9FC !important;
            --shadow: 0 4px 24px rgba(191, 64, 250, 0.22) !important;
        }
        """

    css_cockpit = f"<style>\n{override_css}\n" + """
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

        /* ============================================================
           SISTEMA DE VARIABLES CSS (SINCRONIZACIÓN NATIVA CON STREAMLIT)
           ============================================================ */
        :root,
        html,
        body,
        .stApp,
        [data-base-theme="dark"],
        .stApp[data-base-theme="dark"],
        [data-theme="dark"],
        .stApp[data-theme="dark"],
        .st-theme-dark {
            --bg-base: #040607;
            --bg-surface: #0D0714;
            --bg-card: #180E24;
            --bg-card-hover: #241438;
            --border: #331E4D;
            --border-accent: #BF40FA;
            --accent-primary: #BF40FA;
            --accent-second: #4928C2;
            --text-primary: #E3D9FC;
            --text-secondary: #B8A8DC;
            --text-muted: #8D7AA8;
            --success: #34d399;
            --warning: #fbbf24;
            --danger: #f87171;
            --tab-active-bg: linear-gradient(135deg, #BF40FA 0%, #4928C2 100%);
            --tab-active-text: #FFFFFF;
            --gauge-bg: #12091C;
            --gauge-text: #E3D9FC;
            --shadow: 0 4px 24px rgba(191, 64, 250, 0.22);
        }

        /* Preferencia nativa de sistema operativo en Modo Claro */
        @media (prefers-color-scheme: light) {
            :root:not([data-theme="dark"]):not([data-base-theme="dark"]),
            html:not([data-theme="dark"]):not([data-base-theme="dark"]),
            body:not([data-theme="dark"]):not([data-base-theme="dark"]),
            .stApp:not([data-theme="dark"]):not([data-base-theme="dark"]) {
                --bg-base: #C0BAB3;
                --bg-surface: #D5CFC9;
                --bg-card: #E3DDD7;
                --bg-card-hover: #EDE7E1;
                --border: #A8A096;
                --border-accent: #391214;
                --accent-primary: #391214;
                --accent-second: #52423D;
                --text-primary: #160F0C;
                --text-secondary: #391214;
                --text-muted: #52423D;
                --success: #15803d;
                --warning: #b45309;
                --danger: #b91c1c;
                --tab-active-bg: linear-gradient(135deg, #391214 0%, #52423D 100%);
                --tab-active-text: #FFFFFF;
                --gauge-bg: #D0C9C2;
                --gauge-text: #160F0C;
                --shadow: 0 4px 18px rgba(57, 18, 20, 0.14);
            }
        }

        /* Cuando el usuario o Streamlit activa el Modo Claro */
        :root[data-theme="light"],
        :root[data-base-theme="light"],
        html[data-theme="light"],
        html[data-base-theme="light"],
        body[data-theme="light"],
        body[data-base-theme="light"],
        .stApp[data-theme="light"],
        .stApp[data-base-theme="light"],
        [data-theme="light"],
        [data-base-theme="light"],
        .st-theme-light {
            --bg-base: #C0BAB3 !important;
            --bg-surface: #D5CFC9 !important;
            --bg-card: #E3DDD7 !important;
            --bg-card-hover: #EDE7E1 !important;
            --border: #A8A096 !important;
            --border-accent: #391214 !important;
            --accent-primary: #391214 !important;
            --accent-second: #52423D !important;
            --text-primary: #160F0C !important;
            --text-secondary: #391214 !important;
            --text-muted: #52423D !important;
            --success: #15803d !important;
            --warning: #b45309 !important;
            --danger: #b91c1c !important;
            --tab-active-bg: linear-gradient(135deg, #391214 0%, #52423D 100%) !important;
            --tab-active-text: #FFFFFF !important;
            --gauge-bg: #D0C9C2 !important;
            --gauge-text: #160F0C !important;
            --shadow: 0 4px 18px rgba(57, 18, 20, 0.14) !important;
        }

        /* ============================================================
           TIPOGRAFÍA PLAYFAIR DISPLAY PARA CONTENIDO TEXTUAL
           ============================================================ */
        html, body, .stApp, 
        h1, h2, h3, h4, h5, h6, 
        p, label, button, input, select, textarea,
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"],
        .auto-card, .gauge-card, .semaforo-hud, .rol-card,
        [data-testid="stTabs"] [role="tab"],
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] span:not([data-testid="stIconMaterial"]):not([class*="material"]),
        [data-testid="stMarkdownContainer"] div:not([data-testid="stIconMaterial"]):not([class*="material"]) {
            font-family: 'Playfair Display', Georgia, serif !important;
        }

        /* ============================================================
           PROTECCIÓN ESTRICTA DE ICONOS DE STREAMLIT (MATERIAL SYMBOLS)
           Evita que los ligatures de iconos se rompan en texto plano
           ============================================================ */
        [data-testid="stIconMaterial"],
        [data-testid="stIconMaterial"] *,
        [class*="material-symbols"],
        [class*="material-icons"],
        .material-symbols-rounded,
        .material-symbols-outlined,
        .material-icons,
        header [data-testid="stIconMaterial"],
        [data-testid="stMainMenu"] [data-testid="stIconMaterial"],
        div[role="dialog"] [data-testid="stIconMaterial"],
        div[data-baseweb="popover"] [data-testid="stIconMaterial"],
        div[data-baseweb="menu"] [data-testid="stIconMaterial"],
        button [data-testid="stIconMaterial"],
        svg {
            font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
            font-weight: normal !important;
            font-style: normal !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            display: inline-block !important;
            white-space: nowrap !important;
            word-wrap: normal !important;
            direction: ltr !important;
            -webkit-font-feature-settings: 'liga' 1 !important;
            font-feature-settings: 'liga' 1 !important;
            -webkit-font-smoothing: antialiased !important;
        }

        /* ============================================================
           HEADER TRANSPARENTE DE STREAMLIT (BUGFIX BARRA BLANCA)
           ============================================================ */
        header[data-testid="stHeader"],
        [data-testid="stHeader"] {
            background: transparent !important;
            background-color: transparent !important;
            color: var(--text-primary) !important;
        }
        [data-testid="stToolbar"] {
            color: var(--text-primary) !important;
        }
        .stApp {
            background-color: var(--bg-base) !important;
            color: var(--text-primary) !important;
            transition: background-color 0.3s ease, color 0.3s ease;
        }
        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 1400px;
        }

        /* ============================================================
           SIDEBAR
           ============================================================ */
        [data-testid="stSidebar"] {
            background-color: var(--bg-surface) !important;
            border-right: 1px solid var(--border) !important;
        }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4 {
            color: var(--text-primary) !important;
        }
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label {
            color: var(--text-secondary) !important;
        }

        /* ============================================================
           ENCABEZADOS Y TEXTOS
           ============================================================ */
        h1, h2, h3, h4, h5 {
            color: var(--text-primary) !important;
            font-weight: 700 !important;
            letter-spacing: -0.3px;
        }
        p, span, label, li {
            color: var(--text-secondary);
        }
        code {
            background: rgba(191, 64, 250, 0.12) !important;
            color: var(--accent-primary) !important;
            padding: 2px 6px !important;
            border-radius: 4px !important;
            font-size: 13px !important;
        }

        /* ============================================================
           PESTAÑAS (TABS) — TAMAÑO HORIZONTAL AMPLIO Y ELEGANTE
           ============================================================ */
        [data-testid="stTabs"] [role="tablist"] {
            background-color: var(--bg-surface) !important;
            border-radius: 16px !important;
            padding: 8px 12px !important;
            gap: 12px !important;
            border: 1px solid var(--border) !important;
            margin-bottom: 24px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            overflow-x: auto !important;
        }
        /* Pestañas NO seleccionadas */
        [data-testid="stTabs"] [role="tab"]:not([aria-selected="true"]) {
            background: transparent !important;
            color: var(--text-primary) !important;
            font-size: 14.5px !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            padding: 10px 28px !important;
            min-width: 120px !important;
            border: none !important;
            opacity: 0.8 !important;
            transition: all 0.25s ease !important;
            text-align: center !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        [data-testid="stTabs"] [role="tab"]:not([aria-selected="true"]) p,
        [data-testid="stTabs"] [role="tab"]:not([aria-selected="true"]) span {
            color: var(--text-primary) !important;
            font-weight: 600 !important;
            font-size: 14.5px !important;
        }
        [data-testid="stTabs"] [role="tab"]:not([aria-selected="true"]):hover {
            opacity: 1 !important;
            background: rgba(191, 64, 250, 0.12) !important;
            transform: translateY(-1px);
        }
        /* Pestaña SELECCIONADA — TAMAÑO HORIZONTAL AMPLIO CON RESPIRACIÓN Y BRILLO */
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
            background: var(--tab-active-bg) !important;
            color: #FFFFFF !important;
            font-weight: 800 !important;
            border-radius: 12px !important;
            padding: 11px 38px !important;
            min-width: 145px !important;
            box-shadow: var(--shadow), 0 0 16px rgba(191, 64, 250, 0.35) !important;
            opacity: 1 !important;
            border: none !important;
            text-align: center !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            letter-spacing: 0.4px !important;
        }
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] p,
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] span,
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] div {
            color: #FFFFFF !important;
            font-weight: 800 !important;
            font-size: 15px !important;
            letter-spacing: 0.4px !important;
        }

        /* ============================================================
           TARJETAS DEL COCKPIT (CARDS)
           ============================================================ */
        .auto-card {
            background: var(--bg-card) !important;
            border: 1px solid var(--border) !important;
            border-radius: 14px;
            padding: 20px 22px;
            margin-bottom: 16px;
            box-shadow: var(--shadow);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .auto-card:hover {
            border-color: var(--accent-primary) !important;
            transform: translateY(-2px);
        }
        .auto-card h4 {
            margin: 0 0 12px 0 !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            color: var(--text-primary) !important;
        }
        .auto-card div {
            font-size: 13.5px;
            color: var(--text-secondary);
            line-height: 1.85;
        }

        /* ============================================================
           TARJETA TELEMETRÍA ULTRA-ESTÉTICA (SIN RECORTE DE TEXTO)
           ============================================================ */
        .gauge-card {
            background: var(--bg-card) !important;
            border: 1px solid var(--border) !important;
            border-radius: 16px;
            padding: 18px 16px;
            text-align: center;
            box-shadow: var(--shadow);
            transition: all 0.25s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            min-height: 210px;
        }
        .gauge-card:hover {
            border-color: var(--accent-primary) !important;
            transform: translateY(-2px);
        }
        .gauge-header {
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--text-primary) !important;
            margin-bottom: 10px;
        }
        .gauge-ring-container {
            position: relative;
            width: 110px;
            height: 110px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .gauge-center-text {
            position: absolute;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .gauge-center-value {
            font-size: 25px;
            font-weight: 800;
            color: var(--text-primary) !important;
            line-height: 1;
        }
        .gauge-center-unit {
            font-size: 11px;
            font-weight: 600;
            color: var(--text-muted) !important;
            margin-top: 2px;
        }
        .gauge-subtext {
            font-size: 12px;
            color: var(--text-secondary) !important;
            margin-top: 8px;
            font-weight: 600;
        }
        .gauge-bg-ring {
            stroke: var(--gauge-bg) !important;
        }

        /* ============================================================
           SEMÁFORO VEHICULAR ELEGANTE (BARRA HUD)
           ============================================================ */
        .semaforo-hud {
            background: var(--bg-card) !important;
            border: 1px solid var(--border) !important;
            border-radius: 14px;
            padding: 18px 24px;
            margin-bottom: 22px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: var(--shadow) !important;
        }
        .semaforo-hud-left {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .semaforo-beacon {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            display: inline-block;
        }
        .beacon-verde {
            background-color: var(--success);
            box-shadow: 0 0 12px var(--success);
        }
        .beacon-amarillo {
            background-color: var(--warning);
            box-shadow: 0 0 12px var(--warning);
        }
        .beacon-rojo {
            background-color: var(--danger);
            box-shadow: 0 0 14px var(--danger);
            animation: pulse-hud 1.8s infinite;
        }
        @keyframes pulse-hud {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.3); opacity: 0.7; }
        }
        .semaforo-title {
            font-size: 17px;
            font-weight: 800;
            color: var(--text-primary) !important;
            letter-spacing: 0.2px;
        }
        .semaforo-msg {
            font-size: 13px;
            color: var(--text-secondary) !important;
            margin-top: 3px;
        }
        .semaforo-hud-right {
            display: flex;
            gap: 14px;
            align-items: center;
        }
        .semaforo-pill {
            background: rgba(0, 0, 0, 0.08) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px;
            padding: 7px 14px;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: var(--text-muted) !important;
        }
        .semaforo-pill b {
            color: var(--text-primary) !important;
            font-weight: 800;
        }

        /* ============================================================
           BADGES DE HARDWARE
           ============================================================ */
        .badge-operativo {
            background: rgba(34, 197, 94, 0.15);
            color: var(--success);
            padding: 4px 11px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            border: 1px solid rgba(34, 197, 94, 0.3);
            text-transform: uppercase;
        }
        .badge-degradado {
            background: rgba(245, 158, 11, 0.15);
            color: var(--warning);
            padding: 4px 11px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            border: 1px solid rgba(245, 158, 11, 0.3);
            text-transform: uppercase;
        }
        .badge-falla {
            background: rgba(239, 68, 68, 0.15);
            color: var(--danger);
            padding: 4px 11px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            border: 1px solid rgba(239, 68, 68, 0.3);
            text-transform: uppercase;
        }
        .badge-desconectado {
            background: rgba(120, 120, 120, 0.15);
            color: var(--text-muted);
            padding: 4px 11px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            border: 1px solid var(--border);
            text-transform: uppercase;
        }

        /* ============================================================
           ROL SIDEBAR CARD
           ============================================================ */
        .rol-card {
            background: var(--bg-card) !important;
            padding: 14px 16px;
            border-radius: 12px;
            border: 1px solid var(--border) !important;
            border-left: 4px solid var(--accent-primary) !important;
            margin-top: 12px;
        }
        .rol-card .rol-label {
            font-size: 10px;
            text-transform: uppercase;
            color: var(--text-muted) !important;
            letter-spacing: 1px;
            font-weight: 700;
        }
        .rol-card .rol-name {
            font-size: 15px;
            font-weight: 700;
            color: var(--text-primary) !important;
            margin: 4px 0 2px;
        }
        .rol-card .rol-nivel {
            font-size: 11.5px;
            color: var(--text-secondary) !important;
        }

        /* ============================================================
           FASES DE INCIDENTES
           ============================================================ */
        .fase-step {
            border-left: 4px solid var(--accent-primary) !important;
            padding: 14px 20px;
            margin-bottom: 12px;
            background: var(--bg-card) !important;
            border-radius: 0 10px 10px 0;
            border-top: 1px solid var(--border) !important;
            border-right: 1px solid var(--border) !important;
            border-bottom: 1px solid var(--border) !important;
        }

        /* ============================================================
           BLOQUE ACCESO RESTRINGIDO
           ============================================================ */
        .access-denied-block {
            background: var(--bg-card) !important;
            border: 1px dashed var(--border-accent) !important;
            border-radius: 14px;
            padding: 36px 28px;
            text-align: center;
            margin-top: 12px;
            margin-bottom: 16px;
        }
        .access-denied-block h3 {
            color: var(--text-primary) !important;
            font-size: 17px;
            margin-bottom: 6px;
        }
        .access-denied-block p {
            font-size: 13.5px;
            color: var(--text-secondary) !important;
            max-width: 420px;
            margin: 0 auto;
        }

        /* ============================================================
           STREAMLIT FORM CONTROLS & TABLES
           ============================================================ */
        .stButton > button {
            border-radius: 8px !important;
            font-weight: 700 !important;
            font-size: 13.5px !important;
            border: 1px solid var(--border) !important;
            background-color: var(--bg-card) !important;
            color: var(--text-primary) !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button:hover {
            border-color: var(--accent-primary) !important;
            box-shadow: 0 0 0 2px rgba(191, 64, 250, 0.2) !important;
            transform: translateY(-1px) !important;
        }
        [data-testid="baseButton-primary"] {
            background: var(--tab-active-bg) !important;
            border-color: transparent !important;
            color: #FFFFFF !important;
        }
        [data-testid="stDataFrame"] {
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid var(--border) !important;
            background: var(--bg-card) !important;
        }
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div {
            border-radius: 8px !important;
            border-color: var(--border) !important;
            background-color: var(--bg-surface) !important;
            color: var(--text-primary) !important;
        }
        hr {
            border-color: var(--border) !important;
            opacity: 0.5;
            margin: 20px 0 !important;
        }

        /* ============================================================
           PLOTLY TEXT STYLING NATIVO
           ============================================================ */
        .stPlotlyChart .js-plotly-plot text,
        .stPlotlyChart .xtick text,
        .stPlotlyChart .ytick text,
        .stPlotlyChart .legendtext,
        .stPlotlyChart .g-title text,
        .stPlotlyChart .pielabel text {
            font-family: 'Playfair Display', Georgia, serif !important;
            fill: var(--text-primary) !important;
            color: var(--text-primary) !important;
        }
        .stPlotlyChart .gridpath {
            stroke: var(--border) !important;
            stroke-opacity: 0.25 !important;
        }
        </style>
    """
    st.markdown(css_cockpit, unsafe_allow_html=True)
    inyectar_sincronizador_tema()


def inyectar_sincronizador_tema():
    """
    Inyecta un micro-script invisible que monitorea en tiempo real
    el selector nativo de tema de Streamlit (menú de 3 puntos -> Settings -> Light/Dark),
    sincronizando los atributos data-theme en el documento padre para activar
    instantáneamente la paleta Soft Dove (Modo Claro) o Purple Night (Modo Oscuro).
    """
    script_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { margin: 0; padding: 0; display: none; }
        </style>
    </head>
    <body>
    <script>
    (function() {
        function detectStreamlitTheme() {
            try {
                const pWin = window.parent;
                const pDoc = window.parent.document;
                if (!pWin || !pDoc) return "dark";

                // 1. Revisar localStorage de Streamlit
                const keys = ['streamlit:theme', 'stActiveTheme', 'theme'];
                for (let k of keys) {
                    const raw = pWin.localStorage.getItem(k);
                    if (raw) {
                        try {
                            const parsed = JSON.parse(raw);
                            const base = (parsed.base || parsed.name || parsed.theme || '').toLowerCase();
                            if (base === 'light') return 'light';
                            if (base === 'dark') return 'dark';
                        } catch(e) {
                            const str = String(raw).toLowerCase();
                            if (str.includes('light')) return 'light';
                            if (str.includes('dark')) return 'dark';
                        }
                    }
                }

                // 2. Revisar color de toolbar nativo de Streamlit
                const toolbar = pDoc.querySelector('[data-testid="stToolbar"]') || pDoc.querySelector('header');
                if (toolbar) {
                    const color = pWin.getComputedStyle(toolbar).color;
                    const match = color ? color.match(/\\d+/g) : null;
                    if (match && match.length >= 3) {
                        const r = parseInt(match[0]), g = parseInt(match[1]), b = parseInt(match[2]);
                        const brightness = (r * 299 + g * 587 + b * 114) / 1000;
                        if (brightness < 120) return 'light';
                        if (brightness > 180) return 'dark';
                    }
                }

                // 3. Preferencia del sistema operativo
                if (pWin.matchMedia && pWin.matchMedia('(prefers-color-scheme: light)').matches) {
                    return 'light';
                }
                return 'dark';
            } catch(e) {
                return 'dark';
            }
        }

        function sincronizar() {
            try {
                const tema = detectStreamlitTheme();
                const pDoc = window.parent.document;
                if (!pDoc) return;

                const root = pDoc.documentElement;
                const body = pDoc.body;
                const stApp = pDoc.querySelector('.stApp');

                if (root && root.getAttribute('data-theme') !== tema) {
                    root.setAttribute('data-theme', tema);
                    root.setAttribute('data-base-theme', tema);
                }
                if (body && body.getAttribute('data-theme') !== tema) {
                    body.setAttribute('data-theme', tema);
                    body.setAttribute('data-base-theme', tema);
                }
                if (stApp && stApp.getAttribute('data-theme') !== tema) {
                    stApp.setAttribute('data-theme', tema);
                    stApp.setAttribute('data-base-theme', tema);
                    if (tema === 'light') {
                        stApp.classList.add('st-theme-light');
                        stApp.classList.remove('st-theme-dark');
                    } else {
                        stApp.classList.add('st-theme-dark');
                        stApp.classList.remove('st-theme-light');
                    }
                }
            } catch(err) {}
        }

        // Ocultar este micro-frame completamente
        try {
            if (window.frameElement) {
                window.frameElement.style.display = 'none';
                window.frameElement.style.height = '0px';
                window.frameElement.style.width = '0px';
                window.frameElement.style.border = 'none';
                if (window.frameElement.parentElement) {
                    window.frameElement.parentElement.style.display = 'none';
                    window.frameElement.parentElement.style.height = '0px';
                }
            }
        } catch(e) {}

        sincronizar();
        if (window.parent) {
            window.parent.addEventListener('storage', sincronizar);
        }
        setInterval(sincronizar, 250);
    })();
    </script>
    </body>
    </html>
    """
    components.html(script_html, height=0)


def render_reloj_en_vivo(modo: str = "oscuro"):
    """
    Renderiza un reloj digital en tiempo real con segundero continuo,
    utilizando JavaScript en un micro-componente sin lag para Streamlit,
    adaptándose de inmediato al tema claro u oscuro del sistema.
    """
    p = obtener_paleta(modo)
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Playfair Display', Georgia, serif;
                transition: all 0.25s ease;
            }}
            body {{
                background: transparent;
                display: flex;
                justify-content: flex-end;
                align-items: center;
                height: 100%;
                overflow: hidden;
            }}
            .reloj-hud {{
                background: #180E24;
                border: 1px solid #331E4D;
                border-radius: 12px;
                padding: 8px 18px;
                text-align: right;
                box-shadow: 0 4px 24px rgba(191, 64, 250, 0.18);
                display: inline-block;
                min-width: 175px;
            }}
            .reloj-label {{
                font-size: 10.5px;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                color: #8D7AA8;
                font-weight: 700;
            }}
            .reloj-time {{
                font-size: 22px;
                font-weight: 800;
                color: #E3D9FC;
                line-height: 1.15;
                font-feature-settings: "tnum";
            }}
            .reloj-tag {{
                font-size: 10px;
                color: #34d399;
                font-weight: 700;
            }}
            /* MODO CLARO AUTOMÁTICO */
            body.theme-light .reloj-hud {{
                background: #E3DDD7 !important;
                border: 1px solid #A8A096 !important;
                box-shadow: 0 4px 16px rgba(57, 18, 20, 0.12) !important;
            }}
            body.theme-light .reloj-label {{
                color: #52423D !important;
            }}
            body.theme-light .reloj-time {{
                color: #160F0C !important;
            }}
            body.theme-light .reloj-tag {{
                color: #15803d !important;
            }}
        </style>
    </head>
    <body>
        <div class="reloj-hud" id="reloj-hud-box">
            <div class="reloj-label">Reloj de Sistema</div>
            <div class="reloj-time" id="reloj-live">--:--:--</div>
            <div class="reloj-tag">&bull; RTOS Synced</div>
        </div>
        <script>
            function updateClock() {{
                const d = new Date();
                const h = String(d.getHours()).padStart(2, '0');
                const m = String(d.getMinutes()).padStart(2, '0');
                const s = String(d.getSeconds()).padStart(2, '0');
                const el = document.getElementById('reloj-live');
                if (el) el.innerText = h + ':' + m + ':' + s;
            }}
            function syncTheme() {{
                try {{
                    const parentDoc = window.parent.document;
                    if (!parentDoc) return;
                    const root = parentDoc.documentElement;
                    const stApp = parentDoc.querySelector('.stApp');
                    const theme = (root ? root.getAttribute('data-theme') : null) || 
                                  (stApp ? stApp.getAttribute('data-theme') : null) ||
                                  (stApp ? stApp.getAttribute('data-base-theme') : null);
                    
                    let isLight = theme === 'light';
                    if (!theme && window.parent.localStorage) {{
                        const raw = window.parent.localStorage.getItem('streamlit:theme');
                        if (raw && raw.toLowerCase().includes('light')) isLight = true;
                    }}

                    if (isLight) {{
                        document.body.classList.add('theme-light');
                    }} else {{
                        document.body.classList.remove('theme-light');
                    }}
                }} catch(e) {{}}
            }}
            updateClock();
            syncTheme();
            setInterval(updateClock, 1000);
            setInterval(syncTheme, 300);
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=75)


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
                <span style="font-weight: 700; color: {p['text_primary']}; font-size: 15.5px;">{dev['nombre']}</span>
                {badge_html}
            </div>
            <div style="font-size: 12.5px; color: {p['text_muted']}; margin-bottom: 10px;">
                <code>{dev['codigo']}</code> &nbsp;&bull;&nbsp; Bus: <b style="color: {p['text_secondary']};">{dev['puerto_bus']}</b> &nbsp;&bull;&nbsp; {dev['sub_sistema']}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12.5px;">
                <span>Salud: <b style="color: {p['text_primary']};">{dev['salud_porcentaje']}%</b></span>
                <span style="color: {critico_color}; text-transform: uppercase; font-weight: 700; font-size: 10.5px;
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
            <div style="font-size: 10.5px; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.8; margin-bottom: 6px; font-weight: 700;">ACCESO RESTRINGIDO</div>
            <h3>Permisos Insuficientes</h3>
            <p>La sección <b>{seccion}</b> requiere privilegios de <b>{rol_requerido}</b>. Tu rol actual tiene acceso de solo lectura en este subsistema.</p>
        </div>
    """, unsafe_allow_html=True)
