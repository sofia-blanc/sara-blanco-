"""
Módulo que implementa la CPU simulada de un solo núcleo (Uniprocesador)
y los mecanismos de exclusión mutua para AutoOS.
"""
from typing import Optional, Dict, Any
from src.core.process_state import ProcessState
from src.core.process import Process
from src.core.exceptions import (
    CPUBusyError,
    InvalidStateTransitionError,
    InvalidProcessAttributeError,
)


class CPU:
    """
    Representa una CPU física o virtual de un solo núcleo en AutoOS.
    
    Principios de diseño de SO:
    1. Exclusión Mutua: En cualquier instante de tiempo t, la CPU ejecuta como máximo un proceso.
    2. Transición Estricta: Solo acepta procesos en estado READY, los cuales pasan a RUNNING al cargarse.
    3. Auto-liberación: Si el proceso concluye su tiempo de ráfaga durante un tick, la CPU queda ociosa.
    4. Desalojo Seguro: Permite expulsar (preempt), bloquear (block) o abortar (terminate) el proceso en ejecución
       dejando la CPU lista para una nueva asignación.
    """

    def __init__(self):
        """Inicializa la CPU en estado ocioso (IDLE) con sus métricas en cero."""
        self._current_process: Optional[Process] = None
        self._total_ticks: int = 0
        self._busy_ticks: int = 0
        self._idle_ticks: int = 0

    # --- Propiedades de inspección de la CPU ---

    @property
    def current_process(self) -> Optional[Process]:
        """Retorna el proceso actualmente asignado al núcleo de CPU, o None si está libre."""
        return self._current_process

    @property
    def is_idle(self) -> bool:
        """
        Indica si la CPU está libre (sin proceso asignado o con un proceso ya finalizado).
        """
        return self._current_process is None or self._current_process.is_finished

    @property
    def total_ticks(self) -> int:
        """Cantidad total de ciclos de reloj ejecutados por la CPU."""
        return self._total_ticks

    @property
    def busy_ticks(self) -> int:
        """Ciclos de reloj en los que la CPU ejecutó un proceso."""
        return self._busy_ticks

    @property
    def idle_ticks(self) -> int:
        """Ciclos de reloj en los que la CPU estuvo ociosa (sin proceso asignado)."""
        return self._idle_ticks

    # --- Gestión de Procesos en CPU ---

    def load_process(self, process: Process) -> None:
        """
        Carga un proceso en el núcleo de la CPU para su ejecución inmediata.
        
        Reglas de integridad de SO:
        1. La CPU debe estar libre (is_idle == True). Si ya está ocupada, se rechaza
           con CPUBusyError sin alterar el estado de ningún proceso.
        2. El proceso entrante debe encontrarse en estado READY. Si está en NEW, WAITING,
           RUNNING o TERMINATED, se rechaza con InvalidStateTransitionError.
        3. Al cargarse con éxito, el proceso transiciona inmediatamente de READY a RUNNING
           mediante process.dispatch().

        :param process: Instancia de Process a cargar.
        """
        if not isinstance(process, Process):
            raise InvalidProcessAttributeError("El parámetro proporcionado debe ser una instancia de Process.")

        # Regla 1: Exclusión mutua (Uniprocesador)
        if not self.is_idle:
            raise CPUBusyError(
                current_pid=self._current_process.pid,
                incoming_pid=process.pid
            )

        # Regla 2: Solo procesos READY pueden entrar a la CPU
        if process.state != ProcessState.READY:
            raise InvalidStateTransitionError(
                pid=process.pid,
                current_state=process.state.value,
                target_state=ProcessState.RUNNING.value
            )

        # Regla 3: Despacho a RUNNING y toma de posesión del núcleo
        process.dispatch()
        self._current_process = process

    def tick(self) -> Optional[int]:
        """
        Simula el transcurso de un ciclo de reloj (tick de CPU).
        
        Comportamiento:
        - Incrementa el contador global de ticks.
        - Si la CPU está ociosa, incrementa idle_ticks y retorna None.
        - Si hay un proceso en ejecución, incrementa busy_ticks y ejecuta
          process.consume_cpu_tick().
        - Si el proceso agota su tiempo restante (remaining_time == 0), este
          transiciona automáticamente a TERMINATED y la CPU se libera inmediatamente.

        :return: Tiempo restante del proceso si había uno en ejecución, o None si la CPU estaba ociosa.
        """
        self._total_ticks += 1

        if self.is_idle:
            self._idle_ticks += 1
            return None

        self._busy_ticks += 1
        remaining_time = self._current_process.consume_cpu_tick()

        # Si el proceso completó su ráfaga y finalizó, la CPU queda libre de inmediato
        if self._current_process.is_finished:
            self._current_process = None

        return remaining_time

    # --- Métodos de Liberación / Desalojo Seguro (Context Switch) ---

    def preempt_process(self) -> Optional[Process]:
        """
        Expulsa el proceso activo de la CPU por preempción (quantum expirado o proceso de mayor prioridad).
        El proceso transiciona de RUNNING a READY y la CPU queda libre.
        
        :return: El proceso desalojado, o None si la CPU ya estaba libre.
        """
        return self.release_process(target_state=ProcessState.READY)

    def block_process(self) -> Optional[Process]:
        """
        Retira el proceso activo de la CPU debido a una espera de E/S o sensor vehicular.
        El proceso transiciona de RUNNING a WAITING y la CPU queda libre.
        
        :return: El proceso bloqueado, o None si la CPU ya estaba libre.
        """
        return self.release_process(target_state=ProcessState.WAITING)

    def terminate_process(self) -> Optional[Process]:
        """
        Finaliza/aborta forzosamente el proceso activo en la CPU.
        El proceso transiciona de RUNNING a TERMINATED y la CPU queda libre.
        
        :return: El proceso terminado, o None si la CPU ya estaba libre.
        """
        return self.release_process(target_state=ProcessState.TERMINATED)

    def release_process(self, target_state: ProcessState = ProcessState.READY) -> Optional[Process]:
        """
        Libera el proceso activo de la CPU llevándolo de manera segura al target_state especificado.
        
        :param target_state: Estado destino (debe ser READY, WAITING o TERMINATED).
        :return: El proceso que fue liberado, o None si la CPU no tenía ningún proceso activo.
        """
        if self.is_idle:
            return None

        process = self._current_process

        if target_state == ProcessState.READY:
            process.preempt()
        elif target_state == ProcessState.WAITING:
            process.block()
        elif target_state == ProcessState.TERMINATED:
            process.terminate()
        else:
            raise InvalidStateTransitionError(
                pid=process.pid,
                current_state=process.state.value,
                target_state=target_state.value
            )

        # La CPU queda formalmente libre
        self._current_process = None
        return process

    # --- Serialización para métricas e interfaz ---

    def to_dict(self) -> Dict[str, Any]:
        """
        Genera una instantánea de estado de la CPU en formato diccionario (JSON-serializable).
        Facilita la futura integración con el Dashboard web y Supabase.
        """
        cpu_utilization = 0.0
        if self._total_ticks > 0:
            cpu_utilization = round((self._busy_ticks / self._total_ticks) * 100, 2)

        return {
            "is_idle": self.is_idle,
            "current_process": self._current_process.to_dict() if self._current_process else None,
            "total_ticks": self._total_ticks,
            "busy_ticks": self._busy_ticks,
            "idle_ticks": self._idle_ticks,
            "utilization_percentage": cpu_utilization,
        }

    def __repr__(self) -> str:
        current_pid = self._current_process.pid if self._current_process else "None"
        return (
            f"CPU(is_idle={self.is_idle}, active_pid={current_pid}, "
            f"ticks={self._total_ticks}, busy={self._busy_ticks}, idle={self._idle_ticks})"
        )
