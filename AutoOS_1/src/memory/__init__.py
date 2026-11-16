"""
Subsistema de Memoria y Almacenamiento de AutoOS.

Contiene los componentes encargados de:

- Gestión de memoria RAM.
- Memoria virtual.
- Sistema de archivos.
- Almacenamiento persistente.
- Registro de eventos.
"""

from src.memory.memory import MemoryManager
from src.memory.virtual_memory import VirtualMemory
from src.memory.storage_manager import StorageManager
from src.memory.file_system import FileSystem
from src.memory.memory_log import MemoryLog

__all__ = [
    "MemoryManager",
    "VirtualMemory",
    "StorageManager",
    "FileSystem",
    "MemoryLog",
]