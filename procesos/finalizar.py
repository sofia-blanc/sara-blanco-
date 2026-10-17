import streamlit as st
from modulos import int1_cpu, int2_memoria, int3_seguridad

def mostrar(supabase, usuario: dict):
    """Muestra la interfaz para finalizar un proceso."""
    st.title("⏹️ Finalizar Proceso")
    
    procesos = int1_cpu.listar_procesos(supabase)
    procesos_activos = [p for p in procesos if p["estado"] != "terminado"]
    procesos_dict = {f"{p['id']} - {p['nombre']} (CPU: {p['cpu_porcentaje']}%, RAM: {p['memoria_mb']}MB)": p for p in procesos_activos}
    
    if not procesos_dict:
        st.info("No hay procesos activos para finalizar.")
        return
        
    proceso_sel = st.selectbox("Seleccione el proceso a finalizar", list(procesos_dict.keys()))
    proceso = procesos_dict[proceso_sel]
    
    st.warning("⚠️ Esta acción liberará la memoria y terminará el proceso de forma permanente.")
    
    if st.button("Confirmar Finalización", type="primary"):
        if int3_seguridad.validar_rol_para_accion(supabase, usuario['id'], "finalizar_proceso"):
            exito = int1_cpu.finalizar_proceso(supabase, proceso["id"], usuario['email'])
            
            if exito:
                # Liberar memoria
                int2_memoria.liberar_memoria_proceso(supabase, proceso["id"])
                
                # Loggear
                int2_memoria.registrar_log(supabase, f"Proceso {proceso['id']} finalizado", "INFO", usuario['email'])
                
                st.success(f"Proceso '{proceso['nombre']}' finalizado y recursos liberados.")
            else:
                st.error("Error al finalizar el proceso.")
        else:
            st.error("No tienes permisos suficientes para finalizar procesos.")
