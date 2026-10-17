import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_supabase() -> Client:
    """
    Inicializa y retorna el cliente de Supabase usando los secretos de Streamlit.
    """
    url: str = st.secrets["supabase"]["url"]
    key: str = st.secrets["supabase"]["key"]
    return create_client(url, key)
