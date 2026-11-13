"""
Memoria virtual de AutoOS.

Implementa un subsistema de memoria virtual y paginación completo con:
- Paginación física y lógica (páginas y marcos).
- Tablas de páginas por proceso (bits de validez, sucio y referencia).
- Traducción de direcciones virtuales a físicas con cálculo de offsets.
- Detección y tratamiento de fallos de página (Page Faults).
- Algoritmos de reemplazo de páginas (FIFO y LRU).
- Área de intercambio (SWAP) persistente para páginas expulsadas.
- Registro de auditoría de eventos de paginación.
"""
from typing import Optional, Dict, List, Any, Tuple
from collections import deque


class PageTableEntry:
    """
    Entrada de la tabla de páginas (PTE - Page Table Entry).
    Representa el mapeo entre una página virtual y su marco físico o ranura SWAP.
    """
    def __init__(
        self,
        page_number: int,
        frame_number: Optional[int] = None,
        is_valid: bool = False,
        is_dirty: bool = False,
        loaded_at_tick: int = 0,
        last_referenced_tick: int = 0,
        swap_slot: Optional[int] = None,
    ):
        self.page_number: int = page_number
        self.frame_number: Optional[int] = frame_number
        self.is_valid: bool = is_valid  # True = en RAM física, False = en SWAP o no residente
        self.is_dirty: bool = is_dirty  # True = modificada en RAM (requiere writeback a SWAP)
        self.loaded_at_tick: int = loaded_at_tick
        self.last_referenced_tick: int = last_referenced_tick
        self.swap_slot: Optional[int] = swap_slot

    def to_dict(self) -> Dict[str, Any]:
        """Serialización en diccionario."""
        return {
            "page_number": self.page_number,
            "frame_number": self.frame_number,
            "is_valid": self.is_valid,
            "is_dirty": self.is_dirty,
            "loaded_at_tick": self.loaded_at_tick,
            "last_referenced_tick": self.last_referenced_tick,
            "swap_slot": self.swap_slot,
        }

    def __repr__(self) -> str:
        loc = f"Frame={self.frame_number}" if self.is_valid else f"SWAP={self.swap_slot}"
        return f"PTE(P={self.page_number}, {loc}, Valid={self.is_valid}, Dirty={self.is_dirty})"


