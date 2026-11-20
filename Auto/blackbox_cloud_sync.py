"""Persistencia automática de eventos de Caja Negra en Supabase.

Seguridad: el navegador NO tiene acceso directo a secretos. El servidor comprueba
los permisos del usuario Python y valida los campos antes de escribir. Se usa
un identificador estable en detalles.autoos_id para detectar reintentos.
"""
from __future__ import annotations
import math
import re
from typing import Any, MutableMapping

MAX_EVENTS_PER_BATCH = 6
MAX_MESSAGE_LEN = 220
ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{5,90}\Z")
REQUEST_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
KIND_PATTERN = re.compile(r"[A-Z0-9_]{2,32}\Z")
SEVERITY = {"info": "info", "success": "info", "warning": "advertencia", "critical": "critico"}


def _number(value: Any, minimum: float, maximum: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name}: número inválido")
    number = float(value)
    if not math.isfinite(number) or not minimum <= number <= maximum:
        raise ValueError(f"{name}: fuera de rango")
    return round(number, 2)


def validate_blackbox_batch(packet: Any) -> tuple[str, list[dict[str, Any]]]:
    """Valida un lote sin aceptar valores arbitrarios o cargas excesivas."""
    if not isinstance(packet, dict) or packet.get("type") != "autoos:blackbox-batch":
        raise ValueError("Tipo de mensaje desconocido")
    request_id = packet.get("requestId")
    if not isinstance(request_id, str) or not REQUEST_PATTERN.fullmatch(request_id):
        raise ValueError("requestId inválido")
    raw = packet.get("events")
    if not isinstance(raw, list) or not 1 <= len(raw) <= MAX_EVENTS_PER_BATCH:
        raise ValueError("El lote debe contener entre 1 y 6 eventos")
    clean = []
    seen = set()
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("Evento mal formado")
        event_id = item.get("id")
        kind = item.get("kind")
        msg = item.get("message")
        severity = item.get("severity")
        if not isinstance(event_id, str) or not ID_PATTERN.fullmatch(event_id) or event_id in seen:
            raise ValueError("ID de evento inválido o duplicado")
        if not isinstance(kind, str) or not KIND_PATTERN.fullmatch(kind):
            raise ValueError("Clase de evento inválida")
        if not isinstance(msg, str) or not 1 <= len(msg.strip()) <= MAX_MESSAGE_LEN:
            raise ValueError("Descripción fuera de límite")
        if severity not in SEVERITY:
            raise ValueError("Severidad desconocida")
        tick = item.get("tick")
        if isinstance(tick, bool) or not isinstance(tick, int) or not 0 <= tick <= 500000:
            raise ValueError("Tick inválido")
        seen.add(event_id)
        clean.append({
            "id": event_id, "kind": kind, "message": msg.strip(), "severity": SEVERITY[severity],
            "tick": tick,
            "batteryPct": _number(item.get("batteryPct"), 0, 100, "Batería"),
            "cpuPct": _number(item.get("cpuPct"), 0, 10000, "Demanda CPU"),
            "ramMb": _number(item.get("ramMb"), 0, 65536, "RAM"),
        })
    return request_id, clean


def persist_blackbox_batch(packet: Any, client: Any, state: MutableMapping[str, Any], allowed: bool) -> dict[str, Any]:
    """Guarda eventos individualmente; confirma SOLO las filas aceptadas.

    Los IDs confirmados sobreviven a reruns en session_state; la consulta
    por detalles.autoos_id evita repetir un INSERT tras perderse un acuse.
    Si la consulta de deduplicación falla, NO se inserta para evitar duplicados.
    """
    req_id = packet.get("requestId", "") if isinstance(packet, dict) else ""
    result: dict[str, Any] = {"ok": False, "ack": req_id if isinstance(req_id, str) else "",
                              "ackedIds": [], "message": ""}
    try:
        _, events = validate_blackbox_batch(packet)
    except ValueError as exc:
        result["message"] = f"Lote rechazado: {exc}"
        return result
    if not allowed:
        result["message"] = "RBAC: el perfil Python no puede registrar eventos del laboratorio."
        return result
    if client is None:
        result["message"] = "Supabase no configurado en el servidor Streamlit."
        return result

    confirmed = set(state.get("autoos_v14_confirmed_ids", []))
    failures = []
    for event in events:
        uid = event["id"]
        if uid in confirmed:
            result["ackedIds"].append(uid)
            continue
        try:
            # JSONB filtrado por clave estable. La lectura RLS debe permitir verlo.
            previous = client.table("eventos").select("id").contains(
                "detalles", {"autoos_id": uid}
            ).limit(1).execute()
            if not getattr(previous, "data", None):
                details = {
                    "origen": "caja_negra_autoos", "autoos_id": uid,
                    "clase": event["kind"], "tick": event["tick"],
                    "bateria_pct": event["batteryPct"],
                    "cpu_demanda_pct": event["cpuPct"], "ram_estimada_mb": event["ramMb"],
                    "tipo_medicion": "simulacion_react",
                }
                client.table("eventos").insert({
                    "tipo_evento": "simulacion", "severidad": event["severity"],
                    "mensaje": (f"AutoOS Caja Negra T{event['tick']} {event['kind']}: " + event["message"])[:240],
                    "detalles": details, "resuelto": event["severity"] == "info",
                }).execute()
            confirmed.add(uid)
            result["ackedIds"].append(uid)
        except Exception as exc:
            # No incluimos tokens, URL ni traza del SDK en la respuesta JS.
            failures.append(f"{uid[:24]} ({type(exc).__name__})")
    state["autoos_v14_confirmed_ids"] = list(confirmed)[-600:]
    result["ok"] = len(result["ackedIds"]) == len(events)
    count = len(result["ackedIds"])
    result["message"] = (f"Supabase confirmó {count}/{len(events)} eventos de Caja Negra." +
                         (f" Pendientes: {len(failures)}; revisar permisos/conexión." if failures else ""))
    return result
