"""
Módulo de dashboard para los dispositivos.
"""
import streamlit as st
from modulos.int3_seguridad import obtener_dispositivos

def mostrar(supabase):
    """
    Muestra el estado de los dispositivos.
    """
    st.header('📡 Dispositivos')
    
    dispositivos = obtener_dispositivos(supabase)
    
    if not dispositivos:
        st.info("No hay dispositivos registrados.")
        return
        
    activos = sum(1 for d in dispositivos if d['estado'] == 'activo')
    inactivos = sum(1 for d in dispositivos if d['estado'] == 'inactivo')
    errores = sum(1 for d in dispositivos if d['estado'] == 'error')
    
    st.markdown(f"**Resumen:** {activos} activos | {inactivos} inactivos | {errores} con error")
    
    emojis_tipo = {
        'motor': '🚗',
        'freno': '🛑',
        'gps': '🗺️',
        'clima': '❄️',
        'entretenimiento': '🎵',
        'sensor': '📡',
        'camara': '📷',
        'comunicacion': '📶'
    }
    
    indicadores = {
        'activo': '🟢',
        'inactivo': '🔴',
        'error': '🟡'
    }
    
    cols = st.columns(3)
    for i, dev in enumerate(dispositivos):
        col = cols[i % 3]
        with col.container(border=True):
            tipo = dev.get('tipo', 'desconocido')
            estado = dev.get('estado', 'inactivo')
            emoji = emojis_tipo.get(tipo, '🔧')
            indicador = indicadores.get(estado, '⚪')
            
            st.markdown(f"### {emoji} {dev.get('nombre', 'Dispositivo')}")
            st.markdown(f"{indicador} Estado: **{estado.capitalize()}**")
            st.markdown(f"Tipo: {tipo.capitalize()}")
