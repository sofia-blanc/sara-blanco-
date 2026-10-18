"""====================================================================
AUTOOS - DASHBOARD DE CPU Y PLANIFICADOR DE PROCESOS
Responsable: Integrante 1 (CPU & Scheduling Engine)
====================================================================
Vista unificada de alta fidelidad con estética Cockpit AutoOS:
- Despacho multialgoritmo (FCFS, Round Robin, Prioridad)
- Diagrama de Gantt reactivo con trazabilidad temporal
- Simulador de Batería Baja Limp-Mode
- Simulador de Fallas Críticas ASIL-D
- Control único de Rol y Tema en la barra superior
===================================================================="""

import os
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

def mostrar(supabase=None):
    """Renderiza el planificador y simuladores con la estética exacta de Cockpit AutoOS."""
    CURRENT_DIR = Path(__file__).resolve().parent
    ROOT_DIR = CURRENT_DIR.parent
    
    bundle_candidates = [
        ROOT_DIR / "Auto" / "autoos_unified.html",
        ROOT_DIR / "autoos_unified.html",
        CURRENT_DIR / "autoos_unified.html",
        Path("/app/applet/dist/autoos_unified.html")
    ]
    bundle_path = next((p for p in bundle_candidates if p.exists()), None)
    if bundle_path:
        with open(bundle_path, "r", encoding="utf-8") as f:
            app_html = f.read()
        components.html(app_html, height=1350, scrolling=True)
    else:
        st.error("No se encontró el paquete unificado de AutoOS.")
