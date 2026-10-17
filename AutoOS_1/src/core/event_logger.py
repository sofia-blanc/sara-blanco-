"""
Módulo que implementa el registro de eventos y auditoría para AutoOS.
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Event:
    """
    Representa un evento registrado durante el ciclo de vida de la simulación de AutoOS.
    
    Campos:
    - tick: Ciclo de reloj en el que ocurrió el evento.
    - event_type: Categoría canónica del evento (ej. 'PROCESS_CREATED', 'CPU_TICK').
    - message: Descripción legible para el operador o consola.
    - pid: Identificador del proceso involucrado, si aplica.
    - data: Diccionario auxiliar de metadatos (preparado para Supabase/Dashboard).
    """
    tick: int
    event_type: str
    message: str
    pid: Optional[int] = None
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el evento a un formato de diccionario plano JSON-serializable."""
        return {
            "tick": self.tick,
            "event_type": self.event_type,
            "message": self.message,
            "pid": self.pid,
            "data": self.data,
        }


class EventLogger:
    """
    Bitácora de auditoría que recopila todos los eventos del sistema operativo en orden cronológico.
    """

    def __init__(self):
        """Inicializa una bitácora de eventos vacía."""
        self._events: List[Event] = []

    def log(
        self,
        tick: int,
        event_type: str,
        message: str,
        pid: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Event:
        """
        Registra un nuevo evento en la bitácora.
        
        :return: La instancia de Event recién creada.
        """
        event = Event(
            tick=tick,
            event_type=event_type,
            message=message,
            pid=pid,
            data=data or {},
        )
        self._events.append(event)
        return event

    def get_events(
        self,
        pid: Optional[int] = None,
        event_type: Optional[str] = None,
    ) -> List[Event]:
        """
        Retorna una lista de eventos, opcionalmente filtrados por PID y/o tipo de evento.
        """
        result = self._events
        if pid is not None:
            result = [e for e in result if e.pid == pid]
        if event_type is not None:
            result = [e for e in result if e.event_type == event_type]
        return list(result)

    @property
    def total_events(self) -> int:
        """Cantidad total de eventos registrados."""
        return len(self._events)

    def to_list(self) -> List[Dict[str, Any]]:
        """Exporta todos los eventos a una lista de diccionarios JSON-serializables."""
        return [e.to_dict() for e in self._events]

    def clear(self) -> None:
        """Limpia los eventos registrados en la bitácora."""
        self._events.clear()

    def __repr__(self) -> str:
        return f"EventLogger(total_events={self.total_events})"
