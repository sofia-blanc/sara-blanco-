"""
Módulo que implementa el Motor de Simulación (SimulationEngine) para AutoOS.
Coordina el reloj discreto, la CPU, el Scheduler y el EventLogger.
"""
from typing import Optional, Dict, Any, List
from src.core.process_state import ProcessState
from src.core.process import Process
from src.core.cpu import CPU
from src.core.scheduler import Scheduler
from src.core.event_logger import EventLogger
from src.core.exceptions import InvalidProcessAttributeError


class SimulationEngine:
    """
    Motor central de simulación para AutoOS.
    
    Orquesta el avance por ciclos de reloj (ticks lógicos), el despacho de procesos
    según la política no apropiativa del Scheduler y la ejecución en la CPU uninúcleo,
    registrando cada transición en la bitácora de auditoría.
    """

    def __init__(
        self,
        cpu: Optional[CPU] = None,
        scheduler: Optional[Scheduler] = None,
        logger: Optional[EventLogger] = None,
    ):
        """
        Inicializa el motor de simulación.

        :param cpu: Instancia de CPU (por defecto una nueva CPU).
        :param scheduler: Instancia de Scheduler (por defecto un nuevo Scheduler).
        :param logger: Instancia de EventLogger (por defecto un nuevo EventLogger).
        """
        self.cpu: CPU = cpu if cpu is not None else CPU()
        self.scheduler: Scheduler = scheduler if scheduler is not None else Scheduler()
        self.logger: EventLogger = logger if logger is not None else EventLogger()

        self._current_tick: int = 0
        self._is_paused: bool = False

        # Registro central de procesos administrados por el sistema
        self._processes: Dict[int, Process] = {}
        self._waiting_processes: Dict[int, Process] = {}
        self._terminated_processes: List[Process] = []

    # --- Propiedades de inspección del motor ---

    @property
    def current_tick(self) -> int:
        """Ciclo de reloj lógico actual de la simulación."""
        return self._current_tick

    @property
    def is_paused(self) -> bool:
        """Indica si la simulación se encuentra actualmente pausada."""
        return self._is_paused

    # --- Gestión y Admisión de Procesos ---

    def create_process(
        self,
        name: str,
        priority: int = 3,
        burst_time: int = 1,
        auto_admit: bool = True,
    ) -> Process:
        """
        Crea un nuevo proceso vehicular y lo registra en el sistema.
        Si auto_admit es True (por defecto), lo admite a READY y lo encola en el Scheduler.
        Si auto_admit es False, lo registra manteniéndolo en estado NEW.
        
        :return: La instancia de Process creada.
        """
        process = Process(name=name, priority=priority, burst_time=burst_time)
        if auto_admit:
            return self.submit_process(process)
        return self.register_process(process)

    def register_process(self, process: Process) -> Process:
        """
        Registra un proceso en el motor de simulación sin admitirlo a la cola de listos.
        Permite mantener procesos en estado NEW para su posterior admisión o cancelación.
        """
        if not isinstance(process, Process):
            raise InvalidProcessAttributeError("El parámetro proporcionado debe ser una instancia de Process.")

        self._processes[process.pid] = process
        self.logger.log(
            tick=self._current_tick,
            event_type="PROCESS_CREATED",
            message=f"Proceso PID={process.pid} ('{process.name}', Prio={process.priority}, Ráfaga={process.burst_time}) registrado en {process.state.value}",
            pid=process.pid,
            data=process.to_dict(),
        )
        return process


    def submit_process(self, process: Process) -> Process:
        """
        Registra un proceso existente en el motor y lo ingresa a la cola del planificador.
        Si el proceso está en NEW, lo transiciona a READY mediante admit().
        """
        if not isinstance(process, Process):
            raise InvalidProcessAttributeError("El parámetro proporcionado debe ser una instancia de Process.")

        self._processes[process.pid] = process

        # Si es un proceso recién creado en NEW, registramos creación y lo admitimos
        if process.state == ProcessState.NEW:
            self.logger.log(
                tick=self._current_tick,
                event_type="PROCESS_CREATED",
                message=f"Proceso PID={process.pid} ('{process.name}', Prio={process.priority}, Ráfaga={process.burst_time}) creado en NEW",
                pid=process.pid,
                data=process.to_dict(),
            )
            process.admit()

        # Encolar en el planificador
        self.scheduler.add_process(process)
        self.logger.log(
            tick=self._current_tick,
            event_type="PROCESS_ADMITTED",
            message=f"Proceso PID={process.pid} ('{process.name}') encolado en READY",
            pid=process.pid,
            data={"priority": process.priority},
        )
        return process

    # --- Control de Pausa y Reanudación ---

    def pause(self) -> None:
        """
        Pausa la simulación.
        Mientras esté pausada, los métodos tick() y run() no avanzarán el tiempo ni ejecutarán ciclos.
        """
        if not self._is_paused:
            self._is_paused = True
            self.logger.log(
                tick=self._current_tick,
                event_type="SIMULATION_PAUSED",
                message=f"Simulación pausada en el ciclo {self._current_tick}",
            )

    def resume(self) -> None:
        """
        Reanuda la simulación pausada, permitiendo que continúe el avance de ticks.
        """
        if self._is_paused:
            self._is_paused = False
            self.logger.log(
                tick=self._current_tick,
                event_type="SIMULATION_RESUMED",
                message=f"Simulación reanudada en el ciclo {self._current_tick}",
            )

    # --- Ciclo de Reloj y Ejecución ---

    def tick(self) -> bool:
        """
        Avanza exactamente un ciclo de reloj lógico de la simulación.
        
        Flujo de ejecución determinista:
        1. Si la simulación está pausada, retorna False inmediatamente sin avanzar.
        2. Incrementa el reloj lógico del sistema (current_tick += 1).
        3. Si la CPU está libre y hay procesos en la cola, despacha el proceso con mayor prioridad.
        4. Si hay un proceso en ejecución en la CPU, consume un ciclo de CPU:
           - Si el proceso agota su tiempo restante, pasa a TERMINATED y la CPU queda libre.
        5. Si la CPU está ociosa (sin procesos listos), ejecuta un ciclo ocioso contabilizado.

        :return: True si el tick se ejecutó normalmente, False si la simulación estaba pausada.
        """
        if self._is_paused:
            return False

        self._current_tick += 1

        # Paso A: Despacho a CPU si está libre
        if self.cpu.is_idle and not self.scheduler.is_empty:
            dispatched = self.scheduler.dispatch(self.cpu)
            if dispatched:
                self.logger.log(
                    tick=self._current_tick,
                    event_type="PROCESS_DISPATCHED",
                    message=(
                        f"Proceso PID={dispatched.pid} ('{dispatched.name}', "
                        f"Prio={dispatched.priority}) despachado a la CPU"
                    ),
                    pid=dispatched.pid,
                    data={"priority": dispatched.priority, "remaining_time": dispatched.remaining_time},
                )

        # Paso B: Consumo de ciclo de CPU
        if not self.cpu.is_idle:
            active_proc = self.cpu.current_process
            pid = active_proc.pid
            name = active_proc.name

            remaining = self.cpu.tick()
            self.logger.log(
                tick=self._current_tick,
                event_type="CPU_TICK",
                message=f"CPU ejecutó PID={pid} ('{name}'). Tiempo restante: {remaining}",
                pid=pid,
                data={"remaining_time": remaining},
            )

            # Si el proceso finalizó en este ciclo
            if active_proc.is_finished:
                if active_proc not in self._terminated_processes:
                    self._terminated_processes.append(active_proc)
                self.logger.log(
                    tick=self._current_tick,
                    event_type="PROCESS_TERMINATED",
                    message=f"Proceso PID={pid} ('{name}') finalizó su ejecución en el ciclo {self._current_tick}",
                    pid=pid,
                )
        else:
            # CPU ociosa en este ciclo (sin tareas para ejecutar)
            self.cpu.tick()
            self.logger.log(
                tick=self._current_tick,
                event_type="CPU_IDLE",
                message=f"CPU ociosa en el ciclo {self._current_tick} (sin procesos listos)",
            )

        return True

    def run(self, cycles: int) -> int:
        """
        Ejecuta una ráfaga de ciclos de reloj especificada de manera secuencial.
        Se detiene anticipadamente si la simulación es pausada.

        :param cycles: Número de ciclos a avanzar (> 0).
        :return: Cantidad real de ciclos ejecutados.
        """
        if isinstance(cycles, bool) or not isinstance(cycles, int) or cycles <= 0:
            raise InvalidProcessAttributeError("La cantidad de ciclos debe ser un entero mayor a cero.")

        executed_count = 0
        for _ in range(cycles):
            if self._is_paused:
                break
            success = self.tick()
            if success:
                executed_count += 1
            else:
                break

        return executed_count

    # --- Bloqueo, Desbloqueo y Terminación (Sensores y Control Vehicular) ---

    def block_current_process(self, reason: str = "Espera de sensor vehicular") -> Optional[Process]:
        """
        Bloquea el proceso activo en la CPU (RUNNING -> WAITING) y lo transfiere a la lista de espera.
        La CPU queda libre para despachar el siguiente proceso en el próximo ciclo.
        """
        if self.cpu.is_idle:
            return None

        process = self.cpu.block_process()
        if process:
            self._waiting_processes[process.pid] = process
            self.logger.log(
                tick=self._current_tick,
                event_type="PROCESS_BLOCKED",
                message=f"Proceso PID={process.pid} ('{process.name}') bloqueado en WAITING: {reason}",
                pid=process.pid,
                data={"reason": reason},
            )
        return process

    def unblock_process(self, pid: int) -> Process:
        """
        Desbloquea un proceso en espera (WAITING -> READY) y lo reencola en el Scheduler.
        """
        if pid not in self._waiting_processes:
            raise InvalidProcessAttributeError(f"El proceso PID={pid} no se encuentra en estado WAITING.")

        process = self._waiting_processes.pop(pid)
        process.unblock()
        self.scheduler.add_process(process)
        self.logger.log(
            tick=self._current_tick,
            event_type="PROCESS_UNBLOCKED",
            message=f"Proceso PID={pid} ('{process.name}') desbloqueado y reingresado a la cola READY",
            pid=pid,
        )
        return process

    def abort_process(self, pid: int) -> Process:
        """
        Aborta y finaliza forzosamente un proceso en cualquier estado activo (RUNNING, READY o WAITING).
        Transiciona el proceso a TERMINATED, libera la CPU o la cola de listos y registra el evento.
        """
        process = self._processes.get(pid)
        if process is None:
            raise InvalidProcessAttributeError(f"No existe ningún proceso registrado con PID={pid}.")

        if process.state == ProcessState.TERMINATED:
            return process

        if not self.cpu.is_idle and self.cpu.current_process.pid == pid:
            self.cpu.terminate_process()
        elif pid in self._waiting_processes:
            self._waiting_processes.pop(pid)
            process.terminate()
        elif process.state == ProcessState.READY:
            self.scheduler.remove_process(pid)
            process.terminate()
        elif process.state == ProcessState.NEW:
            process.terminate()

        if process not in self._terminated_processes:
            self._terminated_processes.append(process)

        self.logger.log(
            tick=self._current_tick,
            event_type="PROCESS_TERMINATED",
            message=f"Proceso PID={pid} ('{process.name}') abortado forzosamente en el ciclo {self._current_tick}",
            pid=pid,
            data={"aborted": True},
        )
        return process


    # --- Consulta y Estado General (Inmutable para Dashboard / Supabase) ---

    def get_process(self, pid: int) -> Optional[Process]:
        """
        Consulta un proceso registrado por su PID sin mutar su estado.
        Retorna None si el PID no existe en el registro del motor.
        """
        return self._processes.get(pid)

    def get_all_processes(self) -> List[Process]:
        """
        Retorna una copia de la lista de todos los procesos registrados en el sistema.
        """
        return list(self._processes.values())

    def get_status(self) -> Dict[str, Any]:

        """
        Genera una vista completa e inmutable del estado del sistema,
        diseñada para consumo del Dashboard web y persistencia en Supabase.
        """
        state_distribution = {state.value: 0 for state in ProcessState}
        for proc in self._processes.values():
            state_distribution[proc.state.value] += 1

        return {
            "current_tick": self._current_tick,
            "is_paused": self._is_paused,
            "cpu": self.cpu.to_dict(),
            "scheduler": self.scheduler.to_dict(),
            "process_distribution": state_distribution,
            "total_registered_processes": len(self._processes),
            "waiting_processes": [p.to_dict() for p in self._waiting_processes.values()],
            "terminated_processes": [p.to_dict() for p in self._terminated_processes],
            "total_events": self.logger.total_events,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Alias para get_status()."""
        return self.get_status()

    def __repr__(self) -> str:
        return (
            f"SimulationEngine(tick={self._current_tick}, paused={self._is_paused}, "
            f"cpu_idle={self.cpu.is_idle}, ready={self.scheduler.ready_count})"
        )
