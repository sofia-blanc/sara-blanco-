"""
====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Dashboard Principal de Control e Integración
====================================================================
"""
import sys
import os
from pathlib import Path

# Configurar ruta absoluta al módulo Auto para compatibilidad total con Streamlit Cloud
AUTO_DIR = Path(__file__).resolve().parent
if str(AUTO_DIR) not in sys.path:
    sys.path.insert(0, str(AUTO_DIR))

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

# Estilos CSS para experiencia fluida idéntica al preview sin márgenes nativos de Streamlit
st.markdown("""
<style>
    /* Ocultar barra superior y pie nativo de Streamlit */
    header[data-testid="stHeader"], footer, #MainMenu {
        visibility: hidden !important;
        height: 0px !important;
    }
    .stApp > header {
        display: none !important;
    }
    /* Ocupar el 100% del viewport sin bordes ni padding excesivo */
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

# Cargar el bundle interactivo oficial de AutoOS
bundle_candidates = [
    AUTO_DIR / "modules" / "autoos_interactive.html",
    AUTO_DIR / "autoos_interactive.html",
    Path(__file__).resolve().parent.parent / "modules" / "autoos_interactive.html",
]

bundle_path = next((p for p in bundle_candidates if p.exists()), None)

if bundle_path:
    with open(bundle_path, "r", encoding="utf-8") as f:
        app_html = f.read()
    components.html(app_html, height=1350, scrolling=True)
else:
    st.error("Archivo interactivo de AutoOS no encontrado.")
