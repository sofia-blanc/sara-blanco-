"""
Pruebas unitarias para los DTOs y el Servicio de Aplicación (Etapa 5).
"""
import unittest
import json

from src.core.process_state import ProcessState
from src.core.process import Process
from src.core.exceptions import (
    InvalidProcessPriorityError,
    InvalidProcessAttributeError,
)
from src.dto.dtos import (
    ProcessDTO,
    CPUDTO,
    SchedulerDTO,
    EventDTO,
    SystemStatusDTO,
)
from src.services.auto_os_service import AutoOSService


class TestIntegrationLayerAndService(unittest.TestCase):
    """Suite de pruebas para validar DTOs, serialización JSON y AutoOSService."""

    def setUp(self):
        """Reinicia el contador de PIDs y crea una instancia fresca de AutoOSService."""
        Process._reset_pid_generator(start=1)
        self.service = AutoOSService()

    def test_process_to_dto_and_json_serialization(self):
        """Verifica la conversión de Process a ProcessDTO y serialización estricta a JSON."""
        p = Process(name="Control Tracción", priority=1, burst_time=4)
        dto = ProcessDTO.from_process(p)

        self.assertEqual(dto.pid, 1)
        self.assertEqual(dto.name, "Control Tracción")
        self.assertEqual(dto.priority, 1)
        self.assertEqual(dto.state, "NEW")
        self.assertEqual(dto.burst_time, 4)
        self.assertEqual(dto.remaining_time, 4)
        self.assertFalse(dto.is_finished)

        # Serialización a JSON puro
        json_str = json.dumps(dto.to_dict())
        self.assertIsInstance(json_str, str)
        parsed = json.loads(json_str)
        self.assertEqual(parsed["name"], "Control Tracción")
        self.assertEqual(parsed["state"], "NEW")

    def test_system_status_dto_and_json_roundtrip(self):
        """Verifica que el estado general del sistema se serialice completamente a JSON."""
        self.service.create_process(name="Freno ABS", priority=1, burst_time=2)
        status = self.service.get_system_status()

        self.assertIsInstance(status, dict)
        self.assertEqual(status["current_tick"], 0)
        self.assertFalse(status["is_paused"])
        self.assertEqual(status["total_registered_processes"], 1)
        self.assertEqual(status["scheduler"]["ready_count"], 1)

        # Probar serialización JSON sin excepciones
        json_output = self.service.get_system_status_json()
        self.assertIsInstance(json_output, str)
        parsed = json.loads(json_output)
        self.assertEqual(parsed["total_registered_processes"], 1)

    def test_service_create_and_query_processes(self):
        """Verifica la creación y consulta de procesos mediante el servicio."""
        created = self.service.create_process(name="Navegación GPS", priority=3, burst_time=5)

        self.assertEqual(created["pid"], 1)
        self.assertEqual(created["name"], "Navegación GPS")
        self.assertEqual(created["state"], "READY")

        # Consultar por PID
        fetched = self.service.get_process(pid=1)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["pid"], 1)

        # Consultar PID inexistente
        self.assertIsNone(self.service.get_process(pid=999))

        # Listar todos los procesos
        all_procs = self.service.get_all_processes()
        self.assertEqual(len(all_procs), 1)
        self.assertEqual(all_procs[0]["pid"], 1)

    def test_service_step_and_run_cycles(self):
        """Verifica el avance paso a paso y la ejecución en ráfaga a través del servicio."""
        self.service.create_process(name="Sensor Lidar", priority=1, burst_time=3)

        # Paso individual (step)
        step_res = self.service.step()
        self.assertTrue(step_res["success"])
        self.assertEqual(step_res["current_tick"], 1)
        self.assertFalse(step_res["cpu"]["is_idle"])
        self.assertEqual(step_res["cpu"]["current_process"]["remaining_time"], 2)

        # Ejecución en ráfaga (run_cycles)
        run_res = self.service.run_cycles(cycles=2)
        self.assertEqual(run_res["executed_cycles"], 2)
        self.assertEqual(run_res["current_tick"], 3)

        # El proceso debe haber terminado en el tick 3
        proc = self.service.get_process(pid=1)
        self.assertEqual(proc["state"], "TERMINATED")
        self.assertTrue(proc["is_finished"])

    def test_service_pause_and_resume(self):
        """Verifica que el servicio controle la pausa y reanudación correctamente."""
        self.service.create_process(name="Radio", priority=4, burst_time=2)

        # Pausar
        pause_res = self.service.pause()
        self.assertTrue(pause_res["is_paused"])

        # Intentar avanzar ciclos
        step_res = self.service.step()
        self.assertFalse(step_res["success"])
        self.assertEqual(step_res["current_tick"], 0)

        run_res = self.service.run_cycles(cycles=5)
        self.assertEqual(run_res["executed_cycles"], 0)

        # Reanudar
        resume_res = self.service.resume()
        self.assertFalse(resume_res["is_paused"])

        step_res = self.service.step()
        self.assertTrue(step_res["success"])
        self.assertEqual(step_res["current_tick"], 1)

    def test_service_block_and_unblock_process(self):
        """Verifica la operación de bloqueo y desbloqueo vehicular a través del servicio."""
        self.service.create_process(name="Lectura Cámara", priority=2, burst_time=3)
        self.service.step()  # entra a CPU y ejecuta 1 ciclo

        # Bloquear
        blocked = self.service.block_current_process(reason="Esperando bus CAN")
        self.assertIsNotNone(blocked)
        self.assertEqual(blocked["state"], "WAITING")

        status = self.service.get_system_status()
        self.assertEqual(len(status["waiting_processes"]), 1)
        self.assertTrue(status["cpu"]["is_idle"])

        # Desbloquear
        unblocked = self.service.unblock_process(pid=blocked["pid"])
        self.assertEqual(unblocked["state"], "READY")

        status_after = self.service.get_system_status()
        self.assertEqual(len(status_after["waiting_processes"]), 0)
        self.assertEqual(status_after["scheduler"]["ready_count"], 1)

    def test_service_get_events_with_filters(self):
        """Verifica la consulta de eventos con filtrado y límite a través del servicio."""
        self.service.create_process(name="Tarea A", priority=1, burst_time=1)
        self.service.create_process(name="Tarea B", priority=2, burst_time=1)
        self.service.run_cycles(2)

        # Consultar todos los eventos
        all_events = self.service.get_events()
        self.assertGreater(len(all_events), 0)

        # Filtrar por PID 1
        p1_events = self.service.get_events(pid=1)
        self.assertTrue(all(e["pid"] == 1 for e in p1_events))

        # Filtrar por tipo
        term_events = self.service.get_events(event_type="PROCESS_TERMINATED")
        self.assertEqual(len(term_events), 2)

        # Límite
        limited = self.service.get_events(limit=2)
        self.assertEqual(len(limited), 2)

    def test_service_error_handling_without_masking(self):
        """Verifica que el servicio propague errores claros ante datos inválidos sin enmascararlos."""
        # Prioridad fuera de rango
        with self.assertRaises(InvalidProcessPriorityError):
            self.service.create_process(name="Sensor", priority=99)

        # Ráfaga inválida
        with self.assertRaises(InvalidProcessAttributeError):
            self.service.create_process(name="Sensor", burst_time=0)

        # Ciclos negativos
        with self.assertRaises(InvalidProcessAttributeError):
            self.service.run_cycles(cycles=-2)

        # Desbloquear PID inexistente
        with self.assertRaises(InvalidProcessAttributeError):
            self.service.unblock_process(pid=888)


if __name__ == "__main__":
    unittest.main()
