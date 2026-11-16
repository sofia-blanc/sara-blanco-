"""
Pruebas unitarias para el Núcleo (Kernel) y la Terminal interactiva de AutoOS.

Verifica:
1. Secuencia formal de arranque (Boot) con registro de todas sus etapas.
2. Prevención de arranque duplicado (idempotencia).
3. Apagado controlado (Shutdown) y persistencia del VFS.
4. Terminal: comando 'help'.
5. Terminal: comando 'boot' ejecutado sobre el Kernel.
6. Terminal: comando 'ps' mostrando procesos reales y RAM.
7. Terminal: comando 'create' registrando procesos con memoria en el simulador.
8. Terminal: comando 'step' avanzando ciclos reales de CPU.
9. Terminal: comando 'sched' modificando algoritmo de planificación.
10. Terminal: comando 'mem' y 'mem map' mostrando el mapa dinámico contiguo.
11. Terminal: comando 'kill' abortando procesos y liberando recursos.
12. Terminal: comandos de archivos 'write', 'cat', 'ls', 'rm', 'mkdir'.
13. Terminal: comando 'vmem' traduciendo direcciones y detectando fallos de página.
"""
import unittest

from src.core.kernel import Kernel
from src.core.terminal import Terminal
from src.core.process_state import ProcessState


