import streamlit as st
from modulos import int1_cpu, int2_memoria, int3_seguridad

TRANSICIONES_PERMITIDAS = {
    "nuevo": ["listo"],
    "listo": ["ejecutando"],
    "ejecutando": ["bloqueado", "suspendido", "terminado"],
    "bloqueado": ["listo"],
    "suspendido": ["listo"],
    "terminado": []
}

def mostrar(supabase, usuario: dict):
    """Muestra la interfaz para cambiar el estado de un proceso."""
    st.title("🔄 Cambiar Estado de Proceso")
    
    procesos = int1_cpu.listar_procesos(supabase)
    procesos_dict = {f"{p['id']} - {p['nombre']}": p for p in procesos if p['estado'] != "terminado"}
    
    if not procesos_dict:
        st.info("No hay procesos activos para cambiar de estado.")
        return
        
    proceso_sel = st.selectbox("Seleccione el proceso", list(procesos_dict.keys()))
    proceso = procesos_dict[proceso_sel]
    
    estado_actual = proceso["estado"]
    st.write(f"**Estado actual:** {estado_actual.upper()}")
    
    opciones_nuevos_estados = TRANSICIONES_PERMITIDAS.get(estado_actual, [])
    
    if not opciones_nuevos_estados:
        st.warning("Este proceso no tiene transiciones de estado permitidas.")
        return
        
    nuevo_estado = st.selectbox("Seleccione el nuevo estado", opciones_nuevos_estados)
    
    if st.button("Confirmar Cambio"):
        if int3_seguridad.validar_rol_para_accion(supabase, usuario['id'], "cambiar_estado"):
            exito = int1_cpu.cambiar_estado_proceso(supabase, proceso["id"], nuevo_estado, usuario['email'])
            if exito:
                int2_memoria.registrar_log(supabase, f"Estado del proceso {proceso['id']} cambiado de {estado_actual} a {nuevo_estado}", "INFO", usuario['email'])
                st.success(f"Estado actualizado a {nuevo_estado} exitosamente.")
            else:
                st.error("Error al actualizar el estado del proceso.")
        else:
            st.error("No tienes permisos para realizar esta acción.")
