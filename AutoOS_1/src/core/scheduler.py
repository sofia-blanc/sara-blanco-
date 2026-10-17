"""
Módulo que implementa el Planificador por Prioridad (Priority Scheduler)
y la gestión de la cola de listos (ReadyQueue) para AutoOS.
"""
from typing import Optional, List, Dict, Any, Set, Tuple
import heapq
from src.core.process_state import ProcessState
from src.core.process import Process
from src.core.cpu import CPU
from src.core.exceptions import (
    DuplicateProcessError,
    InvalidStateTransitionError,
    InvalidProcessAttributeError,
)


class Scheduler:
    """
    Planificador de procesos por prioridad para AutoOS.
    
    Principios de funcionamiento y teoría de SO:
    1. Cola de listos con prioridad: Los procesos con menor valor numérico
       de prioridad (1 = Crítica) son seleccionados antes que aquellos con mayor valor (5 = Baja).
    2. Desempate FIFO: Procesos con idéntica prioridad se ordenan según el orden
       estricto de llegada a la cola.
    3. Unicidad: No se permite tener el mismo proceso duplicado en la cola.
    4. Validación de estado: Solo se admiten procesos en estado READY.
    5. Política no apropiativa (Non-preemptive): La CPU ejecuta el proceso activo
       sin que el planificador lo desaloje automáticamente al llegar uno de mayor prioridad.
    6. Despacho seguro: Si la CPU está ocupada, no se altera la cola ni se pierden procesos.
    """

    def __init__(self):
        """Inicializa el planificador con una cola de listos vacía."""
        # Cola min-heap de tuplas: (prioridad: int, orden_llegada: int, proceso: Process)
        self._queue: List[Tuple[int, int, Process]] = []
        # Conjunto de PIDs para verificación de duplicados en O(1)
        self._pid_set: Set[int] = set()
        # Contador secuencial para desempate FIFO estricto
        self._arrival_counter: int = 0

    @property
    def is_empty(self) -> bool:
        """Indica si la cola de listos está vacía."""
        return len(self._queue) == 0

    @property
    def ready_count(self) -> int:
        """Cantidad de procesos actualmente en espera en la cola de listos."""
        return len(self._queue)

    def add_process(self, process: Process) -> None:
        """
        Agrega un proceso en estado READY a la cola de listos del planificador.
        
        :param process: Instancia de Process a encolar.
        :raises InvalidProcessAttributeError: Si no es una instancia de Process.
        :raises DuplicateProcessError: Si el proceso ya se encuentra en la cola.
        :raises InvalidStateTransitionError: Si el proceso no se encuentra en estado READY.
        """
        if not isinstance(process, Process):
            raise InvalidProcessAttributeError("El objeto a encolar debe ser una instancia de Process.")

        if process.pid in self._pid_set:
            raise DuplicateProcessError(process.pid)

        if process.state != ProcessState.READY:
            raise InvalidStateTransitionError(
                pid=process.pid,
                current_state=process.state.value,
                target_state=ProcessState.READY.value
            )

        # Encolar en el heap: (prioridad, orden_llegada, proceso)
        heapq.heappush(self._queue, (process.priority, self._arrival_counter, process))
        self._pid_set.add(process.pid)
        self._arrival_counter += 1

    def remove_process(self, pid: int) -> Optional[Process]:
        """
        Retira un proceso de la cola de listos por su PID (útil si fue abortado).
        Retorna el proceso retirado o None si no estaba en la cola.
        """
        if pid not in self._pid_set:
            return None
        self._pid_set.remove(pid)
        for i, (prio, arrival, proc) in enumerate(self._queue):
            if proc.pid == pid:
                removed_proc = self._queue.pop(i)[2]
                heapq.heapify(self._queue)
                return removed_proc
        return None

    def update_process_priority(self, pid: int, new_priority: int) -> bool:
        """
        Actualiza la prioridad de un proceso que ya está en la cola de listos y reordena el montículo.
        """
        Process._validate_priority(new_priority)
        if pid not in self._pid_set:
            return False
        for i, (prio, arrival, proc) in enumerate(self._queue):
            if proc.pid == pid:
                proc.priority = new_priority
                self._queue[i] = (new_priority, arrival, proc)
                heapq.heapify(self._queue)
                return True
        return False

    def peek_next_process(self) -> Optional[Process]:
        """
        Consulta el siguiente proceso a ser despachado según prioridad y FIFO,
        sin extraerlo de la cola. Descarta automáticamente procesos obsoletos del tope.
        
        :return: El proceso candidato o None si la cola está vacía.
        """
        while self._queue and self._queue[0][2].state != ProcessState.READY:
            _, _, stale_process = heapq.heappop(self._queue)
            self._pid_set.discard(stale_process.pid)

        if self.is_empty:
            return None
        return self._queue[0][2]

    def get_next_process(self) -> Optional[Process]:
        """
        Extrae y retorna el siguiente proceso con mayor prioridad de la cola.
        Descarta automáticamente procesos obsoletos que ya no estén en estado READY.
        
        :return: El proceso extraído o None si la cola está vacía.
        """
        while not self.is_empty:
            _, _, process = heapq.heappop(self._queue)
            self._pid_set.discard(process.pid)
            if process.state == ProcessState.READY:
                return process
        return None

    def dispatch(self, cpu: CPU) -> Optional[Process]:
        """
        Intenta despachar el siguiente proceso de mayor prioridad a la CPU.
        
        Garantías de seguridad:
        - Si la CPU está ocupada (not cpu.is_idle), no extrae el proceso de la cola
          y retorna None de manera segura.
        - Si la cola está vacía, retorna None.
        - Si la CPU está libre, extrae el proceso de la cola y lo carga en la CPU
          (el proceso transiciona a RUNNING).
        - Si ocurriese cualquier error durante la carga, el proceso se reincorpora
          a la cola para garantizar cero pérdida de procesos.

        :param cpu: Instancia de la CPU receptora.
        :return: El proceso despachado, o None si no se pudo realizar el despacho.
        """
        if not isinstance(cpu, CPU):
            raise InvalidProcessAttributeError("El parámetro proporcionado debe ser una instancia de CPU.")

        # Si la CPU está ocupada, no hacemos nada (política no apropiativa / salvaguarda)
        if not cpu.is_idle:
            return None

        if self.is_empty:
            return None

        # Obtenemos el proceso de mayor prioridad
        process = self.get_next_process()
        if process is None:
            return None

        try:
            cpu.load_process(process)
            return process
        except Exception:
            # Reencolar en caso de error inesperado para prevenir pérdida del proceso
            if process.state == ProcessState.READY:
                self.add_process(process)
            raise

    def get_ready_processes(self) -> List[Process]:
        """
        Retorna una lista ordenada de todos los procesos en la cola de listos,
        siguiendo el orden exacto de selección (prioridad y FIFO).
        Descarta elementos que ya no se encuentren en estado READY.
        No modifica el orden relativo de los elementos válidos.
        """
        valid_entries = []
        for entry in self._queue:
            if entry[2].state == ProcessState.READY:
                valid_entries.append(entry)
            else:
                self._pid_set.discard(entry[2].pid)
        self._queue = valid_entries
        heapq.heapify(self._queue)

        sorted_entries = sorted(self._queue, key=lambda entry: (entry[0], entry[1]))
        return [entry[2] for entry in sorted_entries]


    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa el estado del planificador a un diccionario para el dashboard y Supabase.
        """
        return {
            "ready_count": self.ready_count,
            "is_empty": self.is_empty,
            "ready_processes": [p.to_dict() for p in self.get_ready_processes()],
        }

    def __repr__(self) -> str:
        next_pid = self.peek_next_process().pid if not self.is_empty else "None"
        return f"Scheduler(ready_count={self.ready_count}, next_pid={next_pid})"
