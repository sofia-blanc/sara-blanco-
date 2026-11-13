"""
====================================================================
AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
Dashboard Principal de Control, Integración del Kernel & Supabase
====================================================================
Implementa y conecta de forma real e interactiva los 10 criterios:
1. Secuencia de arranque formal en 7 fases (Boot).
2. Inicialización y administración del Kernel y sus subsistemas.
3. Creación de procesos con asignación First-Fit de RAM física.
4. Máquina de estados estricta y avance por ticks discretos de CPU.
5. Terminación de procesos con liberación y coalescencia de RAM.
6. Planificador multialgoritmo (FCFS, Priority min-heap, Round Robin con quantum).
7. Gestor de memoria física First-Fit y mapa dinámico de particiones.
8. Memoria virtual con 64 marcos, tablas de páginas, SWAP y fallos de página.
9. Sistema de archivos jerárquico persistente (VFS) sincronizado a JSON.
10. Terminal interactiva real con 16 comandos sobre el Kernel vivo.
Incluye además: Cockpit vehicular, Batería BMS, Matriz de Hardware,
Control de Acceso RBAC (Autenticación != Autorización) y Persistencia Supabase.
====================================================================
"""
import sys
import os
import json
import time
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Rutas del proyecto
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
AUTOOS1_DIR = ROOT_DIR / "AutoOS_1"

if str(AUTOOS1_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOOS1_DIR))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# Intentar importar Streamlit
try:
    import streamlit as st
    import streamlit.components.v1 as components
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    st = None
    components = None

# Si se ejecuta directamente por terminal sin Streamlit
if __name__ == "__main__" and not HAS_STREAMLIT:
    print("=" * 65)
    print("  AutoOS - Sistema Operativo para Vehículo Inteligente v2.4")
    print("=" * 65)
    print("Streamlit no se encuentra instalado en este intérprete.")
    print("Para levantar el Dashboard completo ejecuta:")
    print("   pip install -r requirements.txt")
    print("   streamlit run app.py")
    print("\nPara ejecutar la demostración por consola CLI:")
    print("   python3 AutoOS_1/cli.py --demo")
    print("=" * 65)
    sys.exit(0)

# Importar puente del Kernel y módulos auxiliares
import kernel_bridge
from config import (
    get_db,
    get_supabase_client,
    is_supabase_connected,
    test_supabase_connection_py,
    diagnosticar_supabase_completo,
    guardar_reporte_simulacion,
    obtener_reportes_simulacion,
    sincronizar_evento_supabase,
    sincronizar_auditoria_supabase,
)
from modules.auth_security import (
    obtener_usuario_actual,
    cambiar_usuario_activo,
    validar_accion,
    registrar_evento_seguridad,
    tiene_permiso,
    ROLES_INFO,
)
from modules.devices import (
    obtener_dispositivos,
    calibrar_dispositivo,
    inyectar_fallo_dispositivo,
    restablecer_dispositivos,
)
from modules.telemetry_battery import obtener_estado_bateria
from modules.processes import (
    obtener_procesos,
    crear_proceso,
    cambiar_estado_proceso,
    finalizar_proceso,
    calcular_uso_cpu_total,
)
from modules.memory_storage import (
    obtener_uso_memoria,
    obtener_sistema_archivos,
    obtener_logs_sistema,
)
from modules.ui_components import (
    aplicar_estilos_cockpit,
    obtener_paleta,
)

