"""====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Dashboard Principal de Control e Integración
====================================================================
Interfaz unificada de alta fidelidad con experiencia visual idéntica:
- Planificador de CPU multialgoritmo (FCFS, Round Robin, Prioridad) con Gantt reactivo
- Simuladores de Contingencia (Batería Baja Limp-Mode y Proceso Crítico ASIL-D)
- Cockpit Vehicular Completo (Velocímetro, HUD, Multimedia, Chat, Cámaras)
- Control ÚNICO y centralizado de Usuario/Rol (RBAC) y Tema (Claro/Oscuro) en la barra superior
===================================================================="""

import sys
import os
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

# Configuración de página de Streamlit
st.set_page_config(
    page_title="AutoOS — Cockpit Vehicular & RTOS",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS para ocultar barras redundantes de Streamlit y dar experiencia 100% nativa
st.markdown("""
<style>
    /* Ocultar elementos predeterminados de Streamlit */
    #MainMenu { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    
    /* Contenedor principal sin márgenes para experiencia idéntica a la preview */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    
    /* Iframe de pantalla completa fluido */
    iframe {
        width: 100% !important;
        border: none !important;
        min-height: 100vh !important;
        height: 100vh !important;
    }
</style>
""", unsafe_allow_html=True)

# Buscar el bundle unificado de AutoOS
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent

bundle_candidates = [
    CURRENT_DIR / "autoos_unified.html",
    ROOT_DIR / "autoos_unified.html",
    ROOT_DIR / "web" / "dist" / "autoos_unified.html",
    CURRENT_DIR / "web" / "dist" / "autoos_unified.html",
    Path("/app/applet/dist/autoos_unified.html")
]

bundle_path = next((p for p in bundle_candidates if p.exists()), None)

if bundle_path:
    with open(bundle_path, "r", encoding="utf-8") as f:
        app_html = f.read()
    components.html(app_html, height=1350, scrolling=True)
else:
    st.error("No se encontró el paquete unificado de AutoOS.")
