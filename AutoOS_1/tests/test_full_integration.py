"""
====================================================================
AUTOOS - PRUEBAS DE INTEGRACIÓN INTEGRAL (END-TO-END)
====================================================================
Valida la integración completa entre el motor central AutoOS_1,
el puente del Kernel (kernel_bridge), los módulos de Auto y
la capa de persistencia de simulación y auditoría.
====================================================================
"""
import unittest
import os
import sys
import json
from pathlib import Path

# Configurar PYTHONPATH
CURRENT_DIR = Path(__file__).resolve().parent
AUTOOS1_DIR = CURRENT_DIR.parent
ROOT_DIR = AUTOOS1_DIR.parent
AUTO_DIR = ROOT_DIR / "Auto"

if str(AUTOOS1_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOOS1_DIR))
if str(AUTO_DIR) not in sys.path:
    sys.path.insert(0, str(AUTO_DIR))

import kernel_bridge
from src.core.kernel import Kernel
from src.core.process_state import ProcessState
from src.core.scheduler import AlgorithmType
from src.core.exceptions import InsufficientMemoryError
import config
from modules.auth_security import validar_accion, tiene_permiso, ROLES_INFO
from modules.processes import crear_proceso, finalizar_proceso, obtener_procesos
from modules.memory_storage import obtener_uso_memoria, obtener_sistema_archivos


