"""
Módulo core de AutoOS.
Contiene el modelo de procesos, estados, excepciones y estructuras del sistema operativo.
"""
from src.core.process_state import ProcessState, VALID_TRANSITIONS
from src.core.exceptions import (
    AutoOSError,
    InvalidStateTransitionError,
    InvalidProcessPriorityError,
    InvalidProcessAttributeError,
    CPUBusyError,
    DuplicateProcessError,
)
from src.core.process import Process
from src.core.cpu import CPU
from src.core.scheduler import Scheduler
from src.core.event_logger import Event, EventLogger
from src.core.simulation import SimulationEngine

__all__ = [
    "ProcessState",
    "VALID_TRANSITIONS",
    "AutoOSError",

    "InvalidStateTransitionError",
    "InvalidProcessPriorityError",
    "InvalidProcessAttributeError",
    "CPUBusyError",
    "DuplicateProcessError",
    "Process",
    "CPU",
    "Scheduler",
    "Event",
    "EventLogger",
    "SimulationEngine",
]



