"""Puente React → Kernel Python para el laboratorio AutoOS.

El simulador del navegador tiene su propio planificador. Este adaptador crea
*procesos equivalentes para experimentar* sobre el kernel Python por sesión:
First-Fit reserva RAM, el motor ejecuta ticks y devuelve su estado auténtico.
No copia ciegamente porcentajes de RAM/CPU de React al kernel, no mezcla PIDs,
no altera Supabase ni debe presentarse como un único scheduler determinista.

Una sincronización es una acción explícita y requiere el permiso Python
`proceso.crear`. Los valores de React se validan como entrada no confiable.
"""
from __future__ import annotations

import re
from typing import Any, MutableMapping

MAX_PROCESSES = 24
MAX_TICKS_PER_SYNC = 12
MAX_RAM_PER_PROCESS_MB = 1024
_MAX_NAME_LEN = 56


def _int(value: Any, low: int, high: int, label: str) -> int:
    """Valida enteros sin convertir silenciosamente decimales arbitrarios."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label}: se esperaba un número")
    if not float(value).is_integer() or not low <= int(value) <= high:
        raise ValueError(f"{label}: fuera del rango {low}-{high}")
    return int(value)


def _validate_packet(packet: Any) -> dict[str, Any]:
    """Límite y saneamiento del mensaje que llega desde el iframe."""
    if not isinstance(packet, dict) or packet.get("type") != "autoos:kernel-sync":
        raise ValueError("Mensaje del puente no reconocido")
    req_id = packet.get("requestId")
    if not isinstance(req_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", req_id):
        raise ValueError("Identificador de solicitud inválido")
    tick = _int(packet.get("tick"), 0, 500000, "Tick")
    raw = packet.get("processes")
    if not isinstance(raw, list) or len(raw) > MAX_PROCESSES:
        raise ValueError("Demasiados procesos (máximo 24)")
    processes: list[dict] = []
    seen: set[int] = set()
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("Formato de proceso inválido")
        js_pid = _int(item.get("pid"), 1, 999999, "PID React")
        if js_pid in seen:
            raise ValueError("PIDs React duplicados")
        seen.add(js_pid)
        name = item.get("name", "")
        if not isinstance(name, str) or not name.strip() or len(name) > 120:
            raise ValueError("Nombre de proceso inválido")
        # Nombres acotados para la tabla de procesos y la auditoría del kernel.
        name = re.sub(r"[^\w -]", "_", name, flags=re.UNICODE).strip()[:_MAX_NAME_LEN]
        processes.append({
            "pid": js_pid, "name": name,
            "priority": _int(item.get("priority"), 1, 5, "Prioridad"),
            "memoryMb": _int(item.get("memoryMb"), 1, MAX_RAM_PER_PROCESS_MB, "RAM"),
            "burstTime": _int(item.get("burstTime"), 1, 5000, "Ráfaga"),
        })
    battery = packet.get("batteryPct")
    if isinstance(battery, bool) or not isinstance(battery, (float, int)) or not 0 <= battery <= 100:
        raise ValueError("Batería fuera del rango 0-100")
    return {"requestId": req_id, "tick": tick, "processes": processes,
            "batteryPct": round(float(battery), 2)}


def kernel_status(kernel: Any, state: MutableMapping[str, Any],
                  message: str = "", errors: list[str] | None = None) -> dict[str, Any]:
    """Lectura del kernel auténtico; no copia números calculados en React."""
    active = kernel.cpu.current_process
    pids = state.get("autoos_v10_pid_map", {})
    return {
        "connected": True,
        "mode": "ESPEJO DIDÁCTICO",
        "booted": bool(kernel.is_booted),
        "tick": int(kernel.engine.current_tick),
        "ramMb": int(kernel.memory_manager.used_memory),
        "ramTotalMb": int(kernel.memory_manager.total_memory),
        "cpuPid": active.pid if active else None,
        "pythonProcesses": len(kernel.engine.get_all_processes()),
        "mappedPids": {str(k): v for k, v in pids.items()},
        "events": int(kernel.logger.total_events),
        "lastReactTick": int(state.get("autoos_v10_last_react_tick", 0)),
        "lastBatteryPctReact": state.get("autoos_v10_last_battery"),
        "message": message or state.get("autoos_v10_last_message", "Sincronización disponible."),
        "errors": errors if errors is not None else state.get("autoos_v10_last_errors", []),
        "ack": state.get("autoos_v10_last_request_id"),
    }


def sync_react_with_kernel(packet: Any, kernel: Any,
                           state: MutableMapping[str, Any],
                           allowed: bool) -> dict[str, Any]:
    """Crea/finaliza procesos espejo y avanza ciclos del kernel por demanda.

    Los PIDs en Python son independientes. Los procesos BMS/CAN/ADAS de boot se
    conservan y pueden consumir recursos. El kernel aplica First-Fit real y
    puede rechazar reservas. Nunca se asigna arbitrariamente memoria usada.

    `allowed` debe venir del RBAC de Python, NO del rol declarado por React.
    """
    try:
        cmd = _validate_packet(packet)
    except ValueError as err:
        return kernel_status(kernel, state, f"Solicitud rechazada: {err}", [str(err)])
    if state.get("autoos_v10_last_request_id") == cmd["requestId"]:
        return kernel_status(kernel, state)  # idempotencia ante rerun
    if not allowed:
        return kernel_status(kernel, state, "Acceso denegado: el perfil Python no puede crear procesos.",
                             ["RBAC: falta permiso proceso.crear"])

    if not kernel.is_booted:
        kernel.boot()  # Secuencia formal de 7 etapas, solo en solicitud autorizada.

    mapping: dict[int, int] = dict(state.get("autoos_v10_pid_map", {}))
    previous_definitions: dict[int, tuple] = dict(state.get("autoos_v10_pid_config", {}))
    requested: dict[int, dict] = {p["pid"]: p for p in cmd["processes"]}
    errors: list[str] = []
    # Se abortan SOLO procesos que este puente haya creado; nunca daemons del boot.
    for react_pid, kernel_pid in list(mapping.items()):
        if react_pid not in requested:
            try:
                kernel.engine.abort_process(kernel_pid)
            except Exception:
                pass  # pudo finalizar de forma natural entre sincronizaciones
            del mapping[react_pid]
            previous_definitions.pop(react_pid, None)

    # Algunos procesos pueden finalizar naturalmente: se recrean al solicitar
    # una nueva sesión, con PID Python diferente. No sobrescribimos el proceso.
    existing = {p.pid: p for p in kernel.engine.get_all_processes()}
    for js_pid, p in requested.items():
        mapped = mapping.get(js_pid)
        signature = (p["name"], p["priority"], p["memoryMb"])
        if mapped and previous_definitions.get(js_pid) != signature:
            try:
                kernel.engine.abort_process(mapped)
            except Exception:
                pass
            mapping.pop(js_pid, None)
        if mapped and js_pid in mapping and mapped in existing and existing[mapped].state.value != "TERMINATED":
            continue
        mapping.pop(js_pid, None)
        previous_definitions.pop(js_pid, None)
        try:
            created = kernel.engine.create_process(
                name=f"LAB_{js_pid}_{p['name']}"[:80],
                priority=p["priority"],
                burst_time=max(25, min(250, p["burstTime"])),
                memory_size=p["memoryMb"],
                auto_admit=True,
            )
            mapping[js_pid] = created.pid
            previous_definitions[js_pid] = signature
        except Exception as err:
            errors.append(f"React PID {js_pid}: {type(err).__name__}: {str(err)[:100]}")

    previous_tick = int(state.get("autoos_v10_last_react_tick", 0))
    # Si React reinicia su escena, el reloj Python NO retrocede. Tomamos
    # los nuevos ticks desde cero sin borrar los procesos del sistema real.
    if cmd["tick"] < previous_tick:
        previous_tick = 0
    # Diferencias grandes se limitan para evitar bloquear la interfaz web.
    advance = max(0, min(MAX_TICKS_PER_SYNC, cmd["tick"] - previous_tick))
    for _ in range(advance):
        if not kernel.engine.tick():
            errors.append("Kernel pausado; no se avanzaron todos los ciclos")
            break

    state["autoos_v10_pid_map"] = mapping
    state["autoos_v10_pid_config"] = previous_definitions
    state["autoos_v10_last_react_tick"] = cmd["tick"]
    state["autoos_v10_last_battery"] = cmd["batteryPct"]
    state["autoos_v10_last_request_id"] = cmd["requestId"]
    state["autoos_v10_last_errors"] = errors
    state["autoos_v10_last_message"] = (
        f"Kernel actualizado: {len(mapping)} procesos espejo, "
        f"{kernel.memory_manager.used_memory} MB reservados, "
        f"tick Python {kernel.engine.current_tick}."
    )
    return kernel_status(kernel, state)
