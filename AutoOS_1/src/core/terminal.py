"""
Terminal interactiva de AutoOS (Shell de Sistema Operativo Vehicular).

Permite interactuar mediante línea de comandos con el estado real del simulador:
- Procesos (ps, kill, create)
- Memoria física y virtual (mem, vmem)
- Planificador (sched, step)
- Sistema de archivos (ls, cat, write, rm, mkdir)
- Arranque y diagnóstico (boot, status, help, clear)
"""
from typing import Optional, Dict, List, Any
import shlex

from src.core.kernel import Kernel
from src.core.process_state import ProcessState
from src.core.exceptions import AutoOSError


class TerminalResponse:
    """Representa la respuesta estructurada de un comando ejecutado en la terminal."""
    def __init__(self, command: str, output: str, success: bool = True, data: Optional[Dict[str, Any]] = None):
        self.command: str = command
        self.output: str = output
        self.success: bool = success
        self.data: Dict[str, Any] = data or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command": self.command,
            "output": self.output,
            "success": self.success,
            "data": self.data,
        }

    def __repr__(self) -> str:
        return f"TerminalResponse(cmd='{self.command}', success={self.success})"


class Terminal:
    """
    Intérprete de comandos (CLI) acoplado al núcleo de AutoOS.
    Ejecuta operaciones directamente sobre las instancias reales de los subsistemas.
    """

    def __init__(self, kernel: Optional[Kernel] = None):
        """
        Inicializa la terminal vinculada al Kernel de AutoOS.
        """
        self.kernel: Kernel = kernel if kernel is not None else Kernel()
        self._history: List[str] = []
        self._buffer: List[str] = []

    @property
    def history(self) -> List[str]:
        """Historial de comandos ejecutados."""
        return list(self._history)

    def execute(self, command_line: str) -> TerminalResponse:
        """
        Parsea y ejecuta una línea de comandos sobre el estado real de AutoOS.
        """
        raw_cmd = command_line.strip()
        if not raw_cmd:
            return TerminalResponse(command="", output="")

        self._history.append(raw_cmd)

        try:
            tokens = shlex.split(raw_cmd)
        except ValueError as err:
            return TerminalResponse(command=raw_cmd, output=f"Error de sintaxis: {err}", success=False)

        cmd = tokens[0].lower()
        args = tokens[1:]

        dispatcher = {
            "help": self._cmd_help,
            "boot": self._cmd_boot,
            "status": self._cmd_status,
            "ps": self._cmd_ps,
            "kill": self._cmd_kill,
            "create": self._cmd_create,
            "step": self._cmd_step,
            "sched": self._cmd_sched,
            "mem": self._cmd_mem,
            "vmem": self._cmd_vmem,
            "ls": self._cmd_ls,
            "cat": self._cmd_cat,
            "write": self._cmd_write,
            "rm": self._cmd_rm,
            "mkdir": self._cmd_mkdir,
            "clear": self._cmd_clear,
        }

        handler = dispatcher.get(cmd)
        if handler is None:
            msg = f"Comando no reconocido: '{cmd}'. Escriba 'help' para ver los comandos disponibles."
            return TerminalResponse(command=raw_cmd, output=msg, success=False)

        try:
            return handler(args, raw_cmd)
        except Exception as e:
            return TerminalResponse(command=raw_cmd, output=f"Error en ejecución: {e}", success=False)

    # --- Comandos del Sistema ---

    def _cmd_help(self, args: List[str], raw_cmd: str) -> TerminalResponse:
        help_text = (
            "Comandos disponibles en AutoOS Shell:\n"
            "  boot                        - Ejecuta la secuencia formal de arranque del sistema\n"
            "  status                      - Muestra el estado global de subsistemas y reloj\n"
            "  ps                          - Lista todos los procesos y su asignación de memoria\n"
            "  create <nom> <prio> <raf> [mem] - Crea y encola un nuevo proceso vehicular\n"
            "  kill <pid>                  - Aborta forzosamente un proceso y libera su memoria\n"
            "  step [ciclos]               - Avanza N ciclos de reloj lógico en la CPU\n"
            "  sched <alg> [quantum]       - Configura algoritmo (PRIORITY, FCFS, ROUND_ROBIN)\n"
            "  mem [map]                   - Muestra uso de RAM física y mapa de particiones\n"
            "  vmem <vaddr> [write]        - Traduce dirección virtual y reporta fallos/aciertos\n"
            "  ls [carpeta]                - Lista carpetas del VFS o archivos de una carpeta\n"
            "  cat <carpeta> <archivo>     - Muestra el contenido de un archivo\n"
            "  write <carp> <arch> <texto> - Escribe texto en un archivo del VFS\n"
            "  rm <carpeta> <archivo>      - Elimina un archivo del VFS\n"
            "  mkdir <carpeta>             - Crea un nuevo directorio en el VFS\n"
            "  clear                       - Limpia la pantalla de la terminal\n"
            "  help                        - Muestra este manual de ayuda"
        )
        return TerminalResponse(command=raw_cmd, output=help_text, success=True)

    def _cmd_boot(self, args: List[str], raw_cmd: str) -> TerminalResponse:
        result = self.kernel.boot()
        lines = [f"=== SECUENCIA DE BOOT: {result['status']} ==="]
        for stage in result.get("stages", []):
            lines.append(f"  [{stage['status']}] {stage['stage']}: {stage['description']}")
        lines.append(result["message"])
        return TerminalResponse(command=raw_cmd, output="\n".join(lines), success=True, data=result)

    def _cmd_status(self, args: List[str], raw_cmd: str) -> TerminalResponse:
        snap = self.kernel.get_system_snapshot()
        eng = snap["simulation"]
        mem = snap["memory_physical"]
        vmem = snap["memory_virtual"]
        lines = [
            "=== ESTADO DEL KERNEL AUTOOS ===",
            f"  Estado de Arranque: {'OPERACIONAL' if snap['is_booted'] else 'NO INICIALIZADO'}",
            f"  Ciclo de Reloj (Tick): {snap['tick']}",
            f"  CPU: {'LIBRE' if eng['cpu']['is_idle'] else f'OCUPADA (PID={eng['cpu']['current_process']['pid']})'}",
            f"  Procesos Totales: {eng['total_registered_processes']}",
            f"  Memoria RAM: {mem['used_memory']} MB usados / {mem['total_memory']} MB totales",
            f"  Memoria SWAP: {vmem['used_swap']} MB usados / {vmem['swap_size']} MB totales",
            f"  Paginación: {vmem['page_hits']} Hits, {vmem['page_faults']} Faults (Tasa: {vmem['hit_ratio']}%)",
            f"  Total Eventos Registrados: {snap['total_events']}",
        ]
        return TerminalResponse(command=raw_cmd, output="\n".join(lines), success=True, data=snap)

    def _cmd_ps(self, args: List[str], raw_cmd: str) -> TerminalResponse:
        procs = self.kernel.engine.get_all_processes()
        if not procs:
            return TerminalResponse(command=raw_cmd, output="No hay procesos registrados en el sistema.", success=True)

        header = f"{'PID':<5} {'NOMBRE':<24} {'PRIO':<6} {'ESTADO':<12} {'RÁFAGA':<10} {'RAM (MB)':<10}"
        sep = "-" * len(header)
        rows = [header, sep]

        for p in procs:
            alloc = self.kernel.memory_manager.get_process_allocation(p.pid)
            ram_info = f"{alloc.limit}MB" if alloc else "0MB"
            burst_info = f"{p.remaining_time}/{p.burst_time}"
            rows.append(
                f"{p.pid:<5} {p.name:<24} {p.priority:<6} {p.state.value:<12} {burst_info:<10} {ram_info:<10}"
            )

        return TerminalResponse(command=raw_cmd, output="\n".join(rows), success=True, data={"count": len(procs)})

    def _cmd_kill(self, args: List[str], raw_cmd: str) -> TerminalResponse:
        if not args:
            return TerminalResponse(command=raw_cmd, output="Uso: kill <PID>", success=False)
        try:
            pid = int(args[0])
        except ValueError:
            return TerminalResponse(command=raw_cmd, output=f"PID inválido: '{args[0]}'", success=False)

        try:
            aborted = self.kernel.engine.abort_process(pid)
            # También liberar marcos de paginación si los tuviera
            self.kernel.virtual_memory.release_process_pages(pid)
            msg = (
                f"Proceso PID={pid} ('{aborted.name}') terminado forzosamente. "
                f"Memoria RAM y recursos liberados. RAM libre actual: {self.kernel.memory_manager.free_memory} MB."
            )
            return TerminalResponse(command=raw_cmd, output=msg, success=True, data={"pid": pid})
        except AutoOSError as err:
            return TerminalResponse(command=raw_cmd, output=f"Error al terminar proceso: {err}", success=False)

    def _cmd_create(self, args: List[str], raw_cmd: str) -> TerminalResponse:
        if len(args) < 3:
            return TerminalResponse(
                command=raw_cmd,
                output="Uso: create <nombre> <prioridad 1-5> <ráfaga> [memoria_mb]",
                success=False,
            )
        name = args[0]
        try:
            prio = int(args[1])
            burst = int(args[2])
            mem = int(args[3]) if len(args) > 3 else 64
        except ValueError:
            return TerminalResponse(command=raw_cmd, output="Parámetros numéricos inválidos.", success=False)

        try:
            proc = self.kernel.engine.create_process(name=name, priority=prio, burst_time=burst, memory_size=mem)
            alloc = self.kernel.memory_manager.get_process_allocation(proc.pid)
            base_str = f"0x{alloc.base_address:04X}" if alloc else "N/A"
            msg = (
                f"Proceso creado exitosamente: PID={proc.pid} ('{proc.name}'), "
                f"Prio={proc.priority}, Ráfaga={proc.burst_time}, RAM={proc.memory_size}MB (Base: {base_str})"
            )
            return TerminalResponse(command=raw_cmd, output=msg, success=True, data=proc.to_dict())
        except AutoOSError as err:
            return TerminalResponse(command=raw_cmd, output=f"Fallo al crear proceso: {err}", success=False)

    def _cmd_step(self, args: List[str], raw_cmd: str) -> TerminalResponse:
        cycles = 1
        if args:
            try:
                cycles = int(args[0])
            except ValueError:
                return TerminalResponse(command=raw_cmd, output=f"Cantidad de ciclos inválida: '{args[0]}'", success=False)

        executed = self.kernel.engine.run(cycles)
        cpu_stat = (
            f"ejecutando PID={self.kernel.cpu.current_process.pid} ('{self.kernel.cpu.current_process.name}')"
            if not self.kernel.cpu.is_idle
            else "ociosa"
        )
        msg = f"Avanzados {executed} ciclo(s) de reloj. Ciclo actual: {self.kernel.engine.current_tick}. CPU {cpu_stat}."
        return TerminalResponse(command=raw_cmd, output=msg, success=True, data={"cycles": executed, "tick": self.kernel.engine.current_tick})

    def _cmd_sched(self, args: List[str], raw_cmd: str) -> TerminalResponse:
        if not args:
            curr = self.kernel.scheduler.algorithm
            q = self.kernel.scheduler.quantum
            return TerminalResponse(command=raw_cmd, output=f"Algoritmo activo: {curr} (Quantum: {q})", success=True)

        alg = args[0].upper()
        q = int(args[1]) if len(args) > 1 and args[1].isdigit() else 2
        try:
            self.kernel.scheduler.set_algorithm(alg, quantum=q)
            msg = f"Algoritmo de planificación actualizado a: {alg} (Quantum={q})"
            return TerminalResponse(command=raw_cmd, output=msg, success=True, data={"algorithm": alg, "quantum": q})
        except ValueError as err:
            return TerminalResponse(command=raw_cmd, output=f"Algoritmo no soportado: {err}", success=False)

    def _cmd_mem(self, args: List[str], raw_cmd: str) -> TerminalResponse:
        show_map = len(args) > 0 and args[0].lower() in ["map", "--map", "-m"]
        mem = self.kernel.memory_manager
        vmem = self.kernel.virtual_memory

        lines = [
            "=== MEMORIA FÍSICA (RAM) ===",
            f"  Total: {mem.total_memory} MB | Usada: {mem.used_memory} MB | Libre: {mem.free_memory} MB",
            f"  Bloques totales: {len(mem._blocks)} (Ocupados: {sum(1 for b in mem._blocks if not b.is_free)}, Libres: {sum(1 for b in mem._blocks if b.is_free)})",
            "=== MEMORIA VIRTUAL (SWAP & PAGINACIÓN) ===",
            f"  SWAP Total: {vmem.swap_size} MB | SWAP Usado: {vmem.used_swap} MB | SWAP Libre: {vmem.free_swap} MB",
            f"  Marcos físicos: {vmem.total_frames} (Tamaño de página: {vmem.page_size} MB)",
            f"  Aciertos: {vmem.page_hits} | Fallos: {vmem.page_faults} | Expulsiones: {vmem.page_replacements} | Tasa: {vmem.hit_ratio}%",
        ]

        if show_map:
            lines.append("--- MAPA DINÁMICO DE PARTICIONES CONTIGUAS ---")
            lines.append(f"{'DIRECCIÓN BASE':<16} {'LÍMITE':<10} {'DIR. FIN':<16} {'ESTADO':<10} {'PROPIETARIO'}")
            for b in mem.get_memory_map():
                base = f"0x{b['base_address']:08X}"
                end = f"0x{b['end_address']:08X}"
                lim = f"{b['limit']} MB"
                state = "LIBRE" if b["is_free"] else "OCUPADO"
                owner = f"PID={b['pid']} ({b['process_name']})" if not b["is_free"] else "Sistema (Disponible)"
                lines.append(f"{base:<16} {lim:<10} {end:<16} {state:<10} {owner}")

        return TerminalResponse(command=raw_cmd, output="\n".join(lines), success=True)

    def _cmd_vmem(self, args: List[str], raw_cmd: str) -> TerminalResponse:
        if not args:
            return TerminalResponse(command=raw_cmd, output="Uso: vmem <dirección_virtual> [write] [pid=1]", success=False)
        try:
            vaddr = int(args[0])
        except ValueError:
            return TerminalResponse(command=raw_cmd, output=f"Dirección virtual inválida: '{args[0]}'", success=False)

        is_write = len(args) > 1 and args[1].lower() in ["w", "write", "true"]
        pid = 1
        if len(args) > 2 and args[2].isdigit():
            pid = int(args[2])

        result = self.kernel.virtual_memory.translate_address(
            pid=pid,
            virtual_address=vaddr,
            current_tick=self.kernel.engine.current_tick,
            is_write=is_write,
        )

        kind = "FALLO DE PÁGINA (Page Fault)" if result["page_fault"] else "ACIERTO (Page Hit)"
        msg = (
            f"Traducción de Dirección:\n"
            f"  Dirección Virtual: {vaddr} (0x{vaddr:08X})\n"
            f"  Página: {result['page_number']}, Offset: {result['offset']}\n"
            f"  Marco Físico Asignado: {result['frame_number']}\n"
            f"  Dirección Física Traducida: {result['physical_address']} (0x{result['physical_address']:08X})\n"
            f"  Resultado: {kind}"
        )
        return TerminalResponse(command=raw_cmd, output=msg, success=True, data=result)

    def _cmd_ls(self, args: List[str], raw_cmd: str) -> TerminalResponse:
        fs = self.kernel.file_system
        if not args:
            dirs = fs.list_directories()
            lines = ["Directorios del sistema vehicular:"]
            for d in dirs:
                count = len(fs.list_files(d))
                lines.append(f"  /{d}/ ({count} archivos)")
            return TerminalResponse(command=raw_cmd, output="\n".join(lines), success=True)

        folder = args[0].strip("/")
        if not fs.folder_exists(folder):
            return TerminalResponse(command=raw_cmd, output=f"El directorio '/{folder}' no existe.", success=False)

        files = fs.list_files(folder)
        if not files:
            return TerminalResponse(command=raw_cmd, output=f"El directorio '/{folder}' está vacío.", success=True)

        lines = [f"Archivos en /{folder}/:"]
        for f in files:
            info = fs.get_file_info(folder, f) or {}
            size = info.get("size", 0)
            perm = info.get("permissions", "0644")
            lines.append(f"  {perm:<10} {size:<6} MB   {f}")
        return TerminalResponse(command=raw_cmd, output="\n".join(lines), success=True, data={"files": files})

    def _cmd_cat(self, args: List[str], raw_cmd: str) -> TerminalResponse:
        fs = self.kernel.file_system
        if not args:
            return TerminalResponse(command=raw_cmd, output="Uso: cat <carpeta> <archivo> o cat <carpeta/archivo>", success=False)

        if len(args) == 1 and "/" in args[0]:
            parts = args[0].strip("/").split("/", 1)
            folder, filename = parts[0], parts[1]
        elif len(args) >= 2:
            folder, filename = args[0].strip("/"), args[1]
        else:
            return TerminalResponse(command=raw_cmd, output="Uso: cat <carpeta> <archivo>", success=False)

        content = fs.read_file(folder, filename)
        if content is None:
            return TerminalResponse(command=raw_cmd, output=f"Archivo no encontrado: /{folder}/{filename}", success=False)

        return TerminalResponse(command=raw_cmd, output=content, success=True, data={"content": content})

    def _cmd_write(self, args: List[str], raw_cmd: str) -> TerminalResponse:
        if len(args) < 3:
            return TerminalResponse(command=raw_cmd, output="Uso: write <carpeta> <archivo> <contenido>", success=False)

        folder = args[0].strip("/")
        filename = args[1]
        content = " ".join(args[2:])

        success = self.kernel.file_system.write_file(folder, filename, content)
        if success:
            return TerminalResponse(
                command=raw_cmd,
                output=f"Archivo guardado exitosamente en /{folder}/{filename}",
                success=True,
            )
        return TerminalResponse(
            command=raw_cmd,
            output=f"No se pudo escribir el archivo. Carpeta '/{folder}' inexistente.",
            success=False,
        )

    def _cmd_rm(self, args: List[str], raw_cmd: str) -> TerminalResponse:
        if len(args) < 2:
            return TerminalResponse(command=raw_cmd, output="Uso: rm <carpeta> <archivo>", success=False)

        folder, filename = args[0].strip("/"), args[1]
        deleted = self.kernel.file_system.delete_file(folder, filename)
        if deleted:
            return TerminalResponse(command=raw_cmd, output=f"Archivo /{folder}/{filename} eliminado.", success=True)
        return TerminalResponse(command=raw_cmd, output=f"No se pudo eliminar /{folder}/{filename} (no encontrado).", success=False)

    def _cmd_mkdir(self, args: List[str], raw_cmd: str) -> TerminalResponse:
        if not args:
            return TerminalResponse(command=raw_cmd, output="Uso: mkdir <carpeta>", success=False)

        folder = args[0].strip("/")
        created = self.kernel.file_system.create_directory(folder)
        if created:
            return TerminalResponse(command=raw_cmd, output=f"Directorio /{folder} creado satisfactoriamente.", success=True)
        return TerminalResponse(command=raw_cmd, output=f"El directorio /{folder} ya existe.", success=False)

    def _cmd_clear(self, args: List[str], raw_cmd: str) -> TerminalResponse:
        self._buffer.clear()
        return TerminalResponse(command=raw_cmd, output="PANTALLA LIMPIA", success=True)
