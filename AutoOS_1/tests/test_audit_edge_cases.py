"""
Suite de pruebas de auditoría técnica y casos límite para AutoOS.
Valida la integridad de tipos, manejo de procesos obsoletos en colas,
desalojo/aborto en múltiples estados, invariantes de CPU y serialización.
"""
import unittest
import json

from src.core.process_state import ProcessState
from src.core.process import Process
from src.core.cpu import CPU
from src.core.scheduler import Scheduler
from src.core.simulation import SimulationEngine
from src.services.auto_os_service import AutoOSService
from src.core.exceptions import (
    InvalidProcessPriorityError,
    InvalidProcessAttributeError,
)


class TestAuditEdgeCasesAndInvariants(unittest.TestCase):
    """Pruebas rigurosas de casos límite y verificación de invariantes del sistema."""

    def setUp(self):
        """Reinicia el generador de PIDs y crea un servicio limpio."""
        Process._reset_pid_generator(start=1)
        self.service = AutoOSService()

    def test_booleans_rejected_for_priority_and_burst_time(self):
        """
        Verifica que los tipos booleanos (que heredan de int en Python)
        sean estrictamente rechazados como prioridad y tiempo de ráfaga.
        """
        # Prioridad booleana
        with self.assertRaises(InvalidProcessPriorityError):
            Process(name="Test", priority=True)  # type: ignore

        with self.assertRaises(InvalidProcessPriorityError):
            Process(name="Test", priority=False)  # type: ignore

        # Ráfaga booleana
        with self.assertRaises(InvalidProcessAttributeError):
            Process(name="Test", priority=2, burst_time=True)  # type: ignore

        with self.assertRaises(InvalidProcessAttributeError):
            Process(name="Test", priority=2, burst_time=False)  # type: ignore

        # Ciclos booleanos en run
        engine = SimulationEngine()
        with self.assertRaises(InvalidProcessAttributeError):
            engine.run(cycles=True)  # type: ignore

    def test_scheduler_lazy_cleanup_of_stale_processes(self):
        """
        Verifica que si un proceso en la cola de listos es cancelado/terminado
        externamente, el Scheduler lo descarte limpiamente sin causar excepciones
        en el despacho del siguiente proceso válido.
        """
        scheduler = Scheduler()
        cpu = CPU()

        p1 = Process(name="Tarea Cancelada", priority=1, burst_time=3)
        p2 = Process(name="Tarea Válida", priority=2, burst_time=2)
        p1.admit()
        p2.admit()

        scheduler.add_process(p1)
        scheduler.add_process(p2)

        # Cancelar P1 mientras está en la cola
        p1.terminate()

        # peek_next_process debe limpiar a P1 y retornar P2
        candidate = scheduler.peek_next_process()
        self.assertIs(candidate, p2)

        # dispatch debe cargar a P2 en la CPU sin fallar
        dispatched = scheduler.dispatch(cpu)
        self.assertIs(dispatched, p2)
        self.assertEqual(cpu.current_process, p2)
        self.assertEqual(p2.state, ProcessState.RUNNING)

    def test_scheduler_explicit_remove_process(self):
        """Verifica el retiro manual de un proceso de la cola de listos por su PID."""
        scheduler = Scheduler()
        p1 = Process(name="P1", priority=2)
        p2 = Process(name="P2", priority=1)
        p1.admit()
        p2.admit()
        scheduler.add_process(p1)
        scheduler.add_process(p2)

        # Retirar P2
        removed = scheduler.remove_process(p2.pid)
        self.assertIs(removed, p2)
        self.assertEqual(scheduler.ready_count, 1)
        self.assertIs(scheduler.peek_next_process(), p1)

        # Retiro de PID inexistente
        self.assertIsNone(scheduler.remove_process(pid=999))

    def test_scheduler_dynamic_priority_update(self):
        """Verifica la actualización de prioridad de un proceso que ya está en la cola."""
        scheduler = Scheduler()
        p_low = Process(name="P_Baja", priority=4)
        p_med = Process(name="P_Media", priority=2)
        p_low.admit()
        p_med.admit()
        scheduler.add_process(p_low)
        scheduler.add_process(p_med)

        # Originalmente P_Media sale primero
        self.assertIs(scheduler.peek_next_process(), p_med)

        # Subir P_Baja a prioridad 1 (máxima)
        updated = scheduler.update_process_priority(p_low.pid, 1)
        self.assertTrue(updated)
        self.assertEqual(p_low.priority, 1)

        # Ahora P_Baja debe salir primero
        self.assertIs(scheduler.peek_next_process(), p_low)

    def test_abort_process_in_all_lifecycle_states(self):
        """Verifica la finalización forzada de procesos en RUNNING, READY y WAITING."""
        # 1. Abortar proceso en RUNNING
        p_running = self.service.create_process(name="Proceso CPU", priority=1, burst_time=5)
        self.service.step()  # Despacha a CPU
        status_before = self.service.get_system_status()
        self.assertFalse(status_before["cpu"]["is_idle"])

        aborted_run = self.service.abort_process(p_running["pid"])
        self.assertEqual(aborted_run["state"], "TERMINATED")
        status_after_run = self.service.get_system_status()
        self.assertTrue(status_after_run["cpu"]["is_idle"])

        # 2. Abortar proceso en WAITING
        p_wait = self.service.create_process(name="Proceso Espera", priority=2, burst_time=3)
        self.service.step()  # Despacha a CPU
        self.service.block_current_process("Esperando sensor ultrasónico")
        self.assertEqual(len(self.service.get_system_status()["waiting_processes"]), 1)

        aborted_wait = self.service.abort_process(p_wait["pid"])
        self.assertEqual(aborted_wait["state"], "TERMINATED")
        self.assertEqual(len(self.service.get_system_status()["waiting_processes"]), 0)

        # 3. Abortar proceso en READY
        p_ready = self.service.create_process(name="Proceso Cola", priority=3, burst_time=2)
        self.assertEqual(self.service.get_system_status()["scheduler"]["ready_count"], 1)

        aborted_ready = self.service.abort_process(p_ready["pid"])
        self.assertEqual(aborted_ready["state"], "TERMINATED")
        self.assertEqual(self.service.get_system_status()["scheduler"]["ready_count"], 0)

    def test_cpu_accounting_invariants(self):
        """
        Verifica el invariante fundamental de la CPU:
        total_ticks == busy_ticks + idle_ticks en todo momento.
        """
        engine = self.service.engine

        # Inicialmente 0 ticks
        self.assertEqual(engine.cpu.total_ticks, engine.cpu.busy_ticks + engine.cpu.idle_ticks)

        # 3 ticks ociosos
        engine.run(3)
        self.assertEqual(engine.cpu.total_ticks, 3)
        self.assertEqual(engine.cpu.idle_ticks, 3)
        self.assertEqual(engine.cpu.busy_ticks, 0)
        self.assertEqual(engine.cpu.total_ticks, engine.cpu.busy_ticks + engine.cpu.idle_ticks)

        # Cargar y ejecutar proceso de 2 ticks
        self.service.create_process(name="Tarea", priority=1, burst_time=2)
        engine.run(2)
        self.assertEqual(engine.cpu.total_ticks, 5)
        self.assertEqual(engine.cpu.busy_ticks, 2)
        self.assertEqual(engine.cpu.idle_ticks, 3)
        self.assertEqual(engine.cpu.total_ticks, engine.cpu.busy_ticks + engine.cpu.idle_ticks)

        # Comprobar porcentaje
        snapshot = engine.cpu.to_dict()
        expected_util = round((2 / 5) * 100, 2)
        self.assertEqual(snapshot["utilization_percentage"], expected_util)

    def test_get_all_processes_includes_all_states(self):
        """Verifica que get_all_processes devuelva todos los procesos sin omitir ningún estado."""
        # Proceso 1: Terminará
        self.service.create_process(name="P_Terminado", priority=1, burst_time=1)
        self.service.step()  # Ejecuta y concluye

        # Proceso 2: En CPU (RUNNING)
        self.service.create_process(name="P_EnEjecucion", priority=2, burst_time=3)
        self.service.step()  # Entra a CPU

        # Proceso 3: Bloqueado (WAITING)
        self.service.create_process(name="P_Bloqueado", priority=1, burst_time=2)
        # Desalojamos temporalmente al proceso 2 bloqueándolo
        self.service.block_current_process("Lectura de radar")

        # Proceso 4: En cola (READY)
        self.service.create_process(name="P_EnListo", priority=4, burst_time=3)

        all_procs = self.service.get_all_processes()
        states_found = {p["state"] for p in all_procs}

        self.assertIn("TERMINATED", states_found)
        self.assertIn("WAITING", states_found)
        self.assertIn("READY", states_found)
        self.assertEqual(len(all_procs), 4)

    def test_strict_json_serialization_all_fields(self):
        """Verifica que la serialización a JSON sea estrictamente compatible con cualquier parser estándar."""
        self.service.create_process(name="Sensor Lidar Frontal", priority=1, burst_time=3)
        self.service.step()

        json_str = self.service.get_system_status_json()
        data = json.loads(json_str)

        self.assertIsInstance(data["current_tick"], int)
        self.assertIsInstance(data["is_paused"], bool)
        self.assertIsInstance(data["cpu"], dict)
        self.assertIsInstance(data["scheduler"], dict)
        self.assertIsInstance(data["process_distribution"], dict)
        self.assertIsInstance(data["total_registered_processes"], int)
        self.assertIsInstance(data["waiting_processes"], list)
        self.assertIsInstance(data["terminated_processes"], list)
        self.assertIsInstance(data["total_events"], int)

    def test_abort_process_in_new_state_without_admission(self):

        """
        Verifica que SimulationEngine y AutoOSService puedan abortar forzosamente
        un proceso en estado NEW sin admitirlo previamente a READY.
        Comprueba que quede en TERMINATED, no se inserte en el Scheduler,
        figure en get_all_processes() y registre el evento de terminación.
        """
        p_new = Process(name="Proceso Cancelado Tempranamente", priority=2, burst_time=3)
        self.assertEqual(p_new.state, ProcessState.NEW)

        # Registrar sin admitir a la cola
        self.service.register_process(p_new)
        self.assertEqual(p_new.state, ProcessState.NEW)
        self.assertEqual(self.service.engine.scheduler.ready_count, 0)
        self.assertTrue(self.service.engine.scheduler.is_empty)

        # Abortar el proceso en estado NEW
        aborted = self.service.abort_process(p_new.pid)

        # 1. El proceso debe quedar en TERMINATED
        self.assertEqual(aborted["state"], "TERMINATED")
        self.assertEqual(p_new.state, ProcessState.TERMINATED)
        self.assertTrue(p_new.is_finished)

        # 2. No debe haberse insertado al Scheduler
        self.assertEqual(self.service.engine.scheduler.ready_count, 0)
        self.assertTrue(self.service.engine.scheduler.is_empty)

        # 3. Debe figurar en get_all_processes()
        all_procs = self.service.get_all_processes()
        p_found = next((p for p in all_procs if p["pid"] == p_new.pid), None)
        self.assertIsNotNone(p_found)
        self.assertEqual(p_found["state"], "TERMINATED")

        # 4. Debe figurar en terminated_processes del status
        status = self.service.get_system_status()
        self.assertTrue(any(p["pid"] == p_new.pid for p in status["terminated_processes"]))

        # 5. Debe registrar el evento PROCESS_TERMINATED con metadata aborted=True
        events = self.service.get_events(pid=p_new.pid, event_type="PROCESS_TERMINATED")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["pid"], p_new.pid)
        self.assertTrue(events[0]["data"].get("aborted"))


if __name__ == "__main__":
    unittest.main()

