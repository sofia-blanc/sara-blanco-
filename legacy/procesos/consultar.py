import streamlit as st
import pandas as pd
from modulos import int1_cpu

def mostrar(supabase):
    """Muestra la interfaz para consultar procesos."""
    st.title("📋 Consultar Procesos")
    
    procesos = int1_cpu.listar_procesos(supabase)
    
    if not procesos:
        st.info("No hay procesos en el sistema.")
        return
        
    df = pd.DataFrame(procesos)
    
    col1, col2, col3 = st.columns(3)
    
    # Filtros
    with col1:
        filtro_estado = st.selectbox("Filtrar por Estado", ["Todos"] + list(df["estado"].unique()))
    with col2:
        filtro_prioridad = st.selectbox("Filtrar por Prioridad", ["Todos"] + list(df["prioridad"].unique()))
    with col3:
        # Metricas resumen
        activos = len(df[df["estado"] == "ejecutando"])
        st.metric("Procesos Ejecutando", activos)
        
    # Aplicar filtros
    if filtro_estado != "Todos":
        df = df[df["estado"] == filtro_estado]
    if filtro_prioridad != "Todos":
        df = df[df["prioridad"] == filtro_prioridad]
        
    st.dataframe(
        df,
        column_config={
            "estado": st.column_config.TextColumn(
                "Estado"
            ),
            "cpu_porcentaje": st.column_config.ProgressColumn(
                "CPU %",
                format="%f",
                min_value=0,
                max_value=100,
            ),
        },
        hide_index=True,
        use_container_width=True
    )
