"""
Módulo que implementa el Bloque de Control de Proceso (PCB - Process Control Block)
y la máquina de estados del ciclo de vida del proceso para AutoOS.
"""
from typing import Dict, Any, Set
import itertools
from src.core.process_state import ProcessState, VALID_TRANSITIONS
from src.core.exceptions import (
    InvalidStateTransitionError,
    InvalidProcessPriorityError,
    InvalidProcessAttributeError,
)


class Process:
    """
    Representa un proceso en la simulación de AutoOS (equivalente al PCB en un SO real).
    
    Contiene la información de control necesaria para que el sistema operativo
    pueda gestionar, planificar y monitorear la ejecución del proceso.
    """
    
    # Generador estático para garantizar PIDs únicos, secuenciales e inmutables durante la ejecución.
    _pid_counter = itertools.count(start=1)

    # Matriz canónica de transiciones permitidas (importada de process_state)
    VALID_TRANSITIONS: Dict[ProcessState, Set[ProcessState]] = VALID_TRANSITIONS


    # Rango de prioridad definido: 1 es la más alta (crítica), 5 es la más baja.
    MIN_PRIORITY = 1
    MAX_PRIORITY = 5

    def __init__(
        self,
        name: str,
        priority: int = 3,
        burst_time: int = 1,
    ):
        """
        Inicializa un nuevo proceso (PCB) en estado NEW.

        :param name: Nombre descriptivo de la tarea vehicular (ej. 'Frenado Autónomo').
        :param priority: Nivel de prioridad (1 = Crítica a 5 = Baja). Por defecto 3.
        :param burst_time: Tiempo total estimado de CPU requerido en ciclos/ticks (> 0).
        """
        if not name or not isinstance(name, str) or not name.strip():
            raise InvalidProcessAttributeError("El nombre del proceso debe ser una cadena de texto no vacía.")

        self._validate_priority(priority)
        if isinstance(burst_time, bool) or not isinstance(burst_time, int) or burst_time <= 0:
            raise InvalidProcessAttributeError(
                f"El tiempo de ráfaga (burst_time) debe ser un entero mayor a 0. Recibido: {burst_time}"
            )

        # Campos del Bloque de Control de Proceso (PCB):
        self._pid: int = next(self._pid_counter)
        self._name: str = name.strip()
        self._priority: int = priority
        self._state: ProcessState = ProcessState.NEW
        self._burst_time: int = burst_time
        self._remaining_time: int = burst_time

    @classmethod
    def _reset_pid_generator(cls, start: int = 1) -> None:
        """
        Método utilitario para reiniciar el contador de PIDs.
        Diseñado principalmente para garantizar pruebas unitarias deterministas e independientes.
        """
        cls._pid_counter = itertools.count(start=start)

    @classmethod
    def _validate_priority(cls, priority: int) -> None:
        """Valida que la prioridad esté dentro del rango permitido [1, 5] y no sea booleano."""
        if isinstance(priority, bool) or not isinstance(priority, int) or priority < cls.MIN_PRIORITY or priority > cls.MAX_PRIORITY:
            raise InvalidProcessPriorityError(priority)


    # --- Propiedades del PCB (Getters y Setters controlados) ---

    @property
    def pid(self) -> int:
        """Identificador único del proceso (inmutable tras la creación)."""
        return self._pid

    @property
    def name(self) -> str:
        """Nombre descriptivo de la tarea vehicular."""
        return self._name

    @property
    def priority(self) -> int:
        """Prioridad actual del proceso (1: Crítica, 5: Baja)."""
        return self._priority

    @priority.setter
    def priority(self, new_priority: int) -> None:
        """
        Permite actualizar la prioridad del proceso si no está terminado.
        Lanza excepción si el proceso ya está en TERMINATED o la prioridad está fuera de rango.
        """
        if self._state == ProcessState.TERMINATED:
            raise InvalidStateTransitionError(
                pid=self._pid,
                current_state=self._state.value,
                target_state="MODIFICAR_PRIORIDAD"
            )
        self._validate_priority(new_priority)
        self._priority = new_priority

    @property
    def state(self) -> ProcessState:
        """Estado actual del ciclo de vida del proceso."""
        return self._state

    @property
    def burst_time(self) -> int:
        """Tiempo de CPU total estimado para completar la tarea."""
        return self._burst_time

    @property
    def remaining_time(self) -> int:
        """Tiempo de CPU restante que el proceso aún necesita ejecutar."""
        return self._remaining_time

    @property
    def is_finished(self) -> bool:
        """Indica si el proceso ha finalizado su ciclo de vida."""
        return self._state == ProcessState.TERMINATED

    # --- Máquina de Estados: Transiciones estrictas ---

    def transition_to(self, target_state: ProcessState) -> None:
        """
        Aplica una transición de estado si y solo si es permitida por la máquina de estados.
        Lanza InvalidStateTransitionError en caso de que la transición sea ilegal.
        """
        allowed_targets = self.VALID_TRANSITIONS.get(self._state, set())
        if target_state not in allowed_targets:
            raise InvalidStateTransitionError(
                pid=self._pid,
                current_state=self._state.value,
                target_state=target_state.value,
            )
        self._state = target_state

    # Métodos semánticos para cada transición estándar de SO:

    def admit(self) -> None:
        """
        Transición NEW -> READY.
        El planificador a largo plazo admite el proceso en la memoria/cola de listos.
        """
        self.transition_to(ProcessState.READY)

    def dispatch(self) -> None:
        """
        Transición READY -> RUNNING.
        El despachador (dispatcher) asigna la CPU al proceso.
        """
        self.transition_to(ProcessState.RUNNING)

    def preempt(self) -> None:
        """
        Transición RUNNING -> READY.
        Se expulsa el proceso de la CPU (por fin de quantum o arribo de proceso de mayor prioridad).
        """
        self.transition_to(ProcessState.READY)

    def block(self) -> None:
        """
        Transición RUNNING -> WAITING.
        El proceso se bloquea a la espera de un evento externo o recurso (ej. sensor vehicular).
        """
        self.transition_to(ProcessState.WAITING)

    def unblock(self) -> None:
        """
        Transición WAITING -> READY.
        El evento o recurso esperado se completa, regresando a la cola de listos.
        """
        self.transition_to(ProcessState.READY)

    def terminate(self) -> None:
        """
        Transición a TERMINATED.
        El proceso finaliza su ejecución normalmente o es abortado.
        Puede ocurrir desde RUNNING (término normal), READY o WAITING (cancelación/aborto).
        """
        self.transition_to(ProcessState.TERMINATED)

    # --- Ejecución y consumo de CPU ---

    def consume_cpu_tick(self) -> int:
        """
        Simula el consumo de un tick/ciclo de tiempo de CPU.
        Regla de integridad: Solo puede ejecutarse si el proceso está actualmente en estado RUNNING.
        Si el tiempo restante llega a cero, el proceso transiciona automáticamente a TERMINATED.
        
        :return: Tiempo de CPU restante.
        """
        if self._state != ProcessState.RUNNING:
            raise InvalidStateTransitionError(
                pid=self._pid,
                current_state=self._state.value,
                target_state="EJECUTAR_TICK (requiere estado RUNNING)"
            )

        if self._remaining_time > 0:
            self._remaining_time -= 1

        if self._remaining_time == 0:
            self.terminate()

        return self._remaining_time

    # --- Serialización e Integración ---

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el PCB en un diccionario serializable en formato JSON.
        Prepara el modelo para la integración futura con Supabase y el Dashboard web.
        """
        return {
            "pid": self._pid,
            "name": self._name,
            "priority": self._priority,
            "state": self._state.value,
            "burst_time": self._burst_time,
            "remaining_time": self._remaining_time,
            "is_finished": self.is_finished,
        }

    def __repr__(self) -> str:
        return (
            f"Process(PID={self._pid}, Name='{self._name}', "
            f"Priority={self._priority}, State={self._state.value}, "
            f"Remaining={self._remaining_time}/{self._burst_time})"
        )
