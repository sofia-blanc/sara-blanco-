"""
Módulo de dashboard para el estado general del sistema.
"""
import streamlit as st
from modulos.int1_cpu import uso_cpu_total
from modulos.int2_memoria import uso_memoria
from modulos.int3_seguridad import obtener_bateria, obtener_eventos_criticos

def mostrar(supabase):
    """
    Muestra el estado de salud general del sistema.
    """
    st.header('🚦 Estado General del Sistema')
    
    cpu_pct = uso_cpu_total(supabase)
    mem_datos = uso_memoria(supabase)
    mem_pct = mem_datos['porcentaje']
    bateria = obtener_bateria(supabase)
    eventos_criticos = obtener_eventos_criticos(supabase)
    
    es_critico = cpu_pct > 90 or mem_pct > 95 or bateria < 10 or len(eventos_criticos) > 0
    es_precaucion = cpu_pct > 70 or mem_pct > 80 or bateria < 30
    
    if es_critico:
        estado = "CRÍTICO"
        emoji = "🔴"
        color = "red"
    elif es_precaucion:
        estado = "PRECAUCIÓN"
        emoji = "🟡"
        color = "orange"
    else:
        estado = "NORMAL"
        emoji = "🟢"
        color = "green"
        
    st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 2px solid {color}; border-radius: 10px; background-color: {color}20; margin-bottom: 20px;">
            <h1 style="font-size: 80px; margin: 0;">{emoji}</h1>
            <h2 style="color: {color};">{estado}</h2>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Uso de CPU", f"{cpu_pct:.1f}%")
    col2.metric("Uso de Memoria", f"{mem_pct:.1f}%")
    col3.metric("Batería", f"{bateria:.1f}%")
    
    if eventos_criticos:
        st.subheader("⚠️ Eventos Críticos")
        for evento in eventos_criticos:
            st.error(evento.get('mensaje', 'Evento crítico detectado'))
