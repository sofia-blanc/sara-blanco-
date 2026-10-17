"""
Objetos de Transferencia de Datos (DTOs - Data Transfer Objects) para AutoOS.
Estructuras desacopladas y 100% serializables a JSON para consumo de APIs,
Dashboards web y persistencia en Supabase.
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from src.core.process import Process
from src.core.cpu import CPU
from src.core.scheduler import Scheduler
from src.core.event_logger import Event
from src.core.simulation import SimulationEngine


@dataclass
class ProcessDTO:
    """Representación serializable del Bloque de Control de Proceso (PCB)."""
    pid: int
    name: str
    priority: int
    state: str
    burst_time: int
    remaining_time: int
    is_finished: bool

    @classmethod
    def from_process(cls, process: Process) -> "ProcessDTO":
        """Crea un DTO inmutable a partir de una entidad Process del núcleo."""
        return cls(
            pid=process.pid,
            name=process.name,
            priority=process.priority,
            state=process.state.value,
            burst_time=process.burst_time,
            remaining_time=process.remaining_time,
            is_finished=process.is_finished,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el DTO a un diccionario plano compatible con JSON."""
        return {
            "pid": self.pid,
            "name": self.name,
            "priority": self.priority,
            "state": self.state,
            "burst_time": self.burst_time,
            "remaining_time": self.remaining_time,
            "is_finished": self.is_finished,
        }


@dataclass
class CPUDTO:
    """Representación serializable del estado y las métricas de la CPU."""
    is_idle: bool
    current_process: Optional[ProcessDTO]
    total_ticks: int
    busy_ticks: int
    idle_ticks: int
    utilization_percentage: float

    @classmethod
    def from_cpu(cls, cpu: CPU) -> "CPUDTO":
        """Construye un DTO a partir de la CPU simulada."""
        proc_dto = ProcessDTO.from_process(cpu.current_process) if cpu.current_process else None
        utilization = 0.0
        if cpu.total_ticks > 0:
            utilization = round((cpu.busy_ticks / cpu.total_ticks) * 100, 2)

        return cls(
            is_idle=cpu.is_idle,
            current_process=proc_dto,
            total_ticks=cpu.total_ticks,
            busy_ticks=cpu.busy_ticks,
            idle_ticks=cpu.idle_ticks,
            utilization_percentage=utilization,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el DTO a un diccionario plano compatible con JSON."""
        return {
            "is_idle": self.is_idle,
            "current_process": self.current_process.to_dict() if self.current_process else None,
            "total_ticks": self.total_ticks,
            "busy_ticks": self.busy_ticks,
            "idle_ticks": self.idle_ticks,
            "utilization_percentage": self.utilization_percentage,
        }


@dataclass
class SchedulerDTO:
    """Representación serializable de la cola de listos del planificador."""
    ready_count: int
    is_empty: bool
    ready_processes: List[ProcessDTO]

    @classmethod
    def from_scheduler(cls, scheduler: Scheduler) -> "SchedulerDTO":
        """Construye un DTO a partir del Scheduler existente."""
        return cls(
            ready_count=scheduler.ready_count,
            is_empty=scheduler.is_empty,
            ready_processes=[ProcessDTO.from_process(p) for p in scheduler.get_ready_processes()],
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el DTO a un diccionario plano compatible con JSON."""
        return {
            "ready_count": self.ready_count,
            "is_empty": self.is_empty,
            "ready_processes": [p.to_dict() for p in self.ready_processes],
        }


@dataclass
class EventDTO:
    """Representación serializable de un evento de auditoría."""
    tick: int
    event_type: str
    message: str
    pid: Optional[int] = None
    data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_event(cls, event: Event) -> "EventDTO":
        """Construye un DTO a partir de una entidad Event."""
        return cls(
            tick=event.tick,
            event_type=event.event_type,
            message=event.message,
            pid=event.pid,
            data=event.data,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el DTO a un diccionario plano compatible con JSON."""
        return {
            "tick": self.tick,
            "event_type": self.event_type,
            "message": self.message,
            "pid": self.pid,
            "data": self.data,
        }


@dataclass
class SystemStatusDTO:
    """Representación agregada de todo el estado del sistema operativo."""
    current_tick: int
    is_paused: bool
    cpu: CPUDTO
    scheduler: SchedulerDTO
    process_distribution: Dict[str, int]
    total_registered_processes: int
    waiting_processes: List[ProcessDTO]
    terminated_processes: List[ProcessDTO]
    total_events: int

    @classmethod
    def from_engine(cls, engine: SimulationEngine) -> "SystemStatusDTO":
        """Construye una instantánea global completa a partir del SimulationEngine."""
        raw_status = engine.get_status()
        return cls(
            current_tick=engine.current_tick,
            is_paused=engine.is_paused,
            cpu=CPUDTO.from_cpu(engine.cpu),
            scheduler=SchedulerDTO.from_scheduler(engine.scheduler),
            process_distribution=raw_status["process_distribution"],
            total_registered_processes=raw_status["total_registered_processes"],
            waiting_processes=[
                ProcessDTO.from_process(p)
                for p in engine.get_all_processes()
                if p.state.value == "WAITING"
            ],
            terminated_processes=[
                ProcessDTO.from_process(p)
                for p in engine.get_all_processes()
                if p.state.value == "TERMINATED"
            ],
            total_events=raw_status["total_events"],
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el estado completo a un diccionario anidado compatible con JSON."""
        return {
            "current_tick": self.current_tick,
            "is_paused": self.is_paused,
            "cpu": self.cpu.to_dict(),
            "scheduler": self.scheduler.to_dict(),
            "process_distribution": self.process_distribution,
            "total_registered_processes": self.total_registered_processes,
            "waiting_processes": [p.to_dict() for p in self.waiting_processes],
            "terminated_processes": [p.to_dict() for p in self.terminated_processes],
            "total_events": self.total_events,
        }
