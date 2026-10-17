"""
====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Módulo: auth_security.py
Responsable: Integrante 3 (Seguridad, Roles, Permisos y RLS)
====================================================================
Implementa:
- Gestión de usuarios y perfiles vehiculares
- Modelo RBAC (Role-Based Access Control)
- Demostración de Autenticación != Autorización
- Verificación estricta de permisos para creación y alteración de procesos
- Registro de auditoría de intentos autorizados y bloqueados (403 Forbidden)
"""

import streamlit as st
import datetime
import uuid
from typing import Dict, Any, Tuple, List, Optional
from config import get_db, get_supabase_client

# Definición de Roles del Sistema AutoOS
ROLES_INFO = {
    "admin": {
        "etiqueta": "Mecánico / Ingeniero de Servicio",
        "badge_color": "",
        "descripcion": "Acceso de nivel Kernel. Calibración de sensores ADAS, gestión de usuarios, depuración de hardware y control total de procesos.",
        "nivel": 10
    },
    "user": {
        "etiqueta": "Conductor Autorizado",
        "badge_color": "",
        "descripcion": "Control de navegación, climatización, infoentretenimiento y procesos estándar de conducción. Sin permisos de calibración crítica.",
        "nivel": 5
    },
    "guest": {
        "etiqueta": "Pasajero / Invitado en Cabina",
        "badge_color": "",
        "descripcion": "Acceso restringido a infoentretenimiento y confort de cabina. Bloqueo total de administración de procesos y hardware.",
        "nivel": 1
    }
}

def inicializar_sesion_usuario():
    """Garantiza que exista un usuario vehicular activo en la sesión"""
    if "current_user" not in st.session_state:
        db = get_db()
        # Iniciar por defecto con el Conductor
        st.session_state["current_user"] = db["perfiles"][1]  # Laura Gómez (Conductora)


def obtener_usuario_actual() -> Dict[str, Any]:
    """Retorna el usuario vehicular actualmente autenticado"""
    inicializar_sesion_usuario()
    return st.session_state["current_user"]


def cambiar_usuario_activo(user_id: str):
    """Permite alternar en vivo entre Mecánico, Conductor y Pasajero para sustentación"""
    db = get_db()
    for usr in db["perfiles"]:
        if usr["id"] == user_id:
            st.session_state["current_user"] = usr
            # Registrar log de login
            registrar_evento_seguridad(
                tipo="seguridad",
                severidad="info",
                mensaje=f"Sesión activa cambiada a: {usr['nombre_completo']} [Rol: {usr['rol'].upper()}]"
            )
            return


def tiene_permiso(usuario: Dict[str, Any], clave_permiso: str) -> bool:
    """
    Verifica si el rol del usuario posee un permiso específico en la matriz RBAC.
    """
    db = get_db()
    rol = usuario.get("rol", "guest")
    permisos_del_rol = db["roles_permisos"].get(rol, [])
    return clave_permiso in permisos_del_rol


def validar_accion(usuario: Dict[str, Any], accion: str, recurso: str) -> Tuple[bool, Optional[str]]:
    """
    Valida la autorización de una acción y registra el evento en auditoría.
    Demuestra fehacientemente: Autenticación != Autorización.
    """
    db = get_db()
    autorizado = tiene_permiso(usuario, accion)
    motivo_rechazo = None
    
    if not autorizado:
        rol_label = ROLES_INFO.get(usuario.get("rol"), {}).get("etiqueta", usuario.get("rol"))
        motivo_rechazo = f"Acceso Denegado (403): El rol '{rol_label}' no posee el permiso '{accion}' sobre el recurso '{recurso}'."
        
        # Registrar evento crítico de seguridad si intentó finalizar un proceso crítico
        severidad = "advertencia" if "finalizar" in accion or "calibrar" in accion else "info"
        registrar_evento_seguridad(
            tipo="intento_no_autorizado",
            severidad=severidad,
            mensaje=f"Violación de seguridad: {usuario['email']} intentó '{accion}' sin autorización.",
            detalles={"recurso": recurso, "rol": usuario.get("rol"), "motivo": motivo_rechazo}
        )
    
    # Guardar en auditoría
    registro_auditoria = {
        "id": str(uuid.uuid4()),
        "usuario_email": usuario.get("email"),
        "rol": usuario.get("rol"),
        "recurso": recurso,
        "accion": accion,
        "autorizado": autorizado,
        "motivo_rechazo": motivo_rechazo,
        "hora": datetime.datetime.now().strftime("%H:%M:%S")
    }
    db["auditoria"].insert(0, registro_auditoria)
    
    return autorizado, motivo_rechazo


def registrar_evento_seguridad(tipo: str, severidad: str, mensaje: str, dispositivo_codigo: Optional[str] = None, detalles: Optional[Dict] = None):
    """Registra un evento en la tabla 'eventos' de AutoOS"""
    db = get_db()
    usuario = st.session_state.get("current_user", {})
    evento = {
        "id": str(uuid.uuid4()),
        "tipo_evento": tipo,
        "severidad": severidad,
        "dispositivo_codigo": dispositivo_codigo,
        "usuario": usuario.get("nombre_completo", "Sistema"),
        "mensaje": mensaje,
        "detalles": detalles or {},
        "resuelto": False if severidad in ["critico", "emergencia"] else True,
        "creado_en": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    db["eventos"].insert(0, evento)


def obtener_auditoria(limite: int = 15) -> List[Dict[str, Any]]:
    """Obtiene los últimos registros de auditoría de seguridad"""
    db = get_db()
    return db["auditoria"][:limite]


def obtener_matriz_permisos() -> Dict[str, List[Dict[str, Any]]]:
    """Retorna la matriz de permisos clasificada para renderizado en tabla UI"""
    db = get_db()
    catalogo = db["permisos"]
    roles_permisos = db["roles_permisos"]
    
    resultado = []
    for p in catalogo:
        resultado.append({
            "Clave Permiso": p["clave"],
            "Módulo": p["modulo"].upper(),
            "Descripción": p["descripcion"],
            "Mecánico (Admin)": "Permitido" if p["clave"] in roles_permisos["admin"] else "Denegado",
            "Conductor (User)": "Permitido" if p["clave"] in roles_permisos["user"] else "Denegado",
            "Pasajero (Guest)": "Permitido" if p["clave"] in roles_permisos["guest"] else "Denegado",
        })
    return resultado
