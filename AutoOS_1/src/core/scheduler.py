"""
Módulo que implementa el Planificador de Procesos Multialgoritmo
(Priority Scheduling, FCFS, Round Robin) y gestión avanzada de cola
de listos para AutoOS con soporte de simuladores de Batería Baja y Procesos Críticos.
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

class AlgorithmType:
    PRIORITY = "PRIORITY"
    FCFS = "FCFS"
    ROUND_ROBIN = "ROUND_ROBIN"

class Scheduler:
    """
    Planificador de procesos multialgoritmo para AutoOS.
    Soporta:
      - Priority Scheduling (Prioridad min-heap, 1=Crítica, desempate FIFO)
      - FCFS (First-Come, First-Served estricto por orden de llegada)
      - Round Robin (Cola circular con Quantum de tiempo configurable)
      - Simulador de Batería Baja (Suspensión automática de procesos no esenciales)
      - Simulador de Proceso Crítico (Inyección ASIL-D con preemption)
    """

    def __init__(self, algorithm: str = AlgorithmType.PRIORITY, quantum: int = 2):
        """Inicializa el planificador con una cola de listos vacía."""
        self._algorithm: str = algorithm.upper()
        self._quantum: int = quantum
        self._quantum_remaining: int = quantum
        
        # Cola min-heap de tuplas: (clave_orden: int, orden_llegada: int, proceso: Process)
        self._queue: List[Tuple[int, int, Process]] = []
        # Conjunto de PIDs para verificación de duplicados en O(1)
        self._pid_set: Set[int] = set()
        # Contador secuencial para desempate FIFO estricto
        self._arrival_counter: int = 0
        
        # Modo Ahorro Energético (Batería Baja)
        self._low_battery_mode: bool = False
        self._suspended_battery_processes: Dict[int, Process] = {}

    @property
    def algorithm(self) -> str:
        return self._algorithm

    @algorithm.setter
    def algorithm(self, value: str) -> None:
        self.set_algorithm(value, self._quantum)

    @property
    def quantum(self) -> int:
        return self._quantum

    @property
    def quantum_remaining(self) -> int:
        return self._quantum_remaining

    @property
    def low_battery_mode(self) -> bool:
        return self._low_battery_mode

    @property
    def is_empty(self) -> bool:
        """Indica si la cola de listos está vacía."""
        return len(self._queue) == 0

    @property
    def ready_count(self) -> int:
        """Cantidad de procesos actualmente en espera en la cola de listos."""
        return len(self._queue)

    def set_algorithm(self, algorithm: str, quantum: int = 2) -> None:
        """Cambia el algoritmo de planificación y reordena la cola si es necesario."""
        alg = algorithm.upper()
        if alg not in [AlgorithmType.PRIORITY, AlgorithmType.FCFS, AlgorithmType.ROUND_ROBIN]:
            raise ValueError(f"Algoritmo no soportado: {algorithm}")
        self._algorithm = alg
        self._quantum = max(1, quantum)
        self._quantum_remaining = self._quantum
        self._rebuild_queue()

    def _rebuild_queue(self) -> None:
        """Reconstruye el montículo según el algoritmo activo."""
        old_procs = [entry[2] for entry in self._queue if entry[2].state == ProcessState.READY]
        self._queue = []
        self._pid_set = set()
        for p in old_procs:
            self.add_process(p)

    def add_process(self, process: Process) -> None:
        """
        Agrega un proceso en estado READY a la cola de listos del planificador.
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

        # Política de Batería Baja: si el proceso es no esencial (prioridad >= 4) y el modo está activo, suspenderlo
        if self._low_battery_mode and getattr(process, "priority", 3) >= 4:
            self._suspended_battery_processes[process.pid] = process
            return

        # Clave de ordenamiento según el algoritmo
        if self._algorithm == AlgorithmType.FCFS or self._algorithm == AlgorithmType.ROUND_ROBIN:
            key = self._arrival_counter
        else: # PRIORITY
            key = process.priority

        heapq.heappush(self._queue, (key, self._arrival_counter, process))
        self._pid_set.add(process.pid)
        self._arrival_counter += 1

    def remove_process(self, pid: int) -> Optional[Process]:
        """Retira un proceso de la cola de listos por su PID."""
        if pid in self._suspended_battery_processes:
            return self._suspended_battery_processes.pop(pid)

        if pid not in self._pid_set:
            return None
        self._pid_set.remove(pid)
        for i, (key, arrival, proc) in enumerate(self._queue):
            if proc.pid == pid:
                removed_proc = self._queue.pop(i)[2]
                heapq.heapify(self._queue)
                return removed_proc
        return None

    def update_process_priority(self, pid: int, new_priority: int) -> bool:
        """Actualiza la prioridad de un proceso que ya está en la cola de listos."""
        Process._validate_priority(new_priority)
        if pid not in self._pid_set:
            return False
        for i, (key, arrival, proc) in enumerate(self._queue):
            if proc.pid == pid:
                proc.priority = new_priority
                new_key = new_priority if self._algorithm == AlgorithmType.PRIORITY else arrival
                self._queue[i] = (new_key, arrival, proc)
                heapq.heapify(self._queue)
                return True
        return False

    def peek_next_process(self) -> Optional[Process]:
        """Consulta el siguiente proceso sin extraerlo de la cola."""
        while self._queue and self._queue[0][2].state != ProcessState.READY:
            _, _, stale_process = heapq.heappop(self._queue)
            self._pid_set.discard(stale_process.pid)
        if self.is_empty:
            return None
        return self._queue[0][2]

    def get_next_process(self) -> Optional[Process]:
        """Extrae y retorna el siguiente proceso de la cola según el algoritmo activo."""
        while not self.is_empty:
            _, _, process = heapq.heappop(self._queue)
            self._pid_set.discard(process.pid)
            if process.state == ProcessState.READY:
                return process
        return None

    def dispatch(self, cpu: CPU) -> Optional[Process]:
        """Intenta despachar el siguiente proceso a la CPU."""
        if not isinstance(cpu, CPU):
            raise InvalidProcessAttributeError("El parámetro proporcionado debe ser una instancia de CPU.")
        if not cpu.is_idle:
            return None
        if self.is_empty:
            return None

        process = self.get_next_process()
        if process is None:
            return None

        try:
            cpu.load_process(process)
            self._quantum_remaining = self._quantum
            return process
        except Exception:
            if process.state == ProcessState.READY:
                self.add_process(process)
            raise

    def handle_round_robin_tick(self, cpu: CPU) -> Optional[Process]:
        """
        Ejecuta 1 tick de CPU bajo Round Robin.
        Si expira el quantum y el proceso no ha terminado, desaloja y reencola al final.
        """
        if self._algorithm != AlgorithmType.ROUND_ROBIN or cpu.is_idle:
            return None

        self._quantum_remaining -= 1
        if self._quantum_remaining <= 0:
            preempted = cpu.preempt_process()
            if preempted:
                self.add_process(preempted)
                return self.dispatch(cpu)
        return None

    def inject_critical_process(self, process: Process, cpu: Optional[CPU] = None, preemptive: bool = True) -> Process:
        """
        Simulador de Proceso Crítico: Inyecta un proceso con prioridad 1 (ASIL-D).
        Si preemptive=True y la CPU está ejecutando un proceso de menor prioridad, lo desaloja de inmediato.
        """
        process.priority = 1
        if process.state != ProcessState.READY:
            if process.state == ProcessState.NEW:
                process.transition_to(ProcessState.READY)

        if preemptive and cpu and not cpu.is_idle:
            current = cpu.current_process
            if current and current.priority > 1:
                preempted = cpu.preempt_process()
                if preempted:
                    self.add_process(preempted)
                cpu.load_process(process)
                return process

        self.add_process(process)
        if cpu and cpu.is_idle:
            self.dispatch(cpu)
        return process

    def set_low_battery_mode(self, enabled: bool) -> List[int]:
        """
        Simulador de Batería Baja: Suspende procesos con prioridad >= 4 (multimedia/confort).
        Retorna la lista de PIDs afectados.
        """
        self._low_battery_mode = enabled
        affected_pids = []

        if enabled:
            ready_procs = self.get_ready_processes()
            for p in ready_procs:
                if getattr(p, "priority", 3) >= 4:
                    self.remove_process(p.pid)
                    self._suspended_battery_processes[p.pid] = p
                    affected_pids.append(p.pid)
        else:
            for pid, proc in list(self._suspended_battery_processes.items()):
                if proc.state != ProcessState.READY:
                    try:
                        proc.transition_to(ProcessState.READY)
                    except Exception:
                        pass
                self.add_process(proc)
                affected_pids.append(pid)
            self._suspended_battery_processes.clear()

        return affected_pids

    def get_ready_processes(self) -> List[Process]:
        """Retorna una lista ordenada de todos los procesos en la cola de listos."""
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
        """Serializa el estado del planificador a un diccionario."""
        return {
            "algorithm": self._algorithm,
            "quantum": self._quantum,
            "quantum_remaining": self._quantum_remaining,
            "low_battery_mode": self._low_battery_mode,
            "ready_count": self.ready_count,
            "suspended_count": len(self._suspended_battery_processes),
            "is_empty": self.is_empty,
            "ready_processes": [p.to_dict() for p in self.get_ready_processes()],
        }

    def __repr__(self) -> str:
        next_pid = self.peek_next_process().pid if not self.is_empty else "None"
        return f"Scheduler(algorithm={self._algorithm}, ready_count={self.ready_count}, next_pid={next_pid})"
