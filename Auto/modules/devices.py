"""
====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Módulo: devices.py
Responsable: Integrante 3 (Seguridad, Dispositivos y Controladores)
====================================================================
Implementa:
- Abstracción de Hardware vehicular (Sensores ADAS, Actuadores By-Wire, BMS)
- Supervisión de Buses de Comunicación (CAN-Bus, Automotive Ethernet, LIN)
- Máquina de estados de dispositivos: Operativo, Degradado, Falla, Desconectado
- Diagnóstico OBD-II simulado y calibración de periféricos
- Inyección de fallas y pruebas de desconexión (requeridas en sustentación)
"""

from typing import List, Dict, Any, Optional, Tuple
from config import get_db
from modules.auth_security import validar_accion, registrar_evento_seguridad

def obtener_dispositivos(filtro_estado: Optional[str] = None, filtro_bus: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retorna la lista de dispositivos de AutoOS con filtros opcionales.
    Requisito de la plantilla: 'Entrega la lista de dispositivos con su estado'
    """
    db = get_db()
    dispositivos = db["dispositivos"]
    
    resultado = []
    for d in dispositivos:
        if filtro_estado and filtro_estado != "Todos" and d["estado"] != filtro_estado.lower():
            continue
        if filtro_bus and filtro_bus != "Todos" and d["puerto_bus"] != filtro_bus:
            continue
        resultado.append(d)
        
    return resultado


def obtener_dispositivo(codigo: str) -> Optional[Dict[str, Any]]:
    """Retorna un dispositivo vehicular por su código de identificación"""
    db = get_db()
    for d in db["dispositivos"]:
        if d["codigo"] == codigo:
            return d
    return None


def cambiar_estado_dispositivo(codigo: str, nuevo_estado: str, usuario_actual: Dict[str, Any], motivo: str = "") -> Tuple[bool, str]:
    """
    Modifica el estado operativo de un sensor o actuador (Operativo, Degradado, Falla, Desconectado).
    Aplica rigurosamente validación de permisos de Integrante 3.
    """
    # Validar permisos
    accion_requerida = "dispositivo.desconectar" if nuevo_estado == "desconectado" else "dispositivo.inyectar_fallo"
    if nuevo_estado == "operativo":
        accion_requerida = "dispositivo.calibrar"
        
    autorizado, msg_rechazo = validar_accion(usuario_actual, accion_requerida, recurso=f"dispositivo:{codigo}")
    if not autorizado:
        return False, msg_rechazo
        
    dev = obtener_dispositivo(codigo)
    if not dev:
        return False, f"Dispositivo {codigo} no encontrado en el árbol de hardware."
        
    estado_previo = dev["estado"]
    dev["estado"] = nuevo_estado
    
    # Ajustar porcentaje de salud simulado
    if nuevo_estado == "operativo":
        dev["salud_porcentaje"] = 98
    elif nuevo_estado == "degradado":
        dev["salud_porcentaje"] = 65
    elif nuevo_estado == "falla":
        dev["salud_porcentaje"] = 15
    elif nuevo_estado == "desconectado":
        dev["salud_porcentaje"] = 0
        
    # Registrar evento de hardware
    severidad = "critico" if (nuevo_estado in ["falla", "desconectado"] and dev["nivel_critico"] == "critico") else "advertencia"
    if nuevo_estado == "operativo":
        severidad = "info"
        
    registrar_evento_seguridad(
        tipo="dispositivo_fallo" if nuevo_estado != "operativo" else "cambio_estado_so",
        severidad=severidad,
        dispositivo_codigo=codigo,
        mensaje=f"Dispositivo {dev['nombre']} ({codigo}) transitó de [{estado_previo.upper()}] a [{nuevo_estado.upper()}]. Motivo: {motivo or 'Comando manual'}",
        detalles={"salud_actual": dev["salud_porcentaje"], "bus": dev["puerto_bus"], "critico": dev["nivel_critico"]}
    )
    
    return True, f"Dispositivo {codigo} actualizado exitosamente a '{nuevo_estado}'."


def calibrar_dispositivo(codigo: str, usuario_actual: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Simula una secuencia de calibración OBD-II de un sensor o actuador (Solo Mecánico/Admin)
    """
    autorizado, msg_rechazo = validar_accion(usuario_actual, "dispositivo.calibrar", recurso=f"dispositivo:{codigo}")
    if not autorizado:
        return False, msg_rechazo
        
    dev = obtener_dispositivo(codigo)
    if not dev:
        return False, f"Dispositivo {codigo} no existe."
        
    dev["estado"] = "operativo"
    dev["salud_porcentaje"] = 100
    
    registrar_evento_seguridad(
        tipo="cambio_estado_so",
        severidad="info",
        dispositivo_codigo=codigo,
        mensaje=f"Calibración exitosa de {dev['nombre']} ({codigo}). Parámetros restablecidos al 100% de tolerancia.",
        detalles={"ejecutado_por": usuario_actual.get("nombre_completo")}
    )
    return True, f"Calibración de {codigo} completada con éxito. Sensor al 100% de operatividad."


def obtener_resumen_dispositivos() -> Dict[str, Any]:
    """
    Retorna métricas clave de salud de dispositivos para el tablero principal
    """
    dispositivos = obtener_dispositivos()
    total = len(dispositivos)
    operativos = sum(1 for d in dispositivos if d["estado"] == "operativo")
    degradados = sum(1 for d in dispositivos if d["estado"] == "degradado")
    fallas = sum(1 for d in dispositivos if d["estado"] == "falla")
    desconectados = sum(1 for d in dispositivos if d["estado"] == "desconectado")
    
    salud_promedio = sum(d["salud_porcentaje"] for d in dispositivos) / total if total > 0 else 0
    dispositivos_criticos_en_falla = [d for d in dispositivos if d["nivel_critico"] == "critico" and d["estado"] in ["falla", "desconectado"]]
    
    return {
        "total": total,
        "operativos": operativos,
        "degradados": degradados,
        "fallas": fallas,
        "desconectados": desconectados,
        "salud_promedio": round(salud_promedio, 1),
        "hay_falla_critica": len(dispositivos_criticos_en_falla) > 0,
        "dispositivos_criticos_en_falla": dispositivos_criticos_en_falla
    }
