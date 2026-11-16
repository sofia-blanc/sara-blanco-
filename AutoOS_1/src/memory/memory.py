"""
Gestor de memoria RAM de AutoOS.

Este módulo simula la memoria principal (RAM) utilizada por el vehículo
inteligente. Es responsable de:

- Asignar memoria a procesos.
- Liberar memoria cuando un proceso finaliza.
- Calcular memoria utilizada.
- Calcular memoria disponible.
- Detectar falta de memoria.

Ejemplos de procesos que consumen memoria:

- GPS
- Cámara
- Sensores
- Navegación
- Multimedia
- Comunicación

La memoria se expresa en MB (Megabytes).
"""


from typing import Optional, List, Dict, Any


class MemoryBlock:
    """
    Representa un bloque contiguo de memoria física con dirección base y límite (tamaño).
    Permite modelar el mapa de memoria con direccionamiento real y estado libre/ocupado.
    """
    def __init__(
        self,
        base_address: int,
        limit: int,
        is_free: bool = True,
        pid: Optional[int] = None,
        process_name: Optional[str] = None
    ):
        self.base_address: int = base_address  # Dirección base en MB (ej. 0, 64, 128)
        self.limit: int = limit                # Longitud/tamaño del bloque en MB
        self.is_free: bool = is_free           # True si está libre, False si está asignado
        self.pid: Optional[int] = pid          # PID del proceso propietario
        self.process_name: Optional[str] = process_name

    @property
    def end_address(self) -> int:
        """Dirección final inclusiva del bloque de memoria."""
        return self.base_address + self.limit - 1

    def to_dict(self) -> Dict[str, Any]:
        """Representación serializable del bloque."""
        return {
            "base_address": self.base_address,
            "limit": self.limit,
            "end_address": self.end_address,
            "is_free": self.is_free,
            "pid": self.pid,
            "process_name": self.process_name,
        }

    def __repr__(self) -> str:
        status = "FREE" if self.is_free else f"PID={self.pid} ('{self.process_name}')"
        return f"Block[0x{self.base_address:04X}..0x{self.end_address:04X}, {self.limit}MB, {status}]"


