"""
====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Dashboard Principal de Control e Integración
====================================================================
Interfaz unificada con acceso directo y visible a:
1. Planificador de CPU y Simuladores (FCFS, Round Robin, Prioridad, Batería Baja, Proceso Crítico)
2. Cockpit Vehicular Completo (Velocímetro, Multimedia, Chat, Cámaras)
====================================================================
"""

import sys
import os
from pathlib import Path

# Configurar ruta absoluta
AUTO_DIR = Path(__file__).resolve().parent
ROOT_DIR = AUTO_DIR.parent
for d in [str(AUTO_DIR), str(ROOT_DIR)]:
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    os.chdir(str(AUTO_DIR))
except Exception:
    pass

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="AutoOS - Sistema Operativo Vehicular",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos globales elegantes
st.markdown("""
<style>
    /* Estilos de pestañas y botones superiores */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0D0714;
        padding: 8px 12px;
        border-radius: 16px;
        border: 1px solid #331E4D;
        margin-bottom: 16px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 8px 20px;
        color: #8D7AA8;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4928C2 0%, #BF40FA 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 16px rgba(191, 64, 250, 0.35);
    }
    iframe {
        border: none !important;
        width: 100% !important;
        min-height: 1200px !important;
    }
</style>
""", unsafe_allow_html=True)

# Pestañas principales visibles directamente en la pantalla (sin menús ocultos)
tab_sched, tab_cockpit = st.tabs([
    "🏎️ Planificador & Simuladores de CPU",
    "🚗 Cockpit Vehicular Completo"
])

with tab_sched:
    from dashboard.cpu import mostrar as mostrar_cpu
    mostrar_cpu()

with tab_cockpit:
    bundle_candidates = [
        AUTO_DIR / "modules" / "autoos_interactive.html",
        AUTO_DIR / "autoos_interactive.html",
        ROOT_DIR / "modules" / "autoos_interactive.html",
    ]
    bundle_path = next((p for p in bundle_candidates if p.exists()), None)
    if bundle_path:
        with open(bundle_path, "r", encoding="utf-8") as f:
            app_html = f.read()
        components.html(app_html, height=1350, scrolling=True)
    else:
        st.error("Archivo interactivo de AutoOS no encontrado.")