class TestFullAutoOSIntegration(unittest.TestCase):
    """Suite de validación de los 10 criterios integrados y persistencia."""

    def setUp(self):
        # Reiniciar instancia del Kernel para pruebas aisladas
        self.kernel = Kernel(memory_mb=1024, swap_mb=2048)
        kernel_bridge._FALLBACK_KERNEL = self.kernel
        kernel_bridge._FALLBACK_TERMINAL = None
        kernel_bridge._FALLBACK_GANTT.clear()
        kernel_bridge._FALLBACK_TERMINAL_HIST.clear()

    def test_criterio_1_y_2_boot_and_kernel_lifecycle(self):
        """Criterio 1 y 2: Secuencia de arranque en 7 fases y ciclo de vida del Kernel."""
        self.assertFalse(self.kernel.is_booted)
        
        # Ejecutar Boot
        boot_res = kernel_bridge.boot_system()
        self.assertEqual(boot_res["status"], "BOOT_SUCCESS")
        self.assertTrue(self.kernel.is_booted)
        self.assertEqual(len(boot_res["stages"]), 7)
        
        # Verificar los 4 demonios automotrices creados
        procs = self.kernel.engine.get_all_processes()
        nombres = [p.name for p in procs]
        self.assertIn("BMS_Battery_Monitor", nombres)
        self.assertIn("CAN_Bus_Gateway", nombres)
        self.assertIn("ADAS_Vision_Pilot", nombres)
        self.assertIn("Telemetry_Cloud_Node", nombres)

        # Verificar snapshot
        snap = self.kernel.get_system_snapshot()
        self.assertTrue(snap["is_booted"])
        self.assertGreater(snap["total_events"], 0)

        # Probar apagado seguro
        shutdown_res = kernel_bridge.shutdown_system()
        self.assertEqual(shutdown_res["status"], "SHUTDOWN_SUCCESS")
        self.assertFalse(self.kernel.is_booted)

    def test_criterio_3_y_7_process_creation_and_first_fit_ram(self):
        """Criterios 3 y 7: Creación de procesos con asignación contigua First-Fit."""
        kernel_bridge.boot_system()
        ram_inicial_libre = self.kernel.memory_manager.free_memory

        # Crear proceso vehicular con 128 MB de RAM
        ok, msg, proc = kernel_bridge.create_process_bridge("Sensor_LIDAR_360", priority=2, burst_time=5, memory_size=128)
        self.assertTrue(ok)
        self.assertIsNotNone(proc)
        self.assertEqual(proc["name"], "Sensor_LIDAR_360")
        
        # Verificar que la memoria libre disminuyó exactamente en 128 MB
        self.assertEqual(self.kernel.memory_manager.free_memory, ram_inicial_libre - 128)
        
        # Verificar en el mapa dinámico de memoria
        alloc = self.kernel.memory_manager.get_process_allocation(proc["pid"])
        self.assertIsNotNone(alloc)
        self.assertEqual(alloc.limit, 128)
        self.assertFalse(alloc.is_free)

        # Probar rechazo por memoria insuficiente (pedir más de lo disponible)
        ok_fail, msg_fail, _ = kernel_bridge.create_process_bridge("Carga_Pesada_IA", priority=3, burst_time=10, memory_size=2048)
        self.assertFalse(ok_fail)
        self.assertIn("insuficiente", msg_fail.lower())

    def test_criterio_4_y_6_execution_gantt_and_scheduling(self):
        """Criterios 4 y 6: Ejecución por ticks, diagrama de Gantt y algoritmos de planificación."""
        kernel_bridge.boot_system()

        # Avanzar 3 ciclos de simulación
        step_res = kernel_bridge.step_simulation(3)
        self.assertEqual(step_res["executed"], 3)
        self.assertEqual(self.kernel.engine.current_tick, 3)

        # Verificar que se registraron ticks en el Gantt
        gantt = kernel_bridge.get_gantt_history()
        self.assertGreaterEqual(len(gantt), 3)

        # Cambiar algoritmo a Round Robin con quantum 2
        ok_sched, _ = kernel_bridge.set_scheduler_bridge("ROUND_ROBIN", quantum=2)
        self.assertTrue(ok_sched)
        self.assertEqual(self.kernel.scheduler.algorithm, "ROUND_ROBIN")
        self.assertEqual(self.kernel.scheduler.quantum, 2)

        # Probar inyección de proceso crítico ASIL-D
        ok_crit, msg_crit, p_crit = kernel_bridge.inject_critical_process_bridge()
        self.assertTrue(ok_crit)
        self.assertIn("Freno_Emergencia", p_crit["name"])
        self.assertEqual(p_crit["priority"], 1)

    def test_criterio_5_process_termination_and_memory_coalescing(self):
        """Criterio 5: Terminación forzada y coalescencia de bloques de memoria RAM."""
        kernel_bridge.boot_system()

        # Crear proceso
        ok, _, proc = kernel_bridge.create_process_bridge("Proceso_Temporal", priority=3, burst_time=4, memory_size=64)
        self.assertTrue(ok)
        pid = proc["pid"]

        # Abortar proceso
        ok_abort, msg_abort = kernel_bridge.abort_process_bridge(pid)
        self.assertTrue(ok_abort)

        # Verificar que el proceso está en TERMINATED
        p_obj = self.kernel.engine.get_process(pid)
        self.assertEqual(p_obj.state, ProcessState.TERMINATED)

        # Verificar que la memoria fue liberada (ya no tiene asignación activa)
        alloc = self.kernel.memory_manager.get_process_allocation(pid)
        self.assertIsNone(alloc)

    def test_criterio_8_virtual_memory_paging_and_page_fault(self):
        """Criterio 8: Memoria virtual, traducción de direcciones y detección de Page Fault."""
        kernel_bridge.boot_system()
        vm = self.kernel.virtual_memory

        # Primer acceso a dirección virtual 12 -> Debe generar Page Fault
        res1 = vm.translate_address(pid=1, virtual_address=12, is_write=True)
        self.assertTrue(res1["page_fault"])  # Fallo de página
        self.assertGreater(vm.page_faults, 0)

        # Segundo acceso a la misma dirección -> Debe generar Page Hit
        res2 = vm.translate_address(pid=1, virtual_address=12, is_write=False)
        self.assertFalse(res2["page_fault"])  # Acierto de página
        self.assertGreater(vm.page_hits, 0)

    def test_criterio_9_persistent_file_system_vfs(self):
        """Criterio 9: Sistema de archivos persistente con lectura, escritura y JSON."""
        kernel_bridge.boot_system()
        fs = self.kernel.file_system

        # Escribir en VFS
        created = fs.create_file("logs", "telemetria_test.log", size=1, content="CAN_SPEED=120KMH")
        self.assertTrue(created)

        # Leer archivo
        content = fs.read_file("logs", "telemetria_test.log")
        self.assertEqual(content, "CAN_SPEED=120KMH")

        # Modificar archivo
        fs.write_file("logs", "telemetria_test.log", "CAN_SPEED=130KMH", mode="w")
        self.assertEqual(fs.read_file("logs", "telemetria_test.log"), "CAN_SPEED=130KMH")

        # Persistir a disco temporal
        test_json = str(CURRENT_DIR / "vfs_test_dump.json")
        fs.save_to_disk(test_json)
        self.assertTrue(os.path.exists(test_json))

        # Cargar en otra instancia para verificar persistencia
        from src.memory.file_system import FileSystem
        fs2 = FileSystem(storage_path=test_json, auto_load=True)
        self.assertEqual(fs2.read_file("logs", "telemetria_test.log"), "CAN_SPEED=130KMH")

        # Limpieza
        if os.path.exists(test_json):
            os.remove(test_json)

    def test_criterio_10_interactive_terminal_execution(self):
        """Criterio 10: Terminal interactiva con comandos reales sobre el simulador."""
        kernel_bridge.boot_system()

        # Ejecutar comando 'ps'
        resp_ps = kernel_bridge.execute_terminal_command("ps")
        self.assertTrue(resp_ps.success)
        self.assertIn("BMS_Battery_Monitor", resp_ps.output)

        # Ejecutar comando 'create'
        resp_cr = kernel_bridge.execute_terminal_command("create Tarea_Terminal 2 4 64")
        self.assertTrue(resp_cr.success)
        self.assertIn("creado exitosamente", resp_cr.output)

        # Ejecutar comando 'step 2'
        resp_step = kernel_bridge.execute_terminal_command("step 2")
        self.assertTrue(resp_step.success)
        self.assertIn("Avanzados 2", resp_step.output)

        # Ejecutar comando 'vmem'
        resp_vmem = kernel_bridge.execute_terminal_command("vmem 10 write 1")
        self.assertTrue(resp_vmem.success)
        self.assertIn("FALLO DE PÁGINA", resp_vmem.output)

        # Verificar que el historial de terminal contiene los comandos
        hist = kernel_bridge.get_terminal_history()
        cmds = [h["cmd"] for h in hist]
        self.assertIn("ps", cmds)
        self.assertIn("step 2", cmds)

    def test_seguridad_rbac_autenticacion_vs_autorizacion(self):
        """Demostración de RBAC: Mecánico (Admin) vs Pasajero (Guest)."""
        db = config.get_db()
        usr_mecanico = db["perfiles"][0]  # Admin
        usr_pasajero = db["perfiles"][2]  # Guest

        # Mecánico puede crear y abortar procesos
        ok_admin_create, _ = validar_accion(usr_mecanico, "proceso.crear", recurso="proceso:test")
        self.assertTrue(ok_admin_create)

        ok_admin_kill, _ = validar_accion(usr_mecanico, "proceso.finalizar", recurso="proceso:test")
        self.assertTrue(ok_admin_kill)

        # Pasajero NO puede crear procesos (403 Forbidden)
        ok_guest_create, msg_rechazo = validar_accion(usr_pasajero, "proceso.crear", recurso="proceso:test")
        self.assertFalse(ok_guest_create)
        self.assertIn("Acceso Denegado (403)", msg_rechazo)

        # Pasajero NO puede calibrar sensores de hardware
        ok_guest_cal, _ = validar_accion(usr_pasajero, "dispositivo.calibrar", recurso="sensor:lidar")
        self.assertFalse(ok_guest_cal)

    def test_persistencia_reporte_simulacion(self):
        """Verificación de persistencia de informe de simulación en almacén local."""
        nuevo_rep = {
            "report_id": "TEST-REP-001",
            "escenario": "Prueba Unitaria",
            "titulo": "Auditoría de Integración Completa",
            "diagnostico": "Todos los criterios conformes",
            "evaluacion": "Aprobado",
            "usuario_email": "mecanico@autoos.tech",
            "bateria_inicial": 80.0,
            "bateria_final": 80.0,
            "velocidad_final": 0.0,
            "cpu_load_final": 15.0,
        }
        ok, msg = config.guardar_reporte_simulacion(nuevo_rep)
        self.assertTrue(ok)

        # Recuperar reportes
        reportes = config.obtener_reportes_simulacion()
        ids = [r.get("report_id") for r in reportes]
        self.assertIn("TEST-REP-001", ids)


if __name__ == "__main__":
    unittest.main()
