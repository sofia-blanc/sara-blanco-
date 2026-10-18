"""====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Dashboard Principal de Control e Integración
====================================================================
Interfaz unificada con control global de Tema (Claro / Oscuro) y Usuario/Rol (RBAC)
y estética idéntica de Cockpit AutoOS en toda la aplicación:
1. Pestaña 1: Planificador & Simuladores (FCFS, Round Robin, Prioridad, Batería Limp-Mode, Falla ASIL-D)
2. Pestaña 2: Cockpit Vehicular Completo (Velocímetro, HUD, Multimedia, Chat, Cámaras)
===================================================================="""

import sys
import os
from pathlib import Path

# Configurar rutas absolutas al módulo Auto y raíz para compatibilidad total
AUTO_DIR = Path(__file__).resolve().parent
ROOT_DIR = AUTO_DIR.parent
for d in [str(AUTO_DIR), str(ROOT_DIR), str(ROOT_DIR / "Auto")]:
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    os.chdir(str(AUTO_DIR))
except Exception:
    pass

import streamlit as st
import streamlit.components.v1 as components

# Configuración de página de Streamlit
st.set_page_config(
    page_title="AutoOS — Cockpit Vehicular & RTOS",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar estados de sesión globales si no existen
if "autoos_theme" not in st.session_state:
    st.session_state.autoos_theme = "dark"
if "autoos_user_role" not in st.session_state:
    st.session_state.autoos_user_role = "admin"
if "autoos_user_name" not in st.session_state:
    st.session_state.autoos_user_name = "Carlos Vélez"

# ====================================================================
# BARRA LATERAL: CONTROLADOR ÚNICO DE TEMA Y USUARIO / ROL RBAC
# ====================================================================
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
        <span style="font-size: 1.8rem;">🚗</span>
        <div>
            <h2 style="margin: 0; font-family: 'Playfair Display', Georgia, serif; font-size: 1.3rem; font-weight: 800;">
                AutoOS
            </h2>
            <span style="font-size: 0.72rem; color: #34d399; font-family: monospace; font-weight: bold;">
                ● SISTEMA OPERATIVO ACTIVO
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 1. CONTROLADOR GLOBAL DE MODO (CLARO / OSCURO)
    st.markdown("#### 🌗 Controlador Global de Tema")
    tema_seleccionado = st.radio(
        "Modo de Visualización:",
        options=["Modo Oscuro (Purple Night)", "Modo Claro (Soft Dove)"],
        index=0 if st.session_state.autoos_theme == "dark" else 1,
        label_visibility="collapsed"
    )
    nuevo_tema = "dark" if "Oscuro" in tema_seleccionado else "light"
    if nuevo_tema != st.session_state.autoos_theme:
        st.session_state.autoos_theme = nuevo_tema
        st.rerun()

    st.markdown("---")

    # 2. CONTROLADOR GLOBAL DE USUARIO Y ROL RBAC
    st.markdown("#### 🛡️ Usuario y Rol Activo")
    usuario_opcion = st.selectbox(
        "Seleccionar Identidad:",
        options=[
            "🔧 Carlos Vélez (Mecánico / Admin)",
            "🚗 Laura Gómez (Conductora Principal)",
            "👤 Andrés Rivera (Pasajero de Cabina)"
        ],
        index=0 if st.session_state.autoos_user_role == "admin" else (1 if st.session_state.autoos_user_role == "user" else 2),
        label_visibility="collapsed"
    )
    if "Mecánico" in usuario_opcion:
        rol_cod = "admin"
        rol_nombre = "Mecánico Certificado & Admin"
        rol_desc = "Control total del Kernel, simuladores y diagnóstico ASIL-D."
    elif "Conductora" in usuario_opcion:
        rol_cod = "user"
        rol_nombre = "Conductora Principal"
        rol_desc = "Telemetría vehicular, GPS, HVAC, multimedia y observación."
    else:
        rol_cod = "guest"
        rol_nombre = "Pasajero de Cabina"
        rol_desc = "Acceso restringido. Solo infoentretenimiento y lectura básica."

    if rol_cod != st.session_state.autoos_user_role:
        st.session_state.autoos_user_role = rol_cod
        st.session_state.autoos_user_name = usuario_opcion.split(" (")[0]
        # Intentar actualizar en módulo de seguridad de Auto
        try:
            from modules.auth_security import cambiar_usuario_activo
            cambiar_usuario_activo("usr_mecanico_01" if rol_cod == "admin" else ("usr_conductor_01" if rol_cod == "user" else "usr_pasajero_01"))
        except Exception:
            pass
        st.rerun()

    st.caption(f"**Nivel de Acceso:** {rol_nombre}")
    st.caption(rol_desc)

    st.markdown("---")
    st.markdown("""
    <div style="font-family: monospace; font-size: 0.72rem; opacity: 0.8;">
        <div><b>ISO 26262 ASIL-D</b> Validado</div>
        <div><b>CAN-FD Gateway:</b> 1 Mbps Determinista</div>
        <div><b>RTOS Kernel:</b> Preemptive Multi-Core</div>
    </div>
    """, unsafe_allow_html=True)

# ====================================================================
# ESTILOS CSS GLOBALES COCKPIT AUTOOS SEGÚN TEMA ACTIVO
# ====================================================================
is_dark = (st.session_state.autoos_theme == "dark")
bg_base = "#040607" if is_dark else "#C0BAB3"
bg_surface = "#0D0714" if is_dark else "#D5CFC9"
bg_card = "#180E24" if is_dark else "#E3DDD7"
border_color = "#331E4D" if is_dark else "#A8A096"
text_primary = "#E3D9FC" if is_dark else "#160F0C"
text_muted = "#8D7AA8" if is_dark else "#52423D"
accent_color = "#BF40FA" if is_dark else "#391214"
accent_gradient = "linear-gradient(135deg, #4928C2 0%, #BF40FA 100%)" if is_dark else "linear-gradient(135deg, #52181b 0%, #391214 100%)"

st.markdown(f"""
<style>
    /* Tipografía y Base */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;800&family=Playfair+Display:wght@700;800;900&family=Outfit:wght@400;600;700&display=swap');
    
    .stApp {{
        background-color: {bg_base} !important;
        color: {text_primary} !important;
        font-family: 'Outfit', sans-serif !important;
    }}
    
    section[data-testid="stSidebar"] {{
        background-color: {bg_surface} !important;
        border-right: 1px solid {border_color} !important;
        color: {text_primary} !important;
    }}

    /* Estilos de pestañas principales */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px !important;
        background-color: {bg_surface} !important;
        padding: 8px 12px !important;
        border-radius: 18px !important;
        border: 1px solid {border_color} !important;
        margin-bottom: 20px !important;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 12px !important;
        padding: 10px 24px !important;
        color: {text_muted} !important;
        font-weight: 700 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.88rem !important;
        transition: all 0.2s ease !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {accent_gradient} !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 18px rgba(191, 64, 250, 0.3) !important;
        border: none !important;
    }}

    /* Iframe limpio sin bordes */
    iframe {{
        border: none !important;
        width: 100% !important;
        min-height: 1200px !important;
        border-radius: 16px !important;
    }}
</style>
""", unsafe_allow_html=True)

# ====================================================================
# PESTAÑAS PRINCIPALES (SIN PESTAÑAS DE CÓDIGO PYTHON NI GITHUB)
# ====================================================================
tab_sched, tab_cockpit = st.tabs([
    "⚡ Planificador & Simuladores",
    "🚗 Cockpit Vehicular Completo"
])

# --------------------------------------------------------------------
# TAB 1: PLANIFICADOR DE CPU Y SIMULADORES EN PYTHON PURO
# --------------------------------------------------------------------
with tab_sched:
    from dashboard.cpu import mostrar as mostrar_cpu
    mostrar_cpu()

# --------------------------------------------------------------------
# TAB 2: COCKPIT VEHICULAR COMPLETO CON TEMA Y USUARIO SINCRONIZADOS
# --------------------------------------------------------------------
with tab_cockpit:
    bundle_candidates = [
        AUTO_DIR / "autoos_interactive.html",
        AUTO_DIR / "modules" / "autoos_interactive.html",
        ROOT_DIR / "modules" / "autoos_interactive.html",
        ROOT_DIR / "public" / "autoos_interactive.html",
        Path("/app/applet/public/autoos_interactive.html")
    ]
    bundle_path = next((p for p in bundle_candidates if p.exists()), None)
    if bundle_path:
        with open(bundle_path, "r", encoding="utf-8") as f:
            app_html = f.read()
        # Inyectar el tema activo actual de forma inline para renderizado idéntico instantáneo
        if not is_dark:
            app_html = app_html.replace('class="dark"', 'class=""')
            app_html = app_html.replace("classList.add('dark')", "classList.remove('dark')")
            app_html = app_html.replace("localStorage.getItem('autoos_theme')", "'light'")
        else:
            app_html = app_html.replace('<html>', '<html class="dark">')
            app_html = app_html.replace("localStorage.getItem('autoos_theme')", "'dark'")
        components.html(app_html, height=1350, scrolling=True)
    else:
        st.error("Archivo interactivo de AutoOS no encontrado en la ruta de despliegue.")
