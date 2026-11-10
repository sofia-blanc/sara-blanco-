"""
====================================================================
AUTOOS - MÓDULO INT 1: CPU, PROCESOS Y PLANIFICACIÓN MULTIALGORITMO
Responsable: Integrante 1 (CPU & Scheduling Engine)
====================================================================
Implementa los algoritmos de planificación de CPU:
  - FCFS (First-Come, First-Served)
  - Round Robin (con Quantum configurable)
  - Priority Scheduling (No Apropiativo y Apropiativo / Preemptive)
Incluye los simuladores integrados:
  - Batería Baja (Suspensión dinámica de procesos no esenciales y ahorro de Watts)
  - Proceso Crítico (Inyección ASIL-D con desalojo inmediato de CPU)
====================================================================
"""

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import copy

PROCESOS_DEFECTO = [
    {
        "id": 101,
        "nombre": "Control Motor Inversor",
        "prioridad": 1,
        "rafaga": 6,
        "llegada": 0,
        "categoria": "control",
        "critico": True,
        "color": "#ef4444",
        "consumo_watts": 45,
        "memoria_mb": 128
    },
    {
        "id": 102,
        "nombre": "Sensor Fusión LiDAR/Radar",
        "prioridad": 2,
        "rafaga": 4,
        "llegada": 1,
        "categoria": "sensor",
        "critico": False,
        "color": "#06b6d4",
        "consumo_watts": 28,
        "memoria_mb": 256
    },
    {
        "id": 103,
        "nombre": "Frenado Regenerativo (BMS)",
        "prioridad": 1,
        "rafaga": 5,
        "llegada": 2,
        "categoria": "seguridad",
        "critico": True,
        "color": "#f97316",
        "consumo_watts": 35,
        "memoria_mb": 96
    },
    {
        "id": 104,
        "nombre": "Navegación GPS y Mapas",
        "prioridad": 3,
        "rafaga": 3,
        "llegada": 3,
        "categoria": "control",
        "critico": False,
        "color": "#3b82f6",
        "consumo_watts": 15,
        "memoria_mb": 320
    },
    {
        "id": 105,
        "nombre": "Climatización Confort (HVAC)",
        "prioridad": 4,
        "rafaga": 4,
        "llegada": 4,
        "categoria": "confort",
        "critico": False,
        "color": "#a855f7",
        "consumo_watts": 50,
        "memoria_mb": 64
    },
    {
        "id": 106,
        "nombre": "Infoentretenimiento Multimedia",
        "prioridad": 5,
        "rafaga": 5,
        "llegada": 5,
        "categoria": "multimedia",
        "critico": False,
        "color": "#ec4899",
        "consumo_watts": 40,
        "memoria_mb": 512
    }
]

def obtener_procesos(supabase=None) -> List[Dict[str, Any]]:
    """Retorna la lista de procesos activos del sistema con formato para el dashboard."""
    return [
        {
            "id": p["id"],
            "nombre": p["nombre"],
            "prioridad": "crítica" if p["prioridad"] == 1 else "alta" if p["prioridad"] == 2 else "media" if p["prioridad"] == 3 else "baja",
            "prioridad_num": p["prioridad"],
            "estado": "ejecutando" if p["id"] == 101 else "listo",
            "cpu_porcentaje": 22 if p["id"] == 101 else 15,
            "memoria_mb": p["memoria_mb"],
            "creado_por": "sistema",
            "created_at": "2026-10-18T10:00:00"
        }
        for p in PROCESOS_DEFECTO
    ]

