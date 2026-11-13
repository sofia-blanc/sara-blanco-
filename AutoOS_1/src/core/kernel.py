"""
Módulo del Núcleo Central (Kernel) de AutoOS.

Responsabilidades:
- Centralizar e integrar todos los subsistemas del vehículo inteligente:
  CPU, Memoria Física (MemoryManager), Memoria Virtual (VirtualMemory),
  Sistema de Archivos Persistente (FileSystem), Planificador (Scheduler),
  Motor de Simulación (SimulationEngine) y Bitácora Central (EventLogger).
- Implementar la secuencia formal de arranque (Boot) con registro detallado de etapas.
- Garantizar inicialización única sin redundancias.
- Proveer apagado controlado (Shutdown) con sincronización de almacenamiento a disco.
"""
from typing import Optional, Dict, List, Any
import time

from src.core.cpu import CPU
from src.core.scheduler import Scheduler, AlgorithmType
from src.core.event_logger import EventLogger
from src.core.simulation import SimulationEngine
from src.memory.memory import MemoryManager
from src.memory.virtual_memory import VirtualMemory
from src.memory.file_system import FileSystem


class Kernel:
    """
    Núcleo operativo de AutoOS.
    Punto de convergencia central que coordina los subsistemas del vehículo.
    """

    BOOT_STAGES = [
        ("POST", "Power-On Self-Test: Diagnóstico de registros CPU y bus de instrucciones"),
        ("MEMORY_INIT", "Inicialización de gestor de memoria RAM y particiones físicas"),
        ("VMEM_INIT", "Inicialización de paginación virtual, tablas de páginas y área SWAP"),
        ("VFS_MOUNT", "Montaje del sistema de archivos persistente (/system, /config, /logs)"),
        ("SCHEDULER_INIT", "Configuración del planificador de tareas vehiculares y colas de prioridad"),
        ("DAEMONS_SPAWN", "Carga de procesos demonio esenciales del vehículo (BMS, CAN, ADAS)"),
        ("SYSTEM_READY", "AutoOS operacional: kernel vehicular en estado listo para ejecución"),
    ]

    def __init__(
        self,
        memory_mb: int = 4096,
        swap_mb: int = 8192,
        vfs_path: Optional[str] = None,
        scheduler_algorithm: str = AlgorithmType.PRIORITY,
    ):
        """
        Inicializa la estructura del kernel y sus subsistemas.
        """
        self.logger = EventLogger()
        self.cpu = CPU()
        self.scheduler = Scheduler(algorithm=scheduler_algorithm)
        self.memory_manager = MemoryManager(total_memory=memory_mb)
        self.virtual_memory = VirtualMemory(
            swap_size=swap_mb,
            page_size=4,
            total_frames=64,
            replacement_algorithm="FIFO",
            logger=self.logger,
        )
        self.file_system = FileSystem(storage_path=vfs_path, auto_load=True)

        # Motor de simulación centralizado
        self.engine = SimulationEngine(
            cpu=self.cpu,
            scheduler=self.scheduler,
            logger=self.logger,
            memory_manager=self.memory_manager,
        )

        self._is_booted: bool = False
        self._boot_log: List[Dict[str, Any]] = []
        self._boot_timestamp: Optional[str] = None

    @property
    def is_booted(self) -> bool:
        """Indica si el kernel ya completó su secuencia de boot."""
        return self._is_booted

    @property
    def boot_log(self) -> List[Dict[str, Any]]:
        """Historial de etapas registradas durante el arranque."""
        return list(self._boot_log)

    def boot(self) -> Dict[str, Any]:
        """
        Ejecuta la secuencia formal de arranque del sistema operativo vehicular.
        Registra cada fase en el EventLogger y previene inicializaciones duplicadas.
        """
        if self._is_booted:
            return {
                "status": "ALREADY_BOOTED",
                "message": "AutoOS ya se encuentra inicializado y operativo.",
                "stages": self._boot_log,
            }

        self._boot_log.clear()
        self._boot_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        for stage_code, stage_desc in self.BOOT_STAGES:
            stage_entry = {
                "stage": stage_code,
                "description": stage_desc,
                "tick": self.engine.current_tick,
                "status": "OK",
            }

            # Acciones específicas por fase
            if stage_code == "VFS_MOUNT":
                # Crear archivos base de configuración vehicular si no existen
                if not self.file_system.file_exists("config", "vehicle_params.json"):
                    self.file_system.create_file(
                        "config",
                        "vehicle_params.json",
                        size=2,
                        content='{"mode": "AUTONOMOUS_L3", "max_speed_kmh": 140, "battery_cutoff_pct": 10}',
                    )
                if not self.file_system.file_exists("logs", "boot.log"):
                    self.file_system.create_file(
                        "logs",
                        "boot.log",
                        size=1,
                        content=f"[{self._boot_timestamp}] Kernel boot sequence initialized.\n",
                    )
                else:
                    self.file_system.write_file(
                        "logs",
                        "boot.log",
                        f"[{self._boot_timestamp}] Kernel reboot sequence initiated.\n",
                        mode="a",
                    )

            elif stage_code == "DAEMONS_SPAWN":
                # Lanzar demonios críticos del vehículo
                self.engine.create_process(name="BMS_Battery_Monitor", priority=1, burst_time=10, memory_size=64)
                self.engine.create_process(name="CAN_Bus_Gateway", priority=1, burst_time=8, memory_size=64)
                self.engine.create_process(name="ADAS_Vision_Pilot", priority=2, burst_time=6, memory_size=128)
                self.engine.create_process(name="Telemetry_Cloud_Node", priority=3, burst_time=4, memory_size=32)

            self._boot_log.append(stage_entry)
            self.logger.log(
                tick=self.engine.current_tick,
                event_type=f"BOOT_{stage_code}",
                message=f"[BOOT] {stage_code}: {stage_desc}",
                data=stage_entry,
            )

        self._is_booted = True
        return {
            "status": "BOOT_SUCCESS",
            "message": "Secuencia de arranque de AutoOS completada satisfactoriamente.",
            "boot_timestamp": self._boot_timestamp,
            "stages_completed": len(self._boot_log),
            "stages": self._boot_log,
        }

    def shutdown(self) -> Dict[str, Any]:
        """
        Ejecuta el apagado seguro del kernel vehicular.
        Sincroniza el VFS a disco y libera recursos.
        """
        if not self._is_booted:
            return {"status": "NOT_BOOTED", "message": "El sistema no está en ejecución."}

        # Registrar apagado en el archivo de log
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        self.file_system.write_file(
            "logs",
            "boot.log",
            f"[{now}] Kernel shutdown safely executed. VFS synced.\n",
            mode="a",
        )
        self.file_system.save_to_disk()

        self.logger.log(
            tick=self.engine.current_tick,
            event_type="KERNEL_SHUTDOWN",
            message="AutoOS Kernel apagado de manera ordenada. Recursos sincronizados.",
        )

        self._is_booted = False
        return {
            "status": "SHUTDOWN_SUCCESS",
            "message": "AutoOS apagado satisfactoriamente.",
            "final_tick": self.engine.current_tick,
        }

    def get_system_snapshot(self) -> Dict[str, Any]:
        """Retorna una instantánea completa de todos los subsistemas del kernel."""
        return {
            "is_booted": self._is_booted,
            "boot_timestamp": self._boot_timestamp,
            "tick": self.engine.current_tick,
            "simulation": self.engine.get_status(),
            "memory_physical": self.memory_manager.to_dict(),
            "memory_virtual": self.virtual_memory.to_dict(),
            "filesystem": self.file_system.to_dict(),
            "total_events": self.logger.total_events,
        }

    def __repr__(self) -> str:
        status = "BOOTED" if self._is_booted else "UNBOOTED"
        return f"Kernel(Status={status}, Tick={self.engine.current_tick}, Processes={len(self.engine.get_all_processes())})"