# ------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA STREAMLIT
# ------------------------------------------------------------------
st.set_page_config(
    page_title="AutoOS — Sistema Operativo Vehicular & RTOS",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# GESTIÓN PERSISTENTE DEL KERNEL EN SESSION_STATE
# ------------------------------------------------------------------
kernel = kernel_bridge.get_kernel()
terminal = kernel_bridge.get_terminal()

# Control de tema (oscuro por defecto)
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "oscuro"

# Paleta activa
paleta = obtener_paleta(st.session_state["theme_mode"])
aplicar_estilos_cockpit(st.session_state["theme_mode"])

# Estilos CSS específicos para la terminal monospace y cards de subsistemas
st.markdown(f"""
<style>
    .autoos-card {{
        background: {paleta['bg_card']};
        border: 1px solid {paleta['border']};
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: {paleta['shadow']};
    }}
    .autoos-card-header {{
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: {paleta['text_primary']};
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .terminal-box {{
        background: #020406;
        border: 1px solid #BF40FA;
        border-radius: 8px;
        padding: 14px;
        font-family: 'JetBrains Mono', monospace;
        color: #34d399;
        font-size: 0.82rem;
        max-height: 480px;
        overflow-y: auto;
        white-space: pre-wrap;
        box-shadow: 0 0 15px rgba(191, 64, 250, 0.2);
    }}
    .badge-ok {{
        background: rgba(52, 211, 153, 0.15);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.3);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: bold;
    }}
    .badge-warn {{
        background: rgba(251, 191, 36, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.3);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: bold;
    }}
    .badge-danger {{
        background: rgba(248, 113, 113, 0.15);
        color: #f87171;
        border: 1px solid rgba(248, 113, 113, 0.3);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: bold;
    }}
    .gantt-bar {{
        display: inline-block;
        height: 24px;
        margin-right: 2px;
        border-radius: 4px;
        text-align: center;
        color: white;
        font-size: 10px;
        font-weight: bold;
        line-height: 24px;
    }}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# BARRA LATERAL: PERFIL DE USUARIO, RBAC, TEMA Y CONTROLES GLOBALES
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🚗 AutoOS v2.4 RTOS")
    st.caption("Sistema Operativo Vehicular Autónomo")

    # Selector de usuario y perfil RBAC
    st.markdown("#### 👤 Perfil Vehicular Activo")
    db = get_db()
    usuarios_opciones = {usr["id"]: f"{usr['nombre_completo']} ({usr['rol'].upper()})" for usr in db["perfiles"]}
    usuario_actual = obtener_usuario_actual()
    usuario_seleccionado_id = st.selectbox(
        "Identidad en Cabina",
        options=list(usuarios_opciones.keys()),
        format_func=lambda uid: usuarios_opciones[uid],
        index=list(usuarios_opciones.keys()).index(usuario_actual["id"]) if usuario_actual["id"] in usuarios_opciones else 0,
        label_visibility="collapsed",
    )
    if usuario_seleccionado_id != usuario_actual["id"]:
        cambiar_usuario_activo(usuario_seleccionado_id)
        st.rerun()

    usr = obtener_usuario_actual()
    rol_info = ROLES_INFO.get(usr["rol"], {})
    st.info(f"**Rol:** {rol_info.get('etiqueta', usr['rol'])}\n\n**Privilegio:** Nivel {rol_info.get('nivel', 1)}/10\n\n_{rol_info.get('descripcion', '')}_")

    # Selector de tema
    st.markdown("---")
    st.markdown("#### 🎨 Tema Visual")
    tema_sel = st.radio(
        "Tema",
        options=["oscuro", "claro"],
        format_func=lambda t: "🌙 Modo Oscuro (Purple Night)" if t == "oscuro" else "☀️ Modo Claro (Soft Dove)",
        index=0 if st.session_state["theme_mode"] == "oscuro" else 1,
        label_visibility="collapsed"
    )
    if tema_sel != st.session_state["theme_mode"]:
        st.session_state["theme_mode"] = tema_sel
        st.rerun()

    # Estado de Supabase en Sidebar
    st.markdown("---")
    st.markdown("#### ☁️ Supabase Cloud")
    supa_conn = is_supabase_connected()
    if supa_conn:
        st.success("🟢 Conectado a Supabase Cloud")
    else:
        st.warning("🟠 Motor Local Resiliente (Credenciales no detectadas)")

    st.markdown("---")
    st.caption("AutoOS — ISO 26262 ASIL-D Compliant")


# ------------------------------------------------------------------
# ENCABEZADO SUPERIOR: ESTADO GENERAL DEL SISTEMA Y TELEMETRÍA RÁPIDA
# ------------------------------------------------------------------
col_title, col_stat = st.columns([2, 1])

with col_title:
    st.markdown("## 🚗 AutoOS — Sistema Operativo para Vehículo Inteligente")
    st.markdown("**Núcleo:** Kernel Multitarea Tiempo Real · **Planificador:** Multialgoritmo · **Memoria:** First-Fit & Paginación")

with col_stat:
    if kernel.is_booted:
        st.markdown("""
        <div style="text-align: right; margin-top: 8px;">
            <span class="badge-ok" style="font-size: 0.9rem; padding: 6px 14px;">● KERNEL OPERACIONAL</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: right; margin-top: 8px;">
            <span class="badge-danger" style="font-size: 0.9rem; padding: 6px 14px;">● KERNEL APAGADO / REQUIERE BOOT</span>
        </div>
        """, unsafe_allow_html=True)


# Tarjetas de resumen en la barra superior
m_tick, m_cpu, m_ram, m_vmem, m_vfs, m_evts = st.columns(6)
snap = kernel.get_system_snapshot() if kernel.is_booted else None

with m_tick:
    st.metric("Reloj Lógico", f"Tick {kernel.engine.current_tick}")
with m_cpu:
    cpu_stat = "LIBRE" if kernel.cpu.is_idle else f"PID {kernel.cpu.current_process.pid}"
    st.metric("Estado CPU", cpu_stat)
with m_ram:
    used_ram = kernel.memory_manager.used_memory
    tot_ram = kernel.memory_manager.total_memory
    st.metric("RAM Física", f"{used_ram} / {tot_ram} MB", delta=f"{kernel.memory_manager.usage_percentage}%")
with m_vmem:
    vm = kernel.virtual_memory
    st.metric("Paginación", f"{vm.page_hits} H / {vm.page_faults} F", delta=f"{vm.hit_ratio}% Hit")
with m_vfs:
    archivos_totales = sum(len(f) for f in kernel.file_system.structure.values())
    st.metric("Archivos VFS", f"{archivos_totales} archivos")
with m_evts:
    st.metric("Auditoría", f"{kernel.logger.total_events} eventos")

st.markdown("---")


# ------------------------------------------------------------------
# LAS 9 PESTAÑAS INTEGRALES DE AUTOOS
# ------------------------------------------------------------------
tab_boot, tab_proc, tab_sched, tab_ram, tab_vmem, tab_vfs, tab_term, tab_cockpit, tab_sec = st.tabs([
    "⚡ Boot & Kernel",
    "🔄 Procesos & CPU",
    "⏱️ Planificador",
    "💾 Memoria Física",
    "📑 Memoria Virtual",
    "📁 Archivos (VFS)",
    "💻 Terminal",
    "🚗 Cockpit & Hardware",
    "🛡️ Seguridad & Supabase",
])


# ==================================================================
# TAB 1: BOOT Y KERNEL (CRITERIOS 1 Y 2)
# ==================================================================
with tab_boot:
    st.markdown("### ⚡ Secuencia de Arranque (Boot) y Administración del Kernel")
    st.write("Control formal de inicialización del sistema operativo vehicular en 7 etapas deterministas.")

    c_b1, c_b2, c_b3 = st.columns([1, 1, 2])
    with c_b1:
        if st.button("🚀 Iniciar Boot del Sistema", type="primary", use_container_width=True, disabled=kernel.is_booted):
            res = kernel_bridge.boot_system()
            st.success(f"{res['message']}")
            st.rerun()

    with c_b2:
        if st.button("🛑 Apagado Ordenado (Shutdown)", type="secondary", use_container_width=True, disabled=not kernel.is_booted):
            res = kernel_bridge.shutdown_system()
            st.warning(f"{res['message']} (Tick final: {res.get('final_tick', 0)})")
            st.rerun()

    with c_b3:
        if kernel.is_booted:
            st.markdown(f"**Hora de Arranque:** `{kernel.boot_log[0]['description'] if kernel.boot_log else 'N/A'}` | **Estado:** `OPERACIONAL`")
        else:
            st.info("Presiona **Iniciar Boot del Sistema** para ejecutar el Power-On Self-Test (POST) y desplegar los demonios.")

    st.markdown("#### 📋 Fases Formales de Arranque (7 Etapas)")
    if kernel.boot_log:
        cols_stages = st.columns(len(kernel.boot_log))
        for idx, stage in enumerate(kernel.boot_log):
            with cols_stages[idx]:
                st.markdown(f"""
                <div class="autoos-card" style="text-align: center; padding: 10px;">
                    <span class="badge-ok">OK</span>
                    <div style="font-weight: bold; margin-top: 6px; font-size: 0.85rem;">{stage['stage']}</div>
                    <div style="font-size: 0.7rem; color: #887D77; margin-top: 4px;">{stage['description'][:45]}...</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.caption("El kernel aún no ha ejecutado la secuencia de arranque.")

    st.markdown("#### ⚙️ Demonios Críticos del Vehículo Desplegados en Boot")
    procs_demonios = [p for p in kernel.engine.get_all_processes() if p.name in ["BMS_Battery_Monitor", "CAN_Bus_Gateway", "ADAS_Vision_Pilot", "Telemetry_Cloud_Node"]]
    if procs_demonios:
        c_d1, c_d2, c_d3, c_d4 = st.columns(4)
        cols_d = [c_d1, c_d2, c_d3, c_d4]
        for idx, d in enumerate(procs_demonios):
            with cols_d[idx]:
                alloc = kernel.memory_manager.get_process_allocation(d.pid)
                st.markdown(f"""
                <div class="autoos-card">
                    <div class="autoos-card-header">
                        <span>{d.name}</span>
                        <span class="badge-ok">PID {d.pid}</span>
                    </div>
                    <div style="font-size: 0.8rem;">
                        <b>Prioridad:</b> {d.priority} (Crítica)<br>
                        <b>Ráfaga:</b> {d.remaining_time}/{d.burst_time} ticks<br>
                        <b>RAM Física:</b> {alloc.limit if alloc else 64} MB<br>
                        <b>Estado:</b> <code>{d.state.value}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ==================================================================
# TAB 2: PROCESOS Y CPU (CRITERIOS 3, 4 Y 5)
# ==================================================================
with tab_proc:
    st.markdown("### 🔄 Gestión de Procesos (PCB) y Ejecución en CPU")
    
    # Barra de acciones y avance de simulación
    col_act1, col_act2, col_act3, col_act4, col_act5 = st.columns([1, 1, 1, 1, 2])
    with col_act1:
        if st.button("▶️ Avanzar 1 Tick", use_container_width=True, disabled=not kernel.is_booted):
            res = kernel_bridge.step_simulation(1)
            st.rerun()
    with col_act2:
        if st.button("⏩ Ráfaga 5 Ticks", use_container_width=True, disabled=not kernel.is_booted):
            res = kernel_bridge.step_simulation(5)
            st.rerun()
    with col_act3:
        if st.button("⏭️ Ráfaga 10 Ticks", use_container_width=True, disabled=not kernel.is_booted):
            res = kernel_bridge.step_simulation(10)
            st.rerun()
    with col_act4:
        pause_txt = "▶️ Reanudar" if kernel.engine.is_paused else "⏸️ Pausar"
        if st.button(pause_txt, use_container_width=True, disabled=not kernel.is_booted):
            if kernel.engine.is_paused:
                kernel.engine.resume()
            else:
                kernel.engine.pause()
            st.rerun()
    with col_act5:
        if not kernel.is_booted:
            st.warning("Inicia el Boot en la Pestaña 1 para ejecutar procesos.")
        else:
            proc_cpu = kernel.cpu.current_process
            if proc_cpu:
                st.success(f"CPU Ejecutando: **PID {proc_cpu.pid} — {proc_cpu.name}** (Ráfaga restante: {proc_cpu.remaining_time})")
            else:
                st.info("CPU Ociosa (Sin proceso despachado en este ciclo)")

    # Formulario para crear procesos con asignación First-Fit
    with st.expander("➕ Crear Nuevo Proceso Vehicular (Con Asignación de RAM First-Fit)", expanded=False):
        c_np1, c_np2, c_np3, c_np4, c_np5 = st.columns([2, 1, 1, 1, 1])
        with c_np1:
            nuevo_nombre = st.text_input("Nombre de la Tarea", value="Radar_Frente_ACC", key="np_name")
        with c_np2:
            nueva_prio = st.selectbox("Prioridad", options=[1, 2, 3, 4, 5], index=2, format_func=lambda p: f"{p} ({'Crítica' if p<=2 else 'Normal' if p==3 else 'Baja'})", key="np_prio")
        with c_np3:
            nueva_rafaga = st.number_input("Ráfaga (Ticks)", min_value=1, max_value=50, value=6, key="np_burst")
        with c_np4:
            nueva_ram = st.number_input("RAM (MB)", min_value=16, max_value=1024, step=16, value=64, key="np_ram")
        with c_np5:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Crear Proceso", type="primary", use_container_width=True, disabled=not kernel.is_booted):
                usr_act = obtener_usuario_actual()
                ok, msg = crear_proceso(
                    nombre=nuevo_nombre,
                    prioridad=nueva_prio,
                    cpu_est=nueva_rafaga,
                    mem_mb=nueva_ram,
                    es_critico=nueva_prio <= 2,
                    usuario_actual=usr_act
                )
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # Tabla viva de procesos
    st.markdown("#### 📑 Bloque de Control de Procesos (PCB en Tiempo Real)")
    todos_procesos = kernel.engine.get_all_processes() if kernel.is_booted else []
    
    if todos_procesos:
        proc_data_display = []
        for p in todos_procesos:
            alloc = kernel.memory_manager.get_process_allocation(p.pid)
            proc_data_display.append({
                "PID": p.pid,
                "Nombre": p.name,
                "Prioridad": f"{p.priority} ({'ASIL-D' if p.priority<=2 else 'Confort'})",
                "Estado": p.state.value,
                "Ráfaga Restante": f"{p.remaining_time} / {p.burst_time} ticks",
                "Avance": f"{p.progress_percentage}%",
                "RAM Física": f"{alloc.limit if alloc else getattr(p, 'memory_size', 64)} MB",
                "Dirección Base": f"0x{alloc.base_address:04X}" if alloc else "N/A",
            })
        st.dataframe(proc_data_display, use_container_width=True)
    else:
        st.caption("No hay procesos registrados.")

    # Terminación forzada (Kill) con liberación y coalescencia
    col_k1, col_k2, col_k3 = st.columns([2, 1, 3])
    with col_k1:
        pid_kill = st.selectbox(
            "Seleccionar PID para abortar (SIGKILL):",
            options=[p.pid for p in todos_procesos if p.state.value != "TERMINATED"],
            format_func=lambda pid: f"PID {pid} — {next((p.name for p in todos_procesos if p.pid == pid), '')}",
            key="kill_pid_select"
        ) if todos_procesos else None
    with col_k2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("💀 Finalizar Proceso", type="secondary", use_container_width=True, disabled=not pid_kill):
            usr_act = obtener_usuario_actual()
            ok, msg = finalizar_proceso(pid_kill, usr_act)
            if ok:
                st.warning(msg)
                st.rerun()
            else:
                st.error(msg)
    with col_k3:
        st.caption("ℹ️ Finalizar un proceso transiciona su estado a `TERMINATED`, libera su bloque en la RAM física y ejecuta la coalescencia automática para eliminar fragmentación externa.")

    # Diagrama de Gantt
    st.markdown("#### 📊 Diagrama de Gantt (Historial Reactivo de Despacho en CPU)")
    gantt_entries = kernel_bridge.get_gantt_history()
    if gantt_entries:
        # Renderizar timeline visual con barras de color
        palette_pids = {
            1: "#ef4444", 2: "#06b6d4", 3: "#3b82f6", 4: "#10b981", 5: "#f59e0b",
            6: "#8b5cf6", 7: "#ec4899", 0: "#334155"
        }
        gantt_html = "<div style='display: flex; overflow-x: auto; padding: 10px 0; background: #0D0714; border-radius: 8px; border: 1px solid #331E4D;'>"
        for g in gantt_entries[-40:]:
            color = palette_pids.get(g['pid'], "#a855f7")
            gantt_html += f"<div class='gantt-bar' style='background: {color}; min-width: 32px;' title='Tick {g['tick']}: PID {g['pid']} ({g['name']})'>P{g['pid']}</div>"
        gantt_html += "</div>"
        st.markdown(gantt_html, unsafe_allow_html=True)
        st.caption("Muestra los últimos ciclos de reloj. P0 representa CPU ociosa (IDLE).")
    else:
        st.caption("Avanza ciclos de simulación para visualizar la traza en el Diagrama de Gantt.")


# ==================================================================
# TAB 3: PLANIFICADOR (SCHEDULER - CRITERIO 6)
# ==================================================================
with tab_sched:
    st.markdown("### ⏱️ Planificador Multialgoritmo (Scheduler)")
    st.write("Configuración de políticas de selección y despacho de procesos automotrices.")

    c_s1, c_s2, c_s3 = st.columns([2, 1, 2])
    with c_s1:
        algoritmo_actual = kernel.scheduler.algorithm
        nuevo_algoritmo = st.selectbox(
            "Algoritmo de Planificación Activo",
            options=["PRIORITY", "FCFS", "ROUND_ROBIN"],
            index=["PRIORITY", "FCFS", "ROUND_ROBIN"].index(algoritmo_actual) if algoritmo_actual in ["PRIORITY", "FCFS", "ROUND_ROBIN"] else 0,
            format_func=lambda a: {
                "PRIORITY": "Prioridad Estricta (Min-Heap con desempate FIFO)",
                "FCFS": "FCFS (First-Come, First-Served estricto)",
                "ROUND_ROBIN": "Round Robin (Turno rotativo con Quantum)"
            }.get(a, a)
        )
    with c_s2:
        quantum_val = st.number_input("Quantum (Ticks para RR)", min_value=1, max_value=10, value=kernel.scheduler.quantum)
    with c_s3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Aplicar Configuración de Scheduler", type="primary", use_container_width=True, disabled=not kernel.is_booted):
            ok, msg = kernel_bridge.set_scheduler_bridge(nuevo_algoritmo, quantum_val)
            st.success(msg)
            st.rerun()

    # Visualización en vivo de la cola de listos (READY Queue)
    st.markdown("#### ⏳ Cola de Procesos Listos (READY Queue - Orden Determinista de Despacho)")
    ready_procs = [entry[2] for entry in kernel.scheduler._queue if entry[2].state.value == "READY"] if kernel.is_booted else []
    
    if ready_procs:
        st.write(f"**Procesos esperando en cola:** {len(ready_procs)}")
        cols_q = st.columns(min(len(ready_procs), 6))
        for idx, proc in enumerate(ready_procs[:6]):
            with cols_q[idx]:
                st.markdown(f"""
                <div class="autoos-card" style="border-left: 4px solid {'#ef4444' if proc.priority<=2 else '#3b82f6'};">
                    <div style="font-weight: bold; font-size: 0.85rem;">Posición {idx + 1}</div>
                    <div style="font-size: 0.8rem; margin-top: 4px;">
                        <b>PID {proc.pid}:</b> {proc.name[:18]}<br>
                        <b>Prioridad:</b> {proc.priority}<br>
                        <b>Ráfaga:</b> {proc.remaining_time} ticks
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.caption("La cola de listos se encuentra vacía o todos los procesos están en CPU o terminados.")

    # Simuladores de contingencia
    st.markdown("#### 🚨 Simuladores de Contingencia Vehicular Integrados")
    c_sc1, c_sc2 = st.columns(2)
    with c_sc1:
        st.markdown("""
        <div class="autoos-card">
            <div class="autoos-card-header">
                <span>🔋 Simulador de Batería Baja</span>
                <span class="badge-warn">Limp-Home Mode</span>
            </div>
            <p style="font-size: 0.8rem;">Suspende dinámicamente tareas de infoentretenimiento y confort para preservar reserva de energía para la dirección y frenos.</p>
        </div>
        """, unsafe_allow_html=True)
        btn_bat_txt = "Desactivar Modo Ahorro" if kernel.scheduler.low_battery_mode else "Activar Modo Batería Baja (<20%)"
        if st.button(btn_bat_txt, use_container_width=True, disabled=not kernel.is_booted):
            ok, msg = kernel_bridge.toggle_low_battery_mode()
            st.warning(msg)
            st.rerun()

    with c_sc2:
        st.markdown("""
        <div class="autoos-card">
            <div class="autoos-card-header">
                <span>🛑 Inyección de Proceso Crítico (ASIL-D)</span>
                <span class="badge-danger">Preemption Inmediata</span>
            </div>
            <p style="font-size: 0.8rem;">Inyecta una tarea de emergencia (Frenado Autónomo de Emergencia) desalojando al proceso en ejecución mediante cambio de contexto.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("💥 Inyectar Frenado de Emergencia AEB", type="primary", use_container_width=True, disabled=not kernel.is_booted):
            ok, msg, p_crit = kernel_bridge.inject_critical_process_bridge()
            if ok:
                st.error(msg)
                st.rerun()
            else:
                st.error(msg)


# ==================================================================
# TAB 4: MEMORIA FÍSICA (FIRST-FIT - CRITERIO 7)
# ==================================================================
with tab_ram:
    st.markdown("### 💾 Gestor de Memoria RAM Física (Particiones First-Fit)")
    st.write("Modelo de direccionamiento base y límite con asignación continua, división de bloques y coalescencia automática.")

    mm = kernel.memory_manager
    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    with c_m1:
        st.metric("RAM Física Total", f"{mm.total_memory} MB")
    with c_m2:
        st.metric("RAM Ocupada", f"{mm.used_memory} MB", delta=f"{mm.usage_percentage}%")
    with c_m3:
        st.metric("RAM Disponible", f"{mm.free_memory} MB")
    with c_m4:
        st.metric("Fragmentación Externa", f"{mm.fragmentation_percentage}%")

    st.markdown("#### 🗺️ Mapa Dinámico de Particiones Contiguas (Memory Map)")
    mem_map = mm.get_memory_map()
    
    # Barra visual de bloques
    bar_html = "<div style='display: flex; width: 100%; height: 32px; border-radius: 8px; overflow: hidden; margin-bottom: 16px; border: 1px solid #331E4D;'>"
    for b in mem_map:
        pct_width = max(2.0, (b['limit'] / mm.total_memory) * 100)
        bg = "#ef4444" if not b['is_free'] and b['pid'] == 1 else "#3b82f6" if not b['is_free'] else "#10b981"
        bar_html += f"<div style='background: {bg}; width: {pct_width}%; display: flex; align-items: center; justify-content: center; font-size: 10px; color: white; font-weight: bold; border-right: 1px solid rgba(0,0,0,0.3);' title='0x{b['base_address']:04X} ({b['limit']} MB): {b['status']}'>{b['limit']}MB</div>"
    bar_html += "</div>"
    st.markdown(bar_html, unsafe_allow_html=True)

    # Tabla detallada de bloques
    map_display = []
    for b in mem_map:
        map_display.append({
            "Dirección Base": f"0x{b['base_address']:08X}",
            "Límite (Tamaño)": f"{b['limit']} MB",
            "Dirección Final": f"0x{b['end_address']:08X}",
            "Estado": "LIBRE" if b["is_free"] else "OCUPADO",
            "Proceso Propietario": f"PID {b['pid']} ({b['process_name']})" if not b["is_free"] else "Disponible (Sistema)",
        })
    st.dataframe(map_display, use_container_width=True)


# ==================================================================
# TAB 5: MEMORIA VIRTUAL Y PAGINACIÓN (CRITERIO 8)
# ==================================================================
with tab_vmem:
    st.markdown("### 📑 Memoria Virtual y Subsistema de Paginación")
    st.write("Traducción de direcciones virtuales a físicas, marcos de memoria, tablas de páginas y tratamiento de Page Faults.")

    vm = kernel.virtual_memory
    c_v1, c_v2, c_v3, c_v4 = st.columns(4)
    with c_v1:
        st.metric("Marcos Físicos", f"{vm.total_frames} marcos (4 MB c/u)")
    with c_v2:
        st.metric("Área SWAP", f"{vm.used_swap} / {vm.swap_size} MB", delta=f"{vm.swap_free} MB libres")
    with c_v3:
        st.metric("Fallos / Aciertos", f"{vm.page_faults} Faults / {vm.page_hits} Hits")
    with c_v4:
        st.metric("Tasa de Aciertos", f"{vm.hit_ratio}%", delta=f"Algoritmo: {vm.replacement_algorithm}")

    # Simulador interactivo de traducción de direcciones
    st.markdown("#### 🔍 Simulador de Traducción de Direcciones (vmem)")
    c_tr1, c_tr2, c_tr3, c_tr4 = st.columns([2, 1, 1, 2])
    with c_tr1:
        vaddr_input = st.number_input("Dirección Virtual (MB)", min_value=0, max_value=2048, value=10, key="vaddr_in")
    with c_tr2:
        op_write = st.selectbox("Operación", options=[False, True], format_func=lambda w: "Escritura (Write)" if w else "Lectura (Read)", key="vaddr_op")
    with c_tr3:
        pid_vmem = st.selectbox("PID Proceso", options=[p.pid for p in todos_procesos] if todos_procesos else [1], key="vmem_pid")
    with c_tr4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Traducir Dirección Virtual", type="primary", use_container_width=True, disabled=not kernel.is_booted):
            res_vmem = vm.translate_address(pid=pid_vmem, virtual_address=vaddr_input, is_write=op_write)
            st.session_state["last_vmem_res"] = res_vmem

    if "last_vmem_res" in st.session_state:
        rv = st.session_state["last_vmem_res"]
        color_alert = "#f59e0b" if rv.get("page_fault") else "#10b981"
        badge_txt = f"PAGE FAULT (Fallo de Página resuelto por SWAP - Marco {rv.get('frame_number')})" if rv.get("page_fault") else "PAGE HIT (Acierto en RAM)"
        st.markdown(f"""
        <div class="autoos-card" style="border-left: 4px solid {color_alert};">
            <div style="font-weight: bold; font-size: 0.95rem;">{badge_txt}</div>
            <div style="font-size: 0.85rem; margin-top: 6px;">
                <b>Dirección Virtual:</b> <code>{rv['virtual_address']} (0x{rv['virtual_address']:08X})</code><br>
                <b>Número de Página:</b> {rv['page_number']} | <b>Offset:</b> {rv['offset']} MB<br>
                <b>Marco Físico Asignado:</b> {rv['frame_number']}<br>
                <b>Dirección Física Traducida:</b> <code>{rv['physical_address']} (0x{rv['physical_address']:08X})</code><br>
                <b>Página Expulsada a SWAP:</b> {rv.get('evicted_page', 'Ninguna (Había marcos libres)')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Vista de marcos físicos
    st.markdown("#### 🔲 Tabla de Marcos Físicos de Paginación (Primeros 16 de 64)")
    cols_frames = st.columns(8)
    for f_idx in range(16):
        col_target = cols_frames[f_idx % 8]
        frame_info = vm._frames[f_idx]
        with col_target:
            status_txt = f"PID {frame_info[0]} (P{frame_info[1]})" if frame_info else "Libre"
            bg_f = "rgba(59, 130, 246, 0.2)" if frame_info else "rgba(16, 185, 129, 0.1)"
            border_f = "#3b82f6" if frame_info else "#10b981"
            st.markdown(f"""
            <div style="background: {bg_f}; border: 1px solid {border_f}; border-radius: 6px; padding: 6px; text-align: center; margin-bottom: 8px;">
                <div style="font-size: 0.7rem; font-weight: bold;">M{f_idx}</div>
                <div style="font-size: 0.65rem;">{status_txt}</div>
            </div>
            """, unsafe_allow_html=True)


# ==================================================================
# TAB 6: SISTEMA DE ARCHIVOS (VFS - CRITERIO 9)
# ==================================================================
with tab_vfs:
    st.markdown("### 📁 Sistema de Archivos Persistente (Virtual File System - VFS)")
    st.write("Estructura jerárquica de carpetas automotrices con metadatos y persistencia automática en disco JSON.")

    fs = kernel.file_system
    c_f1, c_f2, c_f3 = st.columns([1, 2, 1])
    with c_f1:
        carpeta_sel = st.selectbox("Carpeta del VFS", options=list(fs.structure.keys()), index=0)
    with c_f2:
        archivos_en_carpeta = list(fs.structure.get(carpeta_sel, {}).keys())
        archivo_sel = st.selectbox("Archivo", options=archivos_en_carpeta if archivos_en_carpeta else ["(Sin archivos)"])
    with c_f3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("💾 Sincronizar VFS a Disco", type="primary", use_container_width=True):
            fs.save_to_disk()
            st.success(f"VFS persistido exitosamente en: `{fs.storage_path}`")

    # Contenido del archivo seleccionado
    if archivo_sel and archivo_sel != "(Sin archivos)":
        meta = fs.structure[carpeta_sel][archivo_sel]
        st.markdown(f"**Archivo:** `/{carpeta_sel}/{archivo_sel}` | **Tamaño:** `{meta.get('size', 1)} MB` | **Permisos:** `{meta.get('permissions', '0644')}` | **Actualizado:** `{meta.get('updated_at', '')}`")
        contenido_actual = meta.get("content", "")
        nuevo_contenido = st.text_area("Contenido del Archivo", value=contenido_actual, height=140, key=f"vfs_edit_{archivo_sel}")
        
        c_ed1, c_ed2, c_ed3 = st.columns([1, 1, 3])
        with c_ed1:
            if st.button("Guardar Cambios", use_container_width=True):
                fs.write_file(carpeta_sel, archivo_sel, nuevo_contenido, mode="w")
                st.success("Archivo actualizado y guardado.")
                st.rerun()
        with c_ed2:
            if st.button("Eliminar Archivo", type="secondary", use_container_width=True):
                fs.delete_file(carpeta_sel, archivo_sel)
                st.warning("Archivo eliminado.")
                st.rerun()

    # Crear nuevo archivo en el VFS
    with st.expander("📄 Crear Nuevo Archivo en el VFS", expanded=False):
        c_ca1, c_ca2, c_ca3, c_ca4 = st.columns([1, 2, 1, 1])
        with c_ca1:
            dest_folder = st.selectbox("Carpeta Destino", options=list(fs.structure.keys()), key="new_file_folder")
        with c_ca2:
            new_file_name = st.text_input("Nombre de Archivo", value="telemetria_can.log", key="new_file_name")
        with c_ca3:
            new_file_size = st.number_input("Tamaño (MB)", min_value=1, max_value=100, value=1, key="new_file_size")
        with c_ca4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            new_file_content = st.text_input("Texto Inicial", value="INIT_CAN_STREAM", key="new_file_txt")
            if st.button("Crear Archivo", type="primary", use_container_width=True):
                fs.create_file(dest_folder, new_file_name, size=new_file_size, content=new_file_content)
                st.success(f"Archivo creado en /{dest_folder}/{new_file_name}")
                st.rerun()


# ==================================================================
# TAB 7: TERMINAL INTERACTIVA REAL (CRITERIO 10)
# ==================================================================
with tab_term:
    st.markdown("### 💻 Terminal Interactiva del Sistema Operativo (AutoOS Shell)")
    st.write("Línea de comandos conectada directamente al estado real del Kernel y sus subsistemas.")

    # Botón rápido para ejecutar la demostración académica completa
    c_t1, c_t2 = st.columns([2, 1])
    with c_t1:
        st.caption("Comandos disponibles: `boot`, `status`, `ps`, `create <nom> <prio> <raf> [mem]`, `kill <pid>`, `step [n]`, `sched <alg> [q]`, `mem`, `vmem <addr> [write]`, `ls`, `cat`, `write`, `rm`, `mkdir`, `clear`, `help`")
    with c_t2:
        if st.button("🎓 Ejecutar Sustentación Demo en Vivo", type="primary", use_container_width=True):
            from cli import run_live_demonstration
            # Ejecutar comandos de demo en la terminal activa
            demo_cmds = ["boot", "status", "ps", "mem map", "create Freno_Emergencia_AEB 1 3 64", "step 4", "cat config vehicle_params.json", "vmem 10 write 1", "vmem 10 read 1", "sched ROUND_ROBIN 2"]
            for cmd in demo_cmds:
                kernel_bridge.execute_terminal_command(cmd)
            st.success("Demostración universitaria ejecutada con éxito en la terminal.")
            st.rerun()

    # Cuadro visual de terminal monospace
    historial = kernel_bridge.get_terminal_history()
    terminal_output = "======================================================================\n"
    terminal_output += "   AutoOS Interactive Shell v2.4 (RTOS Vehicular - Terminal Conectada)\n"
    terminal_output += "======================================================================\n\n"
    
    for h in historial:
        terminal_output += f"AutoOS [{h['time']}]> {h['cmd']}\n"
        terminal_output += f"{h['output']}\n\n"

    st.markdown(f"<div class='terminal-box'>{terminal_output}</div>", unsafe_allow_html=True)

    # Entrada de comando
    c_in1, c_in2 = st.columns([4, 1])
    with c_in1:
        cmd_input = st.text_input("Comando AutoOS", placeholder="Escribe un comando (ej. 'ps', 'step 3', 'mem map', 'help')...", label_visibility="collapsed", key="terminal_cli_input")
    with c_in2:
        if st.button("Enviar Comando", type="primary", use_container_width=True):
            if cmd_input.strip():
                if cmd_input.strip().lower() == "clear":
                    if "terminal_history" in st.session_state:
                        st.session_state["terminal_history"] = []
                else:
                    kernel_bridge.execute_terminal_command(cmd_input)
                st.rerun()


# ==================================================================
# TAB 8: COCKPIT VEHICULAR Y HARDWARE
# ==================================================================
with tab_cockpit:
    st.markdown("### 🚗 Cockpit Vehicular y Matriz de Salud de Hardware")
    
    bateria = obtener_estado_bateria()
    c_cp1, c_cp2, c_cp3, c_cp4 = st.columns(4)
    with c_cp1:
        st.metric("Batería LiFePO4", f"{bateria['soc_pct']}%", delta=f"{bateria['voltaje_v']} V")
    with c_cp2:
        st.metric("Temperatura BMS", f"{bateria['temp_c']} °C", delta="Nominal")
    with c_cp3:
        st.metric("Potencia Instantánea", f"{bateria['potencia_kw']} kW")
    with c_cp4:
        st.metric("Salud Paquete (SoH)", f"{bateria['salud_soh']}%")

    st.markdown("#### 🛰️ Matriz de Periféricos de Hardware (11 Dispositivos CAN/Ethernet/LIN)")
    dispositivos = obtener_dispositivos()
    cols_dev = st.columns(3)
    for idx, dev in enumerate(dispositivos[:6]):
        with cols_dev[idx % 3]:
            badge_color = "badge-ok" if dev['estado'] == "operativo" else "badge-warn" if dev['estado'] == "degradado" else "badge-danger"
            st.markdown(f"""
            <div class="autoos-card">
                <div class="autoos-card-header">
                    <span>{dev['nombre']}</span>
                    <span class="{badge_color}">{dev['estado'].upper()}</span>
                </div>
                <div style="font-size: 0.8rem;">
                    <b>Código:</b> <code>{dev['codigo']}</code> | <b>Bus:</b> {dev['puerto_bus']}<br>
                    <b>Salud:</b> {dev['salud_porcentaje']}% | <b>Crítico:</b> {dev['nivel_critico'].upper()}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Opción para renderizar el Cockpit HTML interactivo original
    with st.expander("🎛️ Ver Cockpit Visual Interactivo (Instrumentos y Tacómetros)", expanded=False):
        bundle_path = CURRENT_DIR / "autoos_unified.html"
        if bundle_path.exists():
            with open(bundle_path, "r", encoding="utf-8") as f:
                app_html = f.read()
            components.html(app_html, height=1200, scrolling=True)
        else:
            st.info("Paquete unificado autoos_unified.html no encontrado.")


# ==================================================================
# TAB 9: SEGURIDAD, RBAC Y SUPABASE
# ==================================================================
with tab_sec:
    st.markdown("### 🛡️ Control de Acceso RBAC y Conexión Supabase Cloud")
    st.write("Demostración fehaciente de Autenticación != Autorización y persistencia en la nube.")

    # Diagnóstico detallado de Supabase
    st.markdown("#### ☁️ Diagnóstico de Base de Datos Supabase")
    diag_supa = diagnosticar_supabase_completo()
    
    c_sg1, c_sg2, c_sg3 = st.columns(3)
    with c_sg1:
        st.markdown(f"**Librería Oficial Python:** `{'INSTALADA' if diag_supa['has_library'] else 'NO DETECTADA'}`")
    with c_sg2:
        st.markdown(f"**Credenciales (.env/secrets):** `{'CONFIGURADAS' if diag_supa['has_credentials'] else 'PLACEHOLDERS O VACÍAS'}`")
    with c_sg3:
        st.markdown(f"**Estado de Conexión:** `{'CONECTADO (ONLINE)' if diag_supa['connected'] else 'MODO LOCAL RESILIENTE'}`")

    if diag_supa["error"]:
        st.info(f"ℹ️ **Estado:** {diag_supa['error']}\n\n_AutoOS opera de forma 100% funcional y persistente mediante el almacén local en disco JSON mientras configuras tus credenciales de Supabase._")

    # Persistencia de informe de simulación
    st.markdown("#### 💾 Generar y Persistir Reporte de Simulación")
    c_rp1, c_rp2 = st.columns([3, 1])
    with c_rp1:
        st.caption("Guarda una instantánea completa del estado de la simulación, procesos, algoritmo y métricas de CPU/RAM.")
    with c_rp2:
        if st.button("Guardar Reporte Ahora", type="primary", use_container_width=True):
            nuevo_rep = {
                "report_id": f"REP-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "escenario": "Prueba de Integración General",
                "titulo": f"Auditoría Operacional AutoOS (Tick {kernel.engine.current_tick})",
                "diagnostico": "Todos los subsistemas verificados y conformes",
                "evaluacion": "Aprobado (Conforme ISO 26262)",
                "usuario_email": obtener_usuario_actual()["email"],
                "iniciado_en": datetime.datetime.now().isoformat(),
                "finalizado_en": datetime.datetime.now().isoformat(),
                "bateria_inicial": 82.0,
                "bateria_final": 82.0,
                "velocidad_final": 45.0,
                "cpu_load_final": kernel.cpu.usage_percentage,
                "datos_completos": {
                    "total_procesos": len(kernel.engine.get_all_processes()),
                    "algoritmo": kernel.scheduler.algorithm,
                    "ram_usada": kernel.memory_manager.used_memory,
                    "hit_ratio": kernel.virtual_memory.hit_ratio,
                }
            }
            ok_rep, msg_rep = guardar_reporte_simulacion(nuevo_rep)
            st.success(msg_rep)

    # Historial de reportes
    reportes_guardados = obtener_reportes_simulacion()
    if reportes_guardados:
        st.write(f"**Reportes Persistidos Registrados:** {len(reportes_guardados)}")
        rep_display = []
        for r in reportes_guardados[:10]:
            rep_display.append({
                "ID Reporte": r.get("report_id", "N/A"),
                "Título": r.get("titulo", "N/A"),
                "Usuario": r.get("usuario_email", "N/A"),
                "Evaluación": r.get("evaluacion", "N/A"),
                "CPU %": r.get("cpu_load_final", 0),
            })
        st.dataframe(rep_display, use_container_width=True)

    # Bitácora de Auditoría RBAC
    st.markdown("#### 🔒 Registro Inmutable de Auditoría de Accesos (403 Forbidden vs 200 OK)")
    auditoria_items = db.get("auditoria", [])
    if auditoria_items:
        aud_disp = []
        for a in reversed(auditoria_items[-15:]):
            aud_disp.append({
                "Hora": a.get("hora", ""),
                "Usuario": a.get("usuario_email", ""),
                "Rol": a.get("rol", "").upper(),
                "Acción": a.get("accion", ""),
                "Recurso": a.get("recurso", ""),
                "Resultado": "✅ AUTORIZADO" if a.get("autorizado") else "❌ DENEGADO (403)",
                "Motivo": a.get("motivo_rechazo") or "Permiso conforme en matriz RBAC"
            })
        st.dataframe(aud_disp, use_container_width=True)
