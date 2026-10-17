"""
Excepciones de dominio para el módulo de procesos y CPU de AutoOS.
"""


class AutoOSError(Exception):
    """Clase base para todas las excepciones del dominio AutoOS."""
    pass


class InvalidStateTransitionError(AutoOSError):
    """
    Se lanza cuando un proceso intenta una transición de estado no permitida
    por la máquina de estados del sistema operativo.
    """
    def __init__(self, pid: int, current_state: str, target_state: str):
        self.pid = pid
        self.current_state = current_state
        self.target_state = target_state
        super().__init__(
            f"[PID {pid}] Transición inválida: "
            f"no se permite cambiar del estado '{current_state}' al estado '{target_state}'."
        )


class InvalidProcessPriorityError(AutoOSError):
    """
    Se lanza cuando se asigna una prioridad fuera del rango permitido [1, 5].
    En AutoOS: 1 representa la prioridad más alta (crítica) y 5 la más baja.
    """
    def __init__(self, priority: int):
        self.priority = priority
        super().__init__(
            f"Prioridad inválida '{priority}'. "
            f"La prioridad debe ser un entero entre 1 (Crítica) y 5 (Baja)."
        )


class InvalidProcessAttributeError(AutoOSError):
    """
    Se lanza cuando los parámetros iniciales de un proceso no cumplen las restricciones del sistema.
    """
    pass


class CPUBusyError(AutoOSError):
    """
    Se lanza cuando se intenta asignar un proceso a la CPU mientras
    esta ya se encuentra ejecutando otro proceso (violación de exclusión mutua en uniprocesador).
    """
    def __init__(self, current_pid: int, incoming_pid: int):
        self.current_pid = current_pid
        self.incoming_pid = incoming_pid
        super().__init__(
            f"CPU ocupada: No se puede asignar el proceso PID={incoming_pid} "
            f"porque la CPU ya está ejecutando el proceso PID={current_pid}."
        )


class DuplicateProcessError(AutoOSError):
    """
    Se lanza cuando se intenta encolar un proceso que ya está presente en la cola de listos.
    """
    def __init__(self, pid: int):
        self.pid = pid
        super().__init__(
            f"Proceso duplicado: El proceso PID={pid} ya se encuentra en la cola del planificador."
        )


