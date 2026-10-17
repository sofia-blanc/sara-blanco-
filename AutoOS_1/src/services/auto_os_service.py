"""
Módulo de servicio de aplicación (AutoOSService).
Proporciona la interfaz de alto nivel para consumir el simulador de procesos y CPU
desde Dashboards web, APIs REST y adaptadores de persistencia (Supabase).
"""
from typing import Optional, List, Dict, Any
import json

from src.core.simulation import SimulationEngine

# Corrección realizada:
# Se importa Process porque se utiliza como anotación
# de tipo en el método register_process().
# Sin este import Python genera:
# NameError: name 'Process' is not defined

from src.core.process import Process

from src.dto.dtos import (
    ProcessDTO,
    CPUDTO,
    SchedulerDTO,
    EventDTO,
    SystemStatusDTO,
)


class AutoOSService:
    """
    Servicio de aplicación para AutoOS.
    
    Actúa como fachada (Facade Pattern), orquestando el SimulationEngine
    y devolviendo exclusivamente datos serializables a JSON (DTOs o diccionarios).
    Garantiza que el frontend no interactúe con referencias mutables internas.
    """

    def __init__(self, engine: Optional[SimulationEngine] = None):
        """
        Inicializa el servicio inyectando o creando un SimulationEngine.
        
        :param engine: Instancia opcional de SimulationEngine a reutilizar.
        """
        self._engine: SimulationEngine = engine if engine is not None else SimulationEngine()

    @property
    def engine(self) -> SimulationEngine:
        """Acceso al motor subyacente para inspección o configuración de bajo nivel."""
        return self._engine

    def get_system_status(self) -> Dict[str, Any]:
        """
        Retorna la instantánea completa del estado del sistema en formato diccionario JSON-serializable.
        """
        status_dto = SystemStatusDTO.from_engine(self._engine)
        return status_dto.to_dict()

    def get_system_status_json(self) -> str:
        """
        Retorna el estado del sistema serializado directamente en formato JSON (cadena de texto).
        Ideal para respuestas HTTP o mensajes WebSocket para el Dashboard.
        """
        return json.dumps(self.get_system_status())

    def create_process(
        self,
        name: str,
        priority: int = 3,
        burst_time: int = 1,
        auto_admit: bool = True,
    ) -> Dict[str, Any]:
        """
        Crea y registra un nuevo proceso en el sistema.
        Si auto_admit es True (por defecto), lo admite y encola en el Scheduler.
        Si auto_admit es False, lo registra manteniéndolo en estado NEW.
        
        :return: Diccionario serializable con los datos del proceso creado.
        """
        process = self._engine.create_process(
            name=name,
            priority=priority,
            burst_time=burst_time,
            auto_admit=auto_admit,
        )
        return ProcessDTO.from_process(process).to_dict()

    def register_process(self, process: Process) -> Dict[str, Any]:
        """
        Registra una instancia existente de Process sin admitirla a la cola de listos.
        
        :return: Diccionario serializable con los datos del proceso registrado.
        """
        registered = self._engine.register_process(process)
        return ProcessDTO.from_process(registered).to_dict()


    def get_process(self, pid: int) -> Optional[Dict[str, Any]]:
        """
        Consulta un proceso específico por su PID.
        
        :return: Diccionario del proceso o None si no existe.
        """
        process = self._engine.get_process(pid)
        if process is None:
            return None
        return ProcessDTO.from_process(process).to_dict()

    def get_all_processes(self) -> List[Dict[str, Any]]:
        """
        Retorna la lista de todos los procesos registrados en el sistema en formato diccionario.
        """
        processes = self._engine.get_all_processes()
        return [ProcessDTO.from_process(p).to_dict() for p in processes]

    def step(self) -> Dict[str, Any]:
        """
        Avanza exactamente un ciclo de simulación.
        
        :return: Resumen de la ejecución del tick.
        """
        success = self._engine.tick()
        return {
            "success": success,
            "current_tick": self._engine.current_tick,
            "is_paused": self._engine.is_paused,
            "cpu": CPUDTO.from_cpu(self._engine.cpu).to_dict(),
            "scheduler": SchedulerDTO.from_scheduler(self._engine.scheduler).to_dict(),
        }

    def run_cycles(self, cycles: int) -> Dict[str, Any]:
        """
        Ejecuta una ráfaga de ciclos continuos.
        
        :param cycles: Número de ciclos a ejecutar (> 0).
        :return: Resumen con la cantidad real de ciclos ejecutados y el nuevo ciclo actual.
        """
        executed = self._engine.run(cycles=cycles)
        return {
            "requested_cycles": cycles,
            "executed_cycles": executed,
            "current_tick": self._engine.current_tick,
            "is_paused": self._engine.is_paused,
        }

    def pause(self) -> Dict[str, Any]:
        """
        Pausa la simulación.
        """
        self._engine.pause()
        return {
            "is_paused": self._engine.is_paused,
            "current_tick": self._engine.current_tick,
        }

    def resume(self) -> Dict[str, Any]:
        """
        Reanuda la simulación.
        """
        self._engine.resume()
        return {
            "is_paused": self._engine.is_paused,
            "current_tick": self._engine.current_tick,
        }

    def block_current_process(self, reason: str = "Espera de sensor vehicular") -> Optional[Dict[str, Any]]:
        """
        Bloquea el proceso activo en la CPU (RUNNING -> WAITING).
        
        :return: Diccionario del proceso bloqueado, o None si la CPU estaba libre.
        """
        blocked = self._engine.block_current_process(reason=reason)
        if blocked is None:
            return None
        return ProcessDTO.from_process(blocked).to_dict()

    def unblock_process(self, pid: int) -> Dict[str, Any]:
        """
        Desbloquea el proceso especificado por PID y lo regresa a la cola de listos (WAITING -> READY).
        
        :return: Diccionario del proceso desbloqueado.
        """
        unblocked = self._engine.unblock_process(pid=pid)
        return ProcessDTO.from_process(unblocked).to_dict()

    def abort_process(self, pid: int) -> Dict[str, Any]:
        """
        Aborta y finaliza forzosamente un proceso por su PID en cualquier estado activo.
        
        :return: Diccionario del proceso abortado.
        """
        aborted = self._engine.abort_process(pid=pid)
        return ProcessDTO.from_process(aborted).to_dict()

    def update_process_priority(self, pid: int, new_priority: int) -> bool:
        """
        Actualiza la prioridad de un proceso en la cola de listos del Scheduler.
        
        :return: True si se actualizó con éxito, False si el proceso no estaba en la cola.
        """
        return self._engine.scheduler.update_process_priority(pid=pid, new_priority=new_priority)

    def get_events(
        self,
        pid: Optional[int] = None,
        event_type: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Consulta los eventos registrados con filtros opcionales por PID, tipo o límite cronológico.
        """
        events = self._engine.logger.get_events(pid=pid, event_type=event_type)
        if limit is not None and limit > 0:
            events = events[-limit:]
        return [EventDTO.from_event(e).to_dict() for e in events]

