"""
====================================================================
AUTOOS - PUENTE DE INTEGRACIÓN DEL KERNEL Y STREAMLIT (KERNEL BRIDGE)
====================================================================
Centraliza y conecta el motor central de AutoOS_1 con el Dashboard
de Streamlit, garantizando una única instancia persistente en
st.session_state y sincronización reactiva de todos los subsistemas.
====================================================================
"""
import sys
import os
import time
import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple

# Asegurar que AutoOS_1 esté en el PYTHONPATH
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
AUTOOS1_DIR = ROOT_DIR / "AutoOS_1"

if str(AUTOOS1_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOOS1_DIR))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from src.core.kernel import Kernel
    from src.core.terminal import Terminal, TerminalResponse
    from src.core.process_state import ProcessState
    from src.core.scheduler import AlgorithmType
    from src.core.exceptions import AutoOSError, InsufficientMemoryError
except ImportError as err:
    raise ImportError(f"No se pudo cargar el motor central AutoOS_1: {err}")

# Intento de importar Streamlit (permite usar el puente tanto en UI como en scripts de prueba)
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    st = None


# Instancia de respaldo para contextos sin Streamlit (ej. pruebas automatizadas)
_FALLBACK_KERNEL: Optional[Kernel] = None
_FALLBACK_TERMINAL: Optional[Terminal] = None
_FALLBACK_GANTT: List[Dict[str, Any]] = []
_FALLBACK_TERMINAL_HIST: List[Dict[str, Any]] = []


def get_kernel(memory_mb: int = 2048, swap_mb: int = 4096) -> Kernel:
    """
    Retorna la instancia única y persistente del Kernel de AutoOS.
    En Streamlit, se conserva en st.session_state para sobrevivir a los reruns.
    """
    global _FALLBACK_KERNEL, _FALLBACK_TERMINAL

    if HAS_STREAMLIT and st is not None:
        if "autoos_kernel" not in st.session_state:
            # Archivo de persistencia de VFS en la raíz de Auto
            vfs_file = str(CURRENT_DIR / "autoos_vfs_storage.json")
            kernel_instance = Kernel(
                memory_mb=memory_mb,
                swap_mb=swap_mb,
                vfs_path=vfs_file,
                scheduler_algorithm=AlgorithmType.PRIORITY,
            )
            st.session_state["autoos_kernel"] = kernel_instance
            st.session_state["autoos_terminal"] = Terminal(kernel=kernel_instance)
            st.session_state["terminal_history"] = [
                {
                    "cmd": "help",
                    "output": "Bienvenido a AutoOS Shell v2.4. El kernel está listo para inicializar.",
                    "success": True,
                    "time": datetime.datetime.now().strftime("%H:%M:%S"),
                }
            ]
            st.session_state["gantt_history"] = []
            st.session_state["autoos_sim_paused"] = False

        return st.session_state["autoos_kernel"]
    else:
        if _FALLBACK_KERNEL is None:
            vfs_file = str(CURRENT_DIR / "autoos_vfs_storage.json")
            _FALLBACK_KERNEL = Kernel(
                memory_mb=memory_mb,
                swap_mb=swap_mb,
                vfs_path=vfs_file,
                scheduler_algorithm=AlgorithmType.PRIORITY,
            )
            _FALLBACK_TERMINAL = Terminal(kernel=_FALLBACK_KERNEL)
        return _FALLBACK_KERNEL


def get_terminal() -> Terminal:
    """Retorna la terminal conectada a la instancia activa del Kernel."""
    global _FALLBACK_TERMINAL
    if HAS_STREAMLIT and st is not None:
        get_kernel()  # Garantizar inicialización
        return st.session_state["autoos_terminal"]
    else:
        k = get_kernel()
        if _FALLBACK_TERMINAL is None or _FALLBACK_TERMINAL.kernel != k:
            _FALLBACK_TERMINAL = Terminal(kernel=k)
        return _FALLBACK_TERMINAL


def record_gantt_tick(kernel: Kernel) -> None:
    """Registra la traza del tick actual para el Diagrama de Gantt reactivo."""
    global _FALLBACK_GANTT
    tick = kernel.engine.current_tick
    active_proc = kernel.cpu.current_process
    
    entry = {
        "tick": tick,
        "pid": active_proc.pid if active_proc else 0,
        "name": active_proc.name if active_proc else "[CPU OCIOSA / IDLE]",
        "priority": active_proc.priority if active_proc else 0,
        "state": active_proc.state.value if active_proc else "IDLE",
        "time_str": datetime.datetime.now().strftime("%H:%M:%S"),
    }

    if HAS_STREAMLIT and st is not None:
        if "gantt_history" not in st.session_state:
            st.session_state["gantt_history"] = []
        st.session_state["gantt_history"].append(entry)
        # Mantener últimos 100 ticks en pantalla
        if len(st.session_state["gantt_history"]) > 100:
            st.session_state["gantt_history"] = st.session_state["gantt_history"][-100:]
    else:
        _FALLBACK_GANTT.append(entry)
        if len(_FALLBACK_GANTT) > 100:
            _FALLBACK_GANTT = _FALLBACK_GANTT[-100:]


def get_gantt_history() -> List[Dict[str, Any]]:
    """Retorna el historial de ejecución para el Diagrama de Gantt."""
    global _FALLBACK_GANTT
    if HAS_STREAMLIT and st is not None and "gantt_history" in st.session_state:
        return list(st.session_state["gantt_history"])
    return list(_FALLBACK_GANTT)


