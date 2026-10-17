"""
Módulo que define los estados canónicos del ciclo de vida de un proceso en AutoOS
y la matriz de transiciones permitidas.
"""
from enum import Enum
from typing import Dict, Set


class ProcessState(Enum):
    """
    Representa los estados canónicos del ciclo de vida de un proceso en AutoOS.
    
    Siguiendo el modelo clásico de sistemas operativos (Silberschatz / Tanenbaum):
    - NEW: El proceso acaba de ser creado pero aún no ha sido admitido en la cola de listos.
    - READY: El proceso está listo en memoria principal esperando que la CPU sea asignada.
    - RUNNING: El proceso tiene la CPU asignada y sus instrucciones se están ejecutando.
    - WAITING: El proceso está bloqueado esperando un evento externo (ej. lectura de sensor vehicular).
    - TERMINATED: El proceso ha finalizado su ejecución o ha sido abortado.
    """
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    TERMINATED = "TERMINATED"

    def __str__(self) -> str:
        return self.value


# Matriz canónica de transiciones permitidas según la teoría de Sistemas Operativos.
# Clave: Estado actual -> Valor: Conjunto de estados a los que se permite transicionar.
# Permite NEW -> TERMINATED exclusivamente para soportar cancelación/aborto temprano.
VALID_TRANSITIONS: Dict[ProcessState, Set[ProcessState]] = {
    ProcessState.NEW: {ProcessState.READY, ProcessState.TERMINATED},
    ProcessState.READY: {ProcessState.RUNNING, ProcessState.TERMINATED},
    ProcessState.RUNNING: {ProcessState.READY, ProcessState.WAITING, ProcessState.TERMINATED},
    ProcessState.WAITING: {ProcessState.READY, ProcessState.TERMINATED},
    ProcessState.TERMINATED: set(),  # Estado terminal: no permite ninguna transición posterior.
}
