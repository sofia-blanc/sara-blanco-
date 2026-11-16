"""
Módulo de dashboard para el resumen de procesos.
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from modulos.int1_cpu import obtener_procesos

def mostrar(supabase):
    """
    Muestra el resumen de los procesos.
    """
    st.header('⚙️ Procesos')
    
    procesos = obtener_procesos(supabase)
    
    if not procesos:
        st.info("No hay procesos en el sistema.")
        return
        
    df = pd.DataFrame(procesos)
    conteo_estados = df['estado'].value_counts().to_dict()
    
    estados = ['nuevo', 'listo', 'ejecutando', 'bloqueado', 'suspendido', 'terminado']
    emojis = {
        'nuevo': '🌱', 
        'listo': '⏳', 
        'ejecutando': '▶️', 
        'bloqueado': '🔒', 
        'suspendido': '⏸️', 
        'terminado': '✅'
    }
    colores = {
        'nuevo': 'gray',
        'listo': 'blue',
        'ejecutando': 'green',
        'bloqueado': 'red',
        'suspendido': 'orange',
        'terminado': 'black'
    }
    
    st.subheader(f"Total de procesos: {len(procesos)}")
    
    cols = st.columns(len(estados))
    for i, estado in enumerate(estados):
        conteo = conteo_estados.get(estado, 0)
        cols[i].metric(f"{emojis[estado]} {estado.capitalize()}", conteo)
        
    datos_pie = pd.DataFrame({
        'Estado': list(conteo_estados.keys()),
        'Cantidad': list(conteo_estados.values())
    })
    
    fig = px.pie(
        datos_pie, 
        values='Cantidad', 
        names='Estado', 
        title='Distribución de Procesos por Estado',
        hole=0.4,
        color='Estado',
        color_discrete_map=colores
    )
    st.plotly_chart(fig, use_container_width=True)
