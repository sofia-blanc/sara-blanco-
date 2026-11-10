import streamlit as st
from modulos import int1_cpu, int2_memoria, int3_seguridad

def mostrar(supabase, usuario: dict):
    """Muestra la interfaz para crear un nuevo proceso."""
    st.title("➕ Crear Nuevo Proceso")
    
    with st.form("form_crear_proceso"):
        nombre = st.text_input("Nombre del proceso")
        prioridad = st.selectbox("Prioridad", ["crítica", "alta", "media", "baja"])
        memoria_mb = st.number_input("Memoria requerida en MB", min_value=1, max_value=1024, value=64)
        descripcion = st.text_area("Descripción (opcional)")
        
        submitted = st.form_submit_button("Crear Proceso")
        
        if submitted:
            if not nombre:
                st.error("El nombre del proceso es obligatorio.")
                return
            
            # Verificar permiso
            tiene_permiso = int3_seguridad.verificar_permiso(supabase, usuario['id'], "crear_proceso")
            
            if tiene_permiso:
                datos = {
                    "nombre": nombre,
                    "prioridad": prioridad,
                    "memoria_mb": memoria_mb,
                    "descripcion": descripcion,
                    "cpu_porcentaje": 0
                }
                # Crear proceso
                nuevo_proceso = int1_cpu.crear_proceso(supabase, datos, usuario['email'])
                
                # Registrar log
                int2_memoria.registrar_log(supabase, f"Proceso {nombre} creado", "INFO", usuario['email'])
                
                st.success(f"Proceso '{nombre}' creado exitosamente con ID {nuevo_proceso['id']}.")
            else:
                st.error("No tienes permisos para crear procesos.")