class VirtualMemory:
    """
    Gestor de memoria virtual, paginación y área de intercambio (SWAP) de AutoOS.

    Gestiona marcos de memoria física asignados a paginación, tablas de páginas
    por proceso, traducción de direcciones lógicas a físicas, detección de fallos
    de página y expulsión bajo algoritmos FIFO o LRU hacia el área SWAP.
    """

    def __init__(
        self,
        swap_size: int = 8192,
        page_size: int = 4,
        total_frames: int = 64,
        replacement_algorithm: str = "FIFO",
        logger: Optional[Any] = None,
    ):
        """
        Inicializa la memoria virtual y el subsistema de paginación.

        :param swap_size: Tamaño total del área SWAP en MB (por defecto 8192 MB).
        :param page_size: Tamaño de página y marco en MB (por defecto 4 MB).
        :param total_frames: Cantidad total de marcos físicos para paginación (por defecto 64).
        :param replacement_algorithm: Algoritmo de reemplazo ('FIFO' o 'LRU').
        :param logger: Instancia de EventLogger opcional para auditar eventos.
        """
        self._swap_size: int = swap_size
        self._used_swap: int = 0
        self.page_size: int = max(1, page_size)
        self.total_frames: int = max(1, total_frames)
        self._replacement_algorithm: str = replacement_algorithm.upper()
        if self._replacement_algorithm not in ["FIFO", "LRU"]:
            self._replacement_algorithm = "FIFO"
        self.logger = logger

        # Marcos físicos: índice de marco -> (pid, page_number) o None si está libre
        self._frames: List[Optional[Tuple[int, int]]] = [None] * self.total_frames

        # Tablas de páginas: pid -> Dict[page_number, PageTableEntry]
        self._page_tables: Dict[int, Dict[int, PageTableEntry]] = {}

        # Cola FIFO de marcos cargados: almacena frame_index en orden de llegada
        self._fifo_queue: deque = deque()

        # Contador de ranuras de SWAP asignadas
        self._next_swap_slot: int = 0

        # Métricas de rendimiento
        self._page_hits: int = 0
        self._page_faults: int = 0
        self._page_replacements: int = 0

    # --- Propiedades del Área SWAP (Compatibilidad 100%) ---

    @property
    def swap_size(self) -> int:
        """Tamaño total del área SWAP en MB."""
        return self._swap_size

    @property
    def used_swap(self) -> int:
        """Memoria virtual utilizada en el área SWAP en MB."""
        return self._used_swap

    @property
    def free_swap(self) -> int:
        """Memoria virtual disponible en el área SWAP en MB."""
        return max(0, self._swap_size - self._used_swap)

    @property
    def replacement_algorithm(self) -> str:
        """Algoritmo de reemplazo activo ('FIFO' o 'LRU')."""
        return self._replacement_algorithm

    @replacement_algorithm.setter
    def replacement_algorithm(self, alg: str) -> None:
        upper_alg = alg.upper()
        if upper_alg in ["FIFO", "LRU"]:
            self._replacement_algorithm = upper_alg

    @property
    def page_hits(self) -> int:
        """Cantidad total de accesos exitosos a páginas residentes (Page Hits)."""
        return self._page_hits

    @property
    def page_faults(self) -> int:
        """Cantidad total de fallos de página detectados (Page Faults)."""
        return self._page_faults

    @property
    def page_replacements(self) -> int:
        """Cantidad total de páginas expulsadas a SWAP por reemplazo."""
        return self._page_replacements

    @property
    def hit_ratio(self) -> float:
        """Tasa de aciertos de memoria virtual (0.0 a 100.0%)."""
        total = self._page_hits + self._page_faults
        if total == 0:
            return 100.0
        return round((self._page_hits / total) * 100, 2)

    # --- Gestión de Tablas de Páginas y Procesos ---

    def init_process_page_table(self, pid: int, num_pages: int) -> Dict[int, PageTableEntry]:
        """
        Inicializa la tabla de páginas para un proceso con un número dado de páginas virtuales.
        Inicialmente todas las páginas están en estado no residente (is_valid = False).
        """
        table: Dict[int, PageTableEntry] = {}
        for p in range(num_pages):
            table[p] = PageTableEntry(page_number=p, is_valid=False)
        self._page_tables[pid] = table
        return table

    def get_page_table(self, pid: int) -> Optional[Dict[int, PageTableEntry]]:
        """Retorna la tabla de páginas de un proceso o None si no existe."""
        return self._page_tables.get(pid)

    def release_process_pages(self, pid: int) -> None:
        """
        Libera todos los marcos físicos y ranuras SWAP asignadas a un proceso al finalizar.
        """
        table = self._page_tables.pop(pid, None)
        if not table:
            return

        # Liberar marcos físicos ocupados por el proceso
        for frame_idx, occupant in enumerate(self._frames):
            if occupant and occupant[0] == pid:
                self._frames[frame_idx] = None

        # Limpiar cola FIFO de marcos liberados
        self._fifo_queue = deque(
            f_idx for f_idx in self._fifo_queue
            if self._frames[f_idx] is not None
        )

        # Liberar SWAP ocupado por páginas del proceso
        swap_pages_freed = sum(1 for pte in table.values() if not pte.is_valid and pte.swap_slot is not None)
        self.release(swap_pages_freed * self.page_size)

    # --- Algoritmos de Reemplazo y Carga de Páginas ---

    def _find_free_frame(self) -> Optional[int]:
        """Busca el primer marco físico libre."""
        for idx, occupant in enumerate(self._frames):
            if occupant is None:
                return idx
        return None

    def _select_victim_frame(self) -> int:
        """
        Selecciona un marco víctima según la política de reemplazo configurada (FIFO o LRU).
        """
        if self._replacement_algorithm == "FIFO":
            # Extraer el marco más antiguo de la cola FIFO
            if self._fifo_queue:
                return self._fifo_queue.popleft()
            return 0
        else: # LRU (Least Recently Used)
            oldest_tick = float("inf")
            victim_frame = 0
            for idx, occupant in enumerate(self._frames):
                if occupant:
                    owner_pid, page_num = occupant
                    pte = self._page_tables.get(owner_pid, {}).get(page_num)
                    if pte and pte.last_referenced_tick < oldest_tick:
                        oldest_tick = pte.last_referenced_tick
                        victim_frame = idx
            return victim_frame

    def handle_page_fault(
        self,
        pid: int,
        page_number: int,
        current_tick: int = 0
    ) -> Tuple[int, Optional[Dict[str, Any]]]:
        """
        Atiende un fallo de página: asigna un marco físico libre o expulsa una página a SWAP.

        :param pid: PID del proceso solicitante.
        :param page_number: Número de página virtual requerida.
        :param current_tick: Ciclo de reloj actual.
        :return: Tupla (marco_asignado, datos_pagina_expulsada).
        """
        self._page_faults += 1
        table = self._page_tables.setdefault(pid, {})
        pte = table.setdefault(page_number, PageTableEntry(page_number=page_number))

        victim_info = None
        frame_idx = self._find_free_frame()

        if frame_idx is None:
            # No hay marcos libres: invocar política de reemplazo
            frame_idx = self._select_victim_frame()
            victim_pid, victim_page = self._frames[frame_idx]
            victim_pte = self._page_tables.get(victim_pid, {}).get(victim_page)

            if victim_pte:
                self._page_replacements += 1
                # Si la página víctima fue modificada o no tenía SWAP, guardarla en SWAP
                if victim_pte.is_dirty or victim_pte.swap_slot is None:
                    victim_pte.swap_slot = self._next_swap_slot
                    self._next_swap_slot += 1
                    self.allocate(self.page_size)

                victim_info = {
                    "victim_pid": victim_pid,
                    "victim_page": victim_page,
                    "frame": frame_idx,
                    "is_dirty": victim_pte.is_dirty,
                    "swap_slot": victim_pte.swap_slot,
                    "algorithm": self._replacement_algorithm,
                }

                # Invalidar la página víctima en RAM física
                victim_pte.is_valid = False
                victim_pte.frame_number = None

                if self.logger:
                    self.logger.log(
                        tick=current_tick,
                        event_type="PAGE_REPLACED",
                        message=(
                            f"Reemplazo de página ({self._replacement_algorithm}): "
                            f"Página {victim_page} de PID={victim_pid} expulsada a SWAP. "
                            f"Marco {frame_idx} liberado para PID={pid}."
                        ),
                        pid=pid,
                        data=victim_info,
                    )

        # Cargar la página requerida en el marco físico
        self._frames[frame_idx] = (pid, page_number)
        pte.frame_number = frame_idx
        pte.is_valid = True
        pte.loaded_at_tick = current_tick
        pte.last_referenced_tick = current_tick

        # Actualizar cola FIFO
        if frame_idx in self._fifo_queue:
            self._fifo_queue.remove(frame_idx)
        self._fifo_queue.append(frame_idx)

        if self.logger:
            self.logger.log(
                tick=current_tick,
                event_type="PAGE_FAULT",
                message=(
                    f"Fallo de página atendido: PID={pid}, Página {page_number} "
                    f"cargada en Marco {frame_idx}"
                ),
                pid=pid,
                data={
                    "pid": pid,
                    "page_number": page_number,
                    "frame_number": frame_idx,
                    "page_faults_total": self._page_faults,
                },
            )

        return frame_idx, victim_info

    # --- Traducción de Direcciones Virtuales ---

    def translate_address(
        self,
        pid: int,
        virtual_address: int,
        current_tick: int = 0,
        is_write: bool = False,
    ) -> Dict[str, Any]:
        """
        Traduce una dirección virtual lógica a una dirección física real en memoria.
        Detecta aciertos de página o desencadena el tratamiento de fallos de página.

        Fórmulas canónicas de paginación:
        page_number = virtual_address // page_size
        offset      = virtual_address % page_size
        physical_address = (frame_number * page_size) + offset
        """
        if virtual_address < 0:
            raise ValueError("La dirección virtual debe ser mayor o igual a cero.")

        page_number = virtual_address // self.page_size
        offset = virtual_address % self.page_size

        table = self._page_tables.setdefault(pid, {})
        pte = table.get(page_number)

        was_page_fault = False
        victim_info = None

        if pte is None or not pte.is_valid:
            # Fallo de página (Page Fault)
            was_page_fault = True
            frame_number, victim_info = self.handle_page_fault(pid, page_number, current_tick)
            pte = table[page_number]
        else:
            # Acierto de página (Page Hit)
            self._page_hits += 1
            frame_number = pte.frame_number
            pte.last_referenced_tick = current_tick
            if self.logger:
                self.logger.log(
                    tick=current_tick,
                    event_type="PAGE_HIT",
                    message=f"Acierto de página: PID={pid}, Página {page_number} en Marco {frame_number}",
                    pid=pid,
                    data={"page_number": page_number, "frame_number": frame_number},
                )

        if is_write:
            pte.is_dirty = True

        physical_address = (frame_number * self.page_size) + offset

        return {
            "pid": pid,
            "virtual_address": virtual_address,
            "page_number": page_number,
            "offset": offset,
            "physical_address": physical_address,
            "frame_number": frame_number,
            "page_fault": was_page_fault,
            "is_write": is_write,
            "victim_info": victim_info,
        }

    # --- Operaciones heredadas del área SWAP ---

    def allocate(self, size: int) -> bool:
        """Asigna memoria virtual anónima en el área SWAP."""
        if size <= 0 or size > self.free_swap:
            return False
        self._used_swap += size
        return True

    def release(self, size: int) -> bool:
        """Libera memoria virtual del área SWAP."""
        if size <= 0:
            return False
        self._used_swap -= size
        if self._used_swap < 0:
            self._used_swap = 0
        return True

    def has_enough_space(self, required_size: int) -> bool:
        """Verifica si existe espacio suficiente en el área SWAP."""
        return required_size <= self.free_swap

    def to_dict(self) -> Dict[str, Any]:
        """Genera una representación serializable completa del subsistema de memoria virtual."""
        return {
            "swap_size": self.swap_size,
            "used_swap": self.used_swap,
            "free_swap": self.free_swap,
            "page_size": self.page_size,
            "total_frames": self.total_frames,
            "occupied_frames": sum(1 for f in self._frames if f is not None),
            "free_frames": sum(1 for f in self._frames if f is None),
            "replacement_algorithm": self.replacement_algorithm,
            "page_hits": self.page_hits,
            "page_faults": self.page_faults,
            "page_replacements": self.page_replacements,
            "hit_ratio": self.hit_ratio,
            "active_page_tables": len(self._page_tables),
        }

    def __repr__(self) -> str:
        return (
            f"VirtualMemory(SWAP={self.used_swap}/{self.swap_size}MB, "
            f"Frames={sum(1 for f in self._frames if f is not None)}/{self.total_frames}, "
            f"Hits={self.page_hits}, Faults={self.page_faults}, Alg={self.replacement_algorithm})"
        )