def get_terminal_history() -> List[Dict[str, Any]]:
    """Retorna el historial de comandos ejecutados en la terminal."""
    global _FALLBACK_TERMINAL_HIST
    if HAS_STREAMLIT and st is not None and "terminal_history" in st.session_state:
        return list(st.session_state["terminal_history"])
    return list(_FALLBACK_TERMINAL_HIST)


def execute_terminal_command(cmd_line: str) -> TerminalResponse:
    """
    Ejecuta un comando en la terminal interactiva de AutoOS y registra
    la salida en el historial para mostrar en la consola visual.
    """
    global _FALLBACK_TERMINAL_HIST
    terminal = get_terminal()
    kernel = get_kernel()
    
    resp = terminal.execute(cmd_line)
    
    # Si el comando fue step, registrar los ticks en el Gantt
    if cmd_line.strip().lower().startswith("step"):
        record_gantt_tick(kernel)

    entry = {
        "cmd": cmd_line,
        "output": resp.output,
        "success": resp.success,
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
    }

    if HAS_STREAMLIT and st is not None:
        if "terminal_history" not in st.session_state:
            st.session_state["terminal_history"] = []
        st.session_state["terminal_history"].append(entry)
        if len(st.session_state["terminal_history"]) > 50:
            st.session_state["terminal_history"] = st.session_state["terminal_history"][-50:]
    else:
        _FALLBACK_TERMINAL_HIST.append(entry)

    return resp


def step_simulation(cycles: int = 1) -> Dict[str, Any]:
    """
    Avanza N ciclos de simulación sobre el motor central de AutoOS_1.
    Registra cada ciclo en la bitácora de Gantt.
    """
    kernel = get_kernel()
    executed = 0
    for _ in range(cycles):
        success = kernel.engine.tick()
        if success:
            executed += 1
            record_gantt_tick(kernel)
        else:
            break

    return {
        "requested": cycles,
        "executed": executed,
        "current_tick": kernel.engine.current_tick,
        "is_paused": kernel.engine.is_paused,
        "cpu_idle": kernel.cpu.is_idle,
        "active_pid": kernel.cpu.current_process.pid if kernel.cpu.current_process else None,
    }


def boot_system() -> Dict[str, Any]:
    """Ejecuta la secuencia formal de arranque de 7 etapas de AutoOS."""
    kernel = get_kernel()
    res = kernel.boot()
    # Ejecutar demo inicial de Gantt en t=0
    record_gantt_tick(kernel)
    return res


def shutdown_system() -> Dict[str, Any]:
    """Ejecuta el apagado seguro de AutoOS sincronizando VFS y logs a disco."""
    kernel = get_kernel()
    return kernel.shutdown()


def create_process_bridge(
    name: str,
    priority: int = 3,
    burst_time: int = 4,
    memory_size: int = 64,
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Crea un nuevo proceso en el Kernel y asigna su memoria física contigua mediante First-Fit.
    """
    kernel = get_kernel()
    try:
        proc = kernel.engine.create_process(
            name=name,
            priority=priority,
            burst_time=burst_time,
            memory_size=memory_size,
            auto_admit=True,
        )
        return True, f"Proceso PID={proc.pid} ('{proc.name}') creado con éxito.", proc.to_dict()
    except InsufficientMemoryError as err:
        return False, f"Error de memoria: {err}", None
    except Exception as err:
        return False, f"Error al crear proceso: {err}", None


def abort_process_bridge(pid: int) -> Tuple[bool, str]:
    """
    Termina forzosamente un proceso por su PID y libera inmediatamente su bloque de RAM.
    """
    kernel = get_kernel()
    try:
        proc = kernel.engine.abort_process(pid)
        return True, f"Proceso PID={pid} ('{proc.name}') terminado forzosamente. Memoria liberada."
    except Exception as err:
        return False, f"Error al terminar proceso: {err}"


def set_scheduler_bridge(algorithm: str, quantum: int = 2) -> Tuple[bool, str]:
    """Cambia el algoritmo de planificación (PRIORITY, FCFS, ROUND_ROBIN)."""
    kernel = get_kernel()
    try:
        kernel.scheduler.set_algorithm(algorithm, quantum)
        return True, f"Algoritmo actualizado a {algorithm} (Quantum={quantum})."
    except Exception as err:
        return False, f"Error al cambiar algoritmo: {err}"


def toggle_low_battery_mode() -> Tuple[bool, str]:
    """Activa o desactiva el Modo Ahorro de Batería en el Scheduler."""
    kernel = get_kernel()
    sched = kernel.scheduler
    new_state = not sched.low_battery_mode
    affected = sched.set_low_battery_mode(new_state)
    if new_state:
        return True, f"Modo Ahorro de Batería ACTIVADO. PIDs suspendidos: {affected}."
    else:
        return True, f"Modo Ahorro de Batería DESACTIVADO. Procesos reactivados."


def inject_critical_process_bridge() -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Inyecta un proceso crítico ASIL-D de emergencia con preemption forzada."""
    kernel = get_kernel()
    try:
        proc = kernel.engine.create_process(
            name="Freno_Emergencia_AEB_ASILD",
            priority=1,
            burst_time=3,
            memory_size=64,
            auto_admit=False,
        )
        proc.admit()
        kernel.scheduler.inject_critical_process(process=proc, cpu=kernel.cpu, preemptive=True)
        record_gantt_tick(kernel)
        return True, f"¡ALERTA ASIL-D! Proceso crítico inyectado: PID={proc.pid}. CPU desalojada.", proc.to_dict()
    except Exception as err:
        return False, f"Error al inyectar proceso crítico: {err}", None
