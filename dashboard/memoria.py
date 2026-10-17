"""
Módulo de dashboard para la memoria RAM.
"""
import streamlit as st
import plotly.graph_objects as go
from modulos.int2_memoria import uso_memoria

def mostrar(supabase):
    """
    Muestra el estado de la memoria.
    """
    st.header('🧠 Memoria')
    
    memoria = uso_memoria(supabase)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total (MB)", f"{memoria['total_mb']:.1f}")
    col2.metric("Usado (MB)", f"{memoria['usado_mb']:.1f}")
    col3.metric("Libre (MB)", f"{memoria['libre_mb']:.1f}")
    
    if memoria['porcentaje'] > 85:
        st.warning("¡Alto uso de memoria RAM!")
        
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=['Memoria'],
        x=[memoria['usado_mb']],
        name='Usado',
        orientation='h',
        marker=dict(color='orange')
    ))
    fig.add_trace(go.Bar(
        y=['Memoria'],
        x=[memoria['libre_mb']],
        name='Libre',
        orientation='h',
        marker=dict(color='green')
    ))
    fig.update_layout(
        barmode='stack',
        title='Uso de Memoria RAM',
        xaxis_title="MB"
    )
    
    st.plotly_chart(fig, use_container_width=True)