class MemoryManager:
    """
    Representa el gestor de memoria RAM física de AutoOS.

    Gestiona particiones dinámicas mediante bloques contiguos con dirección base
    y límite, aplicando asignación First-Fit, división de bloques y coalescencia
    automática al liberar para evitar la fragmentación externa.
    """

    def __init__(self, total_memory=4096):
        """
        Inicializa el gestor de memoria.

        :param total_memory: Memoria total instalada en MB (por defecto 4096 MB).
        """
        self._total_memory = total_memory
        # Inicialmente toda la memoria es un único bloque libre contiguo desde la dirección 0
        self._blocks: List[MemoryBlock] = [
            MemoryBlock(base_address=0, limit=total_memory, is_free=True)
        ]

    @property
    def total_memory(self) -> int:
        """Retorna la cantidad total de memoria RAM instalada en MB."""
        return self._total_memory

    @property
    def used_memory(self) -> int:
        """Retorna la memoria física actualmente ocupada en MB."""
        return sum(b.limit for b in self._blocks if not b.is_free)

    @property
    def free_memory(self) -> int:
        """Calcula la memoria física disponible en MB."""
        return sum(b.limit for b in self._blocks if b.is_free)

    def allocate_for_process(
        self,
        pid: int,
        size: int,
        process_name: str = ""
    ) -> Optional[MemoryBlock]:
        """
        Asigna un bloque contiguo de memoria a un proceso usando First-Fit.
        Divide el bloque libre si es mayor al tamaño solicitado.
        Previene doble asignación para el mismo PID.

        :param pid: Identificador del proceso.
        :param size: Cantidad de memoria requerida en MB (> 0).
        :param process_name: Nombre descriptivo del proceso.
        :return: El MemoryBlock asignado, o None si no hay suficiente memoria contigua.
        """
        if size <= 0:
            return None

        # Prevenir doble asignación para el mismo PID
        for b in self._blocks:
            if not b.is_free and b.pid == pid:
                return None

        # Estrategia First-Fit: buscar el primer bloque libre con capacidad suficiente
        for i, block in enumerate(self._blocks):
            if block.is_free and block.limit >= size:
                if block.limit == size:
                    # Coincidencia exacta
                    block.is_free = False
                    block.pid = pid
                    block.process_name = process_name
                    return block
                else:
                    # División de bloque (Split)
                    allocated_block = MemoryBlock(
                        base_address=block.base_address,
                        limit=size,
                        is_free=False,
                        pid=pid,
                        process_name=process_name
                    )
                    remaining_free = MemoryBlock(
                        base_address=block.base_address + size,
                        limit=block.limit - size,
                        is_free=True
                    )
                    self._blocks[i] = allocated_block
                    self._blocks.insert(i + 1, remaining_free)
                    return allocated_block

        return None

    def release_for_process(self, pid: int) -> bool:
        """
        Libera todos los bloques de memoria física asignados a un proceso por su PID.
        Aplica coalescencia (fusión) inmediata sobre bloques libres adyacentes.
        Previene doble liberación: retorna False si el proceso no tenía bloques asignados.

        :param pid: PID del proceso a liberar.
        :return: True si se liberó la memoria exitosamente, False si no existía asignación.
        """
        found = False
        for block in self._blocks:
            if not block.is_free and block.pid == pid:
                block.is_free = True
                block.pid = None
                block.process_name = None
                found = True

        if found:
            self._coalesce()
            return True
        return False

    def _coalesce(self) -> None:
        """
        Fusiona bloques libres contiguos en un solo bloque más grande
        para mitigar la fragmentación externa.
        """
        if not self._blocks:
            return

        coalesced: List[MemoryBlock] = [self._blocks[0]]
        for current in self._blocks[1:]:
            previous = coalesced[-1]
            if previous.is_free and current.is_free:
                # Fusión contigua
                previous.limit += current.limit
            else:
                coalesced.append(current)
        self._blocks = coalesced

    def get_memory_map(self) -> List[Dict[str, Any]]:
        """
        Retorna el mapa dinámico completo de bloques físicos (base, límite, estado, PID).
        """
        return [b.to_dict() for b in self._blocks]

    def get_process_allocation(self, pid: int) -> Optional[MemoryBlock]:
        """Consulta el bloque asignado a un PID específico."""
        for b in self._blocks:
            if not b.is_free and b.pid == pid:
                return b
        return None

    # --- Métodos de compatibilidad hacia atrás ---

    def allocate(self, size: int) -> bool:
        """
        Asignación anónima (compatibilidad hacia atrás con pruebas existentes).
        """
        block = self.allocate_for_process(pid=None, size=size, process_name="anonymous")
        return block is not None

    def release(self, size: int) -> bool:
        """
        Liberación de tamaño anónima (compatibilidad hacia atrás con pruebas existentes).
        """
        if size <= 0 or size > self.used_memory:
            return False

        rem = size
        for block in reversed(self._blocks):
            if not block.is_free:
                if block.limit <= rem:
                    rem -= block.limit
                    block.is_free = True
                    block.pid = None
                    block.process_name = None
                else:
                    block.limit -= rem
                    free_part = MemoryBlock(
                        base_address=block.base_address + block.limit,
                        limit=rem,
                        is_free=True
                    )
                    self._blocks.append(free_part)
                    rem = 0
                if rem == 0:
                    break

        self._coalesce()
        return True

    def has_enough_memory(self, required_memory: int) -> bool:
        """
        Verifica si existe al menos un bloque contiguo libre con capacidad suficiente.
        """
        if required_memory <= 0:
            return False
        return any(b.is_free and b.limit >= required_memory for b in self._blocks)

    def to_dict(self) -> Dict[str, Any]:
        """
        Genera representación serializable del estado de la memoria RAM y su mapa de bloques.
        """
        return {
            "total_memory": self.total_memory,
            "used_memory": self.used_memory,
            "free_memory": self.free_memory,
            "total_blocks": len(self._blocks),
            "free_blocks": sum(1 for b in self._blocks if b.is_free),
            "occupied_blocks": sum(1 for b in self._blocks if not b.is_free),
            "memory_map": self.get_memory_map(),
        }

    def __repr__(self) -> str:
        return (
            f"MemoryManager(total={self.total_memory} MB, "
            f"used={self.used_memory} MB, free={self.free_memory} MB, "
            f"blocks={len(self._blocks)})"
        )