def simular_planificacion(
    algoritmo: str = "RR",
    quantum: int = 2,
    bateria_baja: bool = False,
    inyectar_critico: bool = False,
    procesos_custom: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Ejecuta la simulación completa del algoritmo seleccionado y genera:
      - Trazas del diagrama de Gantt
      - Métricas de rendimiento (T. Espera, T. Retorno, Utilización CPU)
      - Registro de eventos y desalojos preemptivos
    """
    alg = algoritmo.upper()
    procs = copy.deepcopy(procesos_custom or PROCESOS_DEFECTO)
    
    # Inyección de Proceso Crítico si está activo
    if inyectar_critico:
        procs.append({
            "id": 999,
            "nombre": "🚨 Frenado Autónomo Emergencia (AEB)",
            "prioridad": 1,
            "rafaga": 3,
            "llegada": 3,
            "categoria": "seguridad",
            "critico": True,
            "color": "#b91c1c",
            "consumo_watts": 65,
            "memoria_mb": 64
        })

    # Preparar estructuras de control
    for p in procs:
        p["restante"] = p["rafaga"]
        p["estado"] = "NUEVO"
        p["inicio"] = None
        p["fin"] = None
        p["espera"] = 0
        p["retorno"] = 0
        p["suspendido"] = False

    t = 0
    cola_listos: List[Dict[str, Any]] = []
    en_cpu: Optional[Dict[str, Any]] = None
    quantum_restante = quantum
    gantt_slots: List[Dict[str, Any]] = []
    eventos: List[str] = []
    conmutaciones = 0
    tiempo_inactivo = 0
    watts_ahorrados = 0

    max_tiempo = 150 # Salvaguarda contra bucles infinitos

    while t < max_tiempo:
        # 1. Llegada de procesos en t
        for p in procs:
            if p["llegada"] == t and p["estado"] == "NUEVO":
                # Filtro de Batería Baja: si el proceso es no esencial (prioridad >= 4 o multimedia/confort), suspender
                if bateria_baja and (p["prioridad"] >= 4 or p["categoria"] in ["multimedia", "confort"]):
                    p["estado"] = "SUSPENDIDO"
                    p["suspendido"] = True
                    watts_ahorrados += p["consumo_watts"]
                    eventos.append(f"t={t}s: [Batería Baja] Proceso '{p['nombre']}' SUSPENDIDO para ahorrar {p['consumo_watts']}W.")
                else:
                    p["estado"] = "LISTO"
                    cola_listos.append(p)
                    eventos.append(f"t={t}s: Proceso '{p['nombre']}' (P{p['id']}, Prio {p['prioridad']}) llegó a cola de listos.")

        # Ordenar cola de listos según algoritmo
        if alg in ["PRIORITY", "PRIORITY_PREEMPTIVE"]:
            cola_listos.sort(key=lambda x: (x["prioridad"], x["llegada"], x["id"]))
        elif alg == "FCFS":
            cola_listos.sort(key=lambda x: (x["llegada"], x["id"]))
        # Round Robin mantiene orden circular FIFO

        # 2. Desalojo Preemptivo en Prioridad Apropiativa
        if alg == "PRIORITY_PREEMPTIVE" and en_cpu and cola_listos:
            if cola_listos[0]["prioridad"] < en_cpu["prioridad"]:
                eventos.append(f"t={t}s: [DESALOJO PREEMPTIVO] Proceso crítico '{cola_listos[0]['nombre']}' desaloja a '{en_cpu['nombre']}'.")
                en_cpu["estado"] = "LISTO"
                cola_listos.append(en_cpu)
                cola_listos.sort(key=lambda x: (x["prioridad"], x["llegada"], x["id"]))
                en_cpu = None
                conmutaciones += 1

        # 3. Despacho a CPU si está libre
        if not en_cpu and cola_listos:
            en_cpu = cola_listos.pop(0)
            en_cpu["estado"] = "EJECUTANDO"
            if en_cpu["inicio"] is None:
                en_cpu["inicio"] = t
            quantum_restante = quantum
            conmutaciones += 1
            eventos.append(f"t={t}s: CPU asignada a '{en_cpu['nombre']}' (Restante: {en_cpu['restante']}s).")

        # 4. Registro en Gantt y ejecución
        if en_cpu:
            # Añadir o extender slot de Gantt
            if gantt_slots and gantt_slots[-1]["id"] == en_cpu["id"] and gantt_slots[-1]["fin"] == t:
                gantt_slots[-1]["fin"] = t + 1
            else:
                gantt_slots.append({
                    "id": en_cpu["id"],
                    "proceso": en_cpu["nombre"],
                    "inicio": t,
                    "fin": t + 1,
                    "color": en_cpu["color"],
                    "critico": en_cpu["critico"],
                    "prioridad": en_cpu["prioridad"],
                    "estado": "ejecutando"
                })

            en_cpu["restante"] -= 1
            quantum_restante -= 1

            if en_cpu["restante"] <= 0:
                en_cpu["estado"] = "TERMINADO"
                en_cpu["fin"] = t + 1
                en_cpu["retorno"] = en_cpu["fin"] - en_cpu["llegada"]
                en_cpu["espera"] = en_cpu["retorno"] - en_cpu["rafaga"]
                eventos.append(f"t={t+1}s: Proceso '{en_cpu['nombre']}' COMPLETADO. (Retorno: {en_cpu['retorno']}s, Espera: {en_cpu['espera']}s).")
                en_cpu = None
            elif alg == "RR" and quantum_restante <= 0:
                en_cpu["estado"] = "LISTO"
                cola_listos.append(en_cpu)
                eventos.append(f"t={t+1}s: Quantum expiró para '{en_cpu['nombre']}'. Reingresa a cola circular.")
                en_cpu = None
        else:
            tiempo_inactivo += 1
            if gantt_slots and gantt_slots[-1]["id"] is None and gantt_slots[-1]["fin"] == t:
                gantt_slots[-1]["fin"] = t + 1
            else:
                gantt_slots.append({
                    "id": None,
                    "proceso": "CPU IDLE (Inactiva)",
                    "inicio": t,
                    "fin": t + 1,
                    "color": "#334155",
                    "critico": False,
                    "prioridad": 5,
                    "estado": "inactivo"
                })

        t += 1

        # Condición de parada: todos los procesos terminados o suspendidos
        activos = [p for p in procs if p["estado"] not in ["TERMINADO", "SUSPENDIDO"]]
        if not activos and not en_cpu and not cola_listos:
            break

    # Calcular estadísticas
    terminados = [p for p in procs if p["estado"] == "TERMINADO"]
    num_term = len(terminados)
    espera_prom = round(sum(p["espera"] for p in terminados) / num_term, 2) if num_term > 0 else 0.0
    retorno_prom = round(sum(p["retorno"] for p in terminados) / num_term, 2) if num_term > 0 else 0.0
    ocupado = t - tiempo_inactivo
    cpu_util = round((ocupado / t) * 100.0, 1) if t > 0 else 0.0

    return {
        "algoritmo": alg,
        "quantum": quantum,
        "tiempo_total": t,
        "gantt_slots": gantt_slots,
        "procesos": procs,
        "eventos": eventos,
        "espera_promedio": espera_prom,
        "retorno_promedio": retorno_prom,
        "cpu_utilizacion": cpu_util,
        "conmutaciones": conmutaciones,
        "watts_ahorrados": watts_ahorrados,
        "suspendidos_count": len([p for p in procs if p["estado"] == "SUSPENDIDO"]),
    }

def uso_cpu(supabase=None, algoritmo="RR", quantum=2, bateria_baja=False, proceso_critico=False) -> List[Dict[str, Any]]:
    """Genera datos de Gantt formateados para Plotly en Streamlit."""
    res = simular_planificacion(
        algoritmo=algoritmo,
        quantum=quantum,
        bateria_baja=bateria_baja,
        inyectar_critico=proceso_critico
    )
    ahora = datetime.now()
    datos_plotly = []
    for slot in res["gantt_slots"]:
        datos_plotly.append({
            "proceso": slot["proceso"],
            "inicio_seg": slot["inicio"],
            "fin_seg": slot["fin"],
            "duracion": slot["fin"] - slot["inicio"],
            "inicio": ahora + timedelta(seconds=slot["inicio"]),
            "fin": ahora + timedelta(seconds=slot["fin"]),
            "estado": slot["estado"],
            "prioridad": "Crítica" if slot["prioridad"] == 1 else "Normal"
        })
    return datos_plotly

def uso_cpu_total(supabase=None) -> float:
    """Retorna el uso total estimado de CPU."""
    return 74.5

def crear_proceso(supabase, datos: dict, usuario: str) -> dict:
    nuevo_proceso = datos.copy()
    nuevo_proceso["id"] = 999
    nuevo_proceso["created_at"] = datetime.now().isoformat()
    nuevo_proceso["creado_por"] = usuario
    nuevo_proceso["estado"] = "nuevo"
    return nuevo_proceso

def listar_procesos(supabase) -> list[dict]:
    return obtener_procesos(supabase)

def cambiar_estado_proceso(supabase, proceso_id: int, nuevo_estado: str, usuario: str) -> bool:
    return True

def finalizar_proceso(supabase, proceso_id: int, usuario: str) -> bool:
    return True
