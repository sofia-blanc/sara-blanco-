"""
Módulo de dashboard para el uso de CPU.
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from modulos.int1_cpu import uso_cpu, uso_cpu_total

def mostrar(supabase):
    """
    Muestra la pestaña del uso de CPU.
    """
    st.header('🖥️ CPU')
    
    total_cpu = uso_cpu_total(supabase)
    st.metric("Uso Total de CPU (%)", f"{total_cpu:.1f}%")
    
    datos_cpu = uso_cpu(supabase)
    if datos_cpu:
        df = pd.DataFrame(datos_cpu)
        fig = px.timeline(
            df, 
            x_start="inicio", 
            x_end="fin", 
            y="proceso", 
            color="estado", 
            title='Diagrama Gantt — Planificación de CPU'
        )
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de CPU disponibles.")
