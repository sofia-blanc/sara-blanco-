"""
====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Dashboard Principal de Control e Integración
====================================================================
Permite alternar de manera fluida entre:
1. El Cockpit Automotriz Interactivo Completo (Velocímetro, Multimedia, Chat, Cámaras)
2. El Módulo de Planificación de CPU y Procesos (FCFS, Round Robin, Prioridad y Simuladores)
====================================================================
"""

import sys
import os
from pathlib import Path

# Configurar ruta absoluta al módulo Auto y raíz
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
    initial_sidebar_state="collapsed"
)

# Selector de Vista en barra lateral o superior
with st.sidebar:
    st.markdown("### 🚘 AutoOS Navigation")
    vista = st.radio(
        "Seleccionar Módulo:",
        [
            "🚗 Cockpit Vehicular Completo",
            "🖥️ Planificador de Procesos (CPU & Simuladores)"
        ],
        index=0
    )
    st.divider()
    st.markdown("**Integración Sistemas Operativos**")
    st.caption("FCFS • Round Robin • Prioridad • Batería Baja • Proceso Crítico")

if vista == "🚗 Cockpit Vehicular Completo":
    # Estilos CSS para experiencia fluida idéntica al preview sin márgenes nativos
    st.markdown("""
    <style>
        header[data-testid="stHeader"], footer, #MainMenu {
            visibility: hidden !important;
            height: 0px !important;
        }
        .stApp > header {
            display: none !important;
        }
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
        }
        div[data-testid="stVerticalBlock"] {
            padding: 0 !important;
            gap: 0 !important;
        }
        iframe {
            border: none !important;
            width: 100% !important;
            min-height: 100vh !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Cargar el bundle interactivo oficial completo de AutoOS
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

else:
    # Renderizar el Módulo de Planificación de CPU en Python puro
    from dashboard.cpu import mostrar as mostrar_cpu
    mostrar_cpu()