class TestKernelAndTerminal(unittest.TestCase):
    def setUp(self):
        self.kernel = Kernel(memory_mb=1024, swap_mb=2048)
        self.terminal = Terminal(kernel=self.kernel)

    def test_1_formal_boot_sequence_and_stages(self):
        """1. Secuencia formal de arranque: registra todas las etapas y demonios."""
        self.assertFalse(self.kernel.is_booted)
        res = self.kernel.boot()
        self.assertEqual(res["status"], "BOOT_SUCCESS")
        self.assertTrue(self.kernel.is_booted)
        self.assertEqual(len(res["stages"]), 7)

        # Verificar que se crearon los demonios vehiculares
        procs = self.kernel.engine.get_all_processes()
        names = [p.name for p in procs]
        self.assertIn("BMS_Battery_Monitor", names)
        self.assertIn("CAN_Bus_Gateway", names)
        self.assertIn("ADAS_Vision_Pilot", names)
        self.assertIn("Telemetry_Cloud_Node", names)

        # Verificar que cada demonio tiene memoria física asignada
        self.assertGreater(self.kernel.memory_manager.used_memory, 0)

    def test_2_prevention_of_duplicate_boot(self):
        """2. Prevención de inicializaciones duplicadas."""
        self.kernel.boot()
        second_boot = self.kernel.boot()
        self.assertEqual(second_boot["status"], "ALREADY_BOOTED")

    def test_3_kernel_shutdown(self):
        """3. Apagado controlado del Kernel."""
        self.kernel.boot()
        res = self.kernel.shutdown()
        self.assertEqual(res["status"], "SHUTDOWN_SUCCESS")
        self.assertFalse(self.kernel.is_booted)

    def test_4_terminal_help_and_boot(self):
        """4. Terminal: ayuda y ejecución del boot interactivo."""
        help_resp = self.terminal.execute("help")
        self.assertTrue(help_resp.success)
        self.assertIn("boot", help_resp.output)
        self.assertIn("kill", help_resp.output)

        boot_resp = self.terminal.execute("boot")
        self.assertTrue(boot_resp.success)
        self.assertIn("SECUENCIA DE BOOT: BOOT_SUCCESS", boot_resp.output)
        self.assertTrue(self.kernel.is_booted)

    def test_5_terminal_ps_and_create(self):
        """5. Terminal: listado 'ps' y creación interactiva 'create'."""
        self.terminal.execute("boot")
        ps_resp = self.terminal.execute("ps")
        self.assertTrue(ps_resp.success)
        self.assertIn("BMS_Battery_Monitor", ps_resp.output)

        # Crear nuevo proceso mediante la terminal
        create_resp = self.terminal.execute("create Frenado_ABS 1 4 64")
        self.assertTrue(create_resp.success)
        self.assertIn("Frenado_ABS", create_resp.output)
        self.assertIn("64MB", create_resp.output)

        # Comprobar que aparece en ps con su PID
        ps_after = self.terminal.execute("ps")
        self.assertIn("Frenado_ABS", ps_after.output)

    def test_6_terminal_step_and_sched(self):
        """6. Terminal: avance de ciclos 'step' y cambio de planificador 'sched'."""
        self.terminal.execute("boot")
        step_resp = self.terminal.execute("step 3")
        self.assertTrue(step_resp.success)
        self.assertIn("Avanzados 3 ciclo(s)", step_resp.output)
        self.assertEqual(self.kernel.engine.current_tick, 3)

        sched_resp = self.terminal.execute("sched ROUND_ROBIN 3")
        self.assertTrue(sched_resp.success)
        self.assertEqual(self.kernel.scheduler.algorithm, "ROUND_ROBIN")
        self.assertEqual(self.kernel.scheduler.quantum, 3)

    def test_7_terminal_mem_and_map(self):
        """7. Terminal: visualización de memoria física, SWAP y mapa de particiones."""
        self.terminal.execute("boot")
        mem_resp = self.terminal.execute("mem")
        self.assertTrue(mem_resp.success)
        self.assertIn("MEMORIA FÍSICA (RAM)", mem_resp.output)
        self.assertIn("MEMORIA VIRTUAL", mem_resp.output)

        map_resp = self.terminal.execute("mem map")
        self.assertTrue(map_resp.success)
        self.assertIn("MAPA DINÁMICO DE PARTICIONES", map_resp.output)
        self.assertIn("0x00000000", map_resp.output)

    def test_8_terminal_kill_frees_memory(self):
        """8. Terminal: 'kill' aborta proceso y libera memoria inmediatamente."""
        self.terminal.execute("boot")
        # Crear proceso temporal
        create_resp = self.terminal.execute("create Sensor_Proximidad 2 8 100")
        pid = create_resp.data["pid"]
        used_before = self.kernel.memory_manager.used_memory

        kill_resp = self.terminal.execute(f"kill {pid}")
        self.assertTrue(kill_resp.success)
        self.assertIn("terminado forzosamente", kill_resp.output)
        self.assertEqual(self.kernel.memory_manager.used_memory, used_before - 100)

    def test_9_terminal_file_system_operations(self):
        """9. Terminal: operaciones de sistema de archivos (mkdir, write, cat, ls, rm)."""
        self.terminal.execute("boot")
        
        # mkdir
        mkdir_resp = self.terminal.execute("mkdir telemetry")
        self.assertTrue(mkdir_resp.success)

        # write
        write_resp = self.terminal.execute("write telemetry gps_coords.txt LAT=4.6097;LON=-74.0817")
        self.assertTrue(write_resp.success)

        # ls
        ls_resp = self.terminal.execute("ls telemetry")
        self.assertTrue(ls_resp.success)
        self.assertIn("gps_coords.txt", ls_resp.output)

        # cat
        cat_resp = self.terminal.execute("cat telemetry gps_coords.txt")
        self.assertTrue(cat_resp.success)
        self.assertIn("LAT=4.6097", cat_resp.output)

        # rm
        rm_resp = self.terminal.execute("rm telemetry gps_coords.txt")
        self.assertTrue(rm_resp.success)
        cat_after = self.terminal.execute("cat telemetry gps_coords.txt")
        self.assertFalse(cat_after.success)

    def test_10_terminal_vmem_address_translation(self):
        """10. Terminal: traducción de direcciones lógicas y detección de fallos de página."""
        self.terminal.execute("boot")
        # Traducir dirección virtual 12: página 12 // 4 = 3, offset = 0
        vmem_resp = self.terminal.execute("vmem 12")
        self.assertTrue(vmem_resp.success)
        self.assertIn("Dirección Virtual: 12", vmem_resp.output)
        self.assertIn("Página: 3", vmem_resp.output)
        self.assertIn("FALLO DE PÁGINA", vmem_resp.output)


if __name__ == "__main__":
    unittest.main()
