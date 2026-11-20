"""Validación del transporte de reportes React hacia Supabase en Streamlit.

La persistencia ocurre desde Python. Los paquetes del navegador son datos
NO CONFIABLES: se valida tamaño, tipos y límites antes de escribirlos.
No se expone ninguna clave del servidor al cliente web.
"""
from __future__ import annotations
import json
import re
from typing import Any

VALID_SCENARIOS = {"normal", "battery", "gps", "camera", "cpu", "network", "storm", "sandbox"}


def validate_cloud_report(packet: Any) -> dict[str, Any]:
    """Devuelve el reporte normalizado o lanza ValueError (sin cambios en BD)."""
    if not isinstance(packet, dict) or packet.get("type") != "autoos:cloud-report":
        raise ValueError("Tipo de mensaje inválido")
    report = packet.get("report")
    if not isinstance(report, dict):
        raise ValueError("Falta el reporte")
    if len(json.dumps(report, ensure_ascii=False)) > 30000:
        raise ValueError("El reporte supera el tamaño permitido")
    report_id = report.get("id")
    if not isinstance(report_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", report_id):
        raise ValueError("ID de reporte inválido")
    if report.get("scenario") not in VALID_SCENARIOS:
        raise ValueError("Escenario desconocido")
    actions = report.get("actions")
    if not isinstance(actions, list) or len(actions) > 50:
        raise ValueError("Acciones fuera de límite")
    for action in actions:
        if not isinstance(action, dict) or not isinstance(action.get("choice"), str):
            raise ValueError("Formato de decisión inválido")
    initial, final = report.get("initial"), report.get("final")
    if not isinstance(initial, dict) or not isinstance(final, dict):
        raise ValueError("Falta instantánea de recursos")
    for name, snapshot in (("inicial", initial), ("final", final)):
        for key in ("battery", "speed", "cpuLoad", "usedMemory"):
            value = snapshot.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not -1e7 < value < 1e7:
                raise ValueError(f"{name}: {key} inválido")
    return {
        "report_id": report_id,
        "escenario": report["scenario"],
        "titulo": str(report.get("title", "Simulación AutoOS"))[:140],
        "diagnostico": str(report.get("diagnosis", ""))[:500],
        "evaluacion": str(report.get("status", ""))[:120],
        "usuario_email": "mecanico@autoos.tech",  # Demo: nunca tomar identidad de JavaScript.
        "iniciado_en": str(report.get("startedAt", ""))[:40],
        "finalizado_en": str(report.get("completedAt", ""))[:40],
        "bateria_inicial": float(initial["battery"]),
        "bateria_final": float(final["battery"]),
        "velocidad_final": float(final["speed"]),
        "cpu_load_final": float(final["cpuLoad"]),
        "acciones_json": actions,
        "recomendaciones": report.get("recommendations", [])[:30] if isinstance(report.get("recommendations"), list) else [],
        "datos_completos": report,
    }
