import streamlit as st
from config.supabase_client import get_supabase

def verificar_sesion() -> bool:
    """Verifica si hay una sesión activa en Streamlit."""
    return 'usuario' in st.session_state

def mostrar_login():
    """Muestra el formulario de inicio de sesión."""
    st.markdown("<h1 style='text-align: center;'>🚗 AutoOS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Sistema Operativo Automotriz</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            email = st.text_input("Correo Electrónico")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            
            if submit:
                supabase = get_supabase()
                try:
                    # Intento de login
                    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    if response.user:
                        # Extraer datos básicos
                        usuario = {
                            "id": response.user.id,
                            "email": response.user.email,
                            "rol": "conductor"  # Valor por defecto
                        }
                        
                        # Intentar obtener el rol de la tabla perfiles si existe
                        try:
                            perfil_res = supabase.table("perfiles").select("rol").eq("id", response.user.id).execute()
                            if perfil_res.data and len(perfil_res.data) > 0:
                                usuario["rol"] = perfil_res.data[0].get("rol", "conductor")
                        except Exception as e:
                            pass # Si no existe la tabla o hay error, mantenemos el rol por defecto
                            
                        st.session_state['usuario'] = usuario
                        st.rerun()
                except Exception as e:
                    st.error("Error al iniciar sesión: Credenciales inválidas.")
