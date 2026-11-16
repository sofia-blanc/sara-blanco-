"""
Pruebas unitarias para el Motor de Simulación de AutoOS (Etapa 4).
"""
import unittest

from src.core.process_state import ProcessState
from src.core.process import Process
from src.core.cpu import CPU
from src.core.scheduler import Scheduler
from src.core.event_logger import EventLogger
from src.core.simulation import SimulationEngine
from src.core.exceptions import InvalidProcessAttributeError


class TestSimulationEngine(unittest.TestCase):
    """Suite de pruebas para validar la coordinación del reloj, CPU, Scheduler y EventLogger."""

    def setUp(self):
        """Reinicia el contador de PIDs y crea un motor nuevo antes de cada prueba."""
        Process._reset_pid_generator(start=1)
        self.engine = SimulationEngine()

    def test_process_registration_and_admission(self):
        """Verifica la creación y admisión de procesos al sistema y al Scheduler."""
        p = self.engine.create_process(name="Freno Autónomo", priority=1, burst_time=3)

        self.assertEqual(p.pid, 1)
        self.assertEqual(p.state, ProcessState.READY)
        self.assertEqual(self.engine.scheduler.ready_count, 1)
        self.assertIs(self.engine.scheduler.peek_next_process(), p)

        # Verificar eventos en la bitácora
        events = self.engine.logger.get_events(pid=p.pid)
        event_types = [e.event_type for e in events]
        self.assertIn("PROCESS_CREATED", event_types)
        self.assertIn("PROCESS_ADMITTED", event_types)

    def test_automatic_dispatch_and_cycle_advance(self):
        """Verifica que el motor despache automáticamente y avance los ciclos de reloj."""
        p = self.engine.create_process(name="Sensor Ultrasonido", priority=2, burst_time=2)

        self.assertEqual(self.engine.current_tick, 0)
        self.assertTrue(self.engine.cpu.is_idle)

        # Tick 1: Despacha a CPU y ejecuta 1 ciclo
        success = self.engine.tick()
        self.assertTrue(success)
        self.assertEqual(self.engine.current_tick, 1)
        self.assertEqual(p.state, ProcessState.RUNNING)
        self.assertEqual(p.remaining_time, 1)
        self.assertFalse(self.engine.cpu.is_idle)

        # Tick 2: Ejecuta segundo ciclo y finaliza
        self.engine.tick()
        self.assertEqual(self.engine.current_tick, 2)
        self.assertEqual(p.state, ProcessState.TERMINATED)
        self.assertTrue(self.engine.cpu.is_idle)
        self.assertEqual(p.remaining_time, 0)

        # Verificar evento de terminación
        term_events = self.engine.logger.get_events(pid=p.pid, event_type="PROCESS_TERMINATED")
        self.assertEqual(len(term_events), 1)
        self.assertEqual(term_events[0].tick, 2)

    def test_execution_of_multiple_consecutive_processes_by_priority(self):
        """
        Verifica la ejecución secuencial de un lote de procesos según prioridad:
        P1 (Prio 3, ráfaga 2), P2 (Prio 1, ráfaga 1), P3 (Prio 2, ráfaga 2).
        Orden de ejecución esperado: P2 -> P3 -> P1.
        """
        p1 = self.engine.create_process(name="Climatizador", priority=3, burst_time=2)
        p2 = self.engine.create_process(name="Freno Emergencia", priority=1, burst_time=1)
        p3 = self.engine.create_process(name="Dirección Eléctrica", priority=2, burst_time=2)

        # Ejecutamos 5 ciclos (1 para P2 + 2 para P3 + 2 para P1)
        executed = self.engine.run(cycles=5)
        self.assertEqual(executed, 5)
        self.assertEqual(self.engine.current_tick, 5)

        # Todos deben estar en TERMINATED y la CPU libre
        self.assertEqual(p1.state, ProcessState.TERMINATED)
        self.assertEqual(p2.state, ProcessState.TERMINATED)
        self.assertEqual(p3.state, ProcessState.TERMINATED)
        self.assertTrue(self.engine.cpu.is_idle)
        self.assertTrue(self.engine.scheduler.is_empty)

        # Verificar el orden cronológico de los despachos a CPU
        dispatch_events = self.engine.logger.get_events(event_type="PROCESS_DISPATCHED")
        dispatched_pids = [e.pid for e in dispatch_events]
        self.assertEqual(dispatched_pids, [p2.pid, p3.pid, p1.pid])

    def test_pause_and_resume_control(self):
        """Verifica que pausar detenga el avance del reloj y que reanudar lo reactive."""
        p = self.engine.create_process(name="GPS", priority=2, burst_time=4)

        # Tick 1: ejecución normal
        self.engine.tick()
        self.assertEqual(self.engine.current_tick, 1)
        self.assertEqual(p.remaining_time, 3)

        # Pausar simulación
        self.engine.pause()
        self.assertTrue(self.engine.is_paused)

        # Intentar tick mientras está pausado
        result = self.engine.tick()
        self.assertFalse(result)
        self.assertEqual(self.engine.current_tick, 1)  # No avanza
        self.assertEqual(p.remaining_time, 3)          # No consume CPU

        # Intentar run mientras está pausado
        cycles = self.engine.run(cycles=5)
        self.assertEqual(cycles, 0)
        self.assertEqual(self.engine.current_tick, 1)

        # Reanudar simulación
        self.engine.resume()
        self.assertFalse(self.engine.is_paused)

        # Tick 2 tras reanudar
        self.engine.tick()
        self.assertEqual(self.engine.current_tick, 2)
        self.assertEqual(p.remaining_time, 2)

    def test_empty_queue_idle_ticks(self):
        """Verifica que ticks sin procesos listos se registren como ociosos (CPU_IDLE)."""
        self.assertTrue(self.engine.scheduler.is_empty)
        self.assertTrue(self.engine.cpu.is_idle)

        self.engine.tick()
        self.assertEqual(self.engine.current_tick, 1)
        self.assertEqual(self.engine.cpu.idle_ticks, 1)

        idle_events = self.engine.logger.get_events(event_type="CPU_IDLE")
        self.assertEqual(len(idle_events), 1)
        self.assertEqual(idle_events[0].tick, 1)

    def test_blocking_and_unblocking_flow(self):
        """
        Verifica el flujo de bloqueo por E/S (RUNNING -> WAITING) y desbloqueo (WAITING -> READY).
        """
        p1 = self.engine.create_process(name="Sensor Cámara", priority=2, burst_time=3)
        p2 = self.engine.create_process(name="Luces Altas", priority=3, burst_time=2)

        # Tick 1: P1 entra a CPU y ejecuta 1 ciclo (le quedan 2)
        self.engine.tick()
        self.assertEqual(self.engine.cpu.current_process.pid, p1.pid)

        # P1 se bloquea esperando cuadro de imagen del sensor
        blocked = self.engine.block_current_process(reason="Espera de fotograma")
        self.assertIs(blocked, p1)
        self.assertEqual(p1.state, ProcessState.WAITING)
        self.assertTrue(self.engine.cpu.is_idle)

        # Tick 2: Como CPU quedó libre, se despacha P2
        self.engine.tick()
        self.assertEqual(self.engine.cpu.current_process.pid, p2.pid)
        self.assertEqual(p2.state, ProcessState.RUNNING)

        # Se recibe el fotograma: desbloqueamos P1
        unblocked = self.engine.unblock_process(p1.pid)
        self.assertIs(unblocked, p1)
        self.assertEqual(p1.state, ProcessState.READY)
        self.assertEqual(self.engine.scheduler.ready_count, 1)

        # Verificar eventos
        self.assertEqual(len(self.engine.logger.get_events(event_type="PROCESS_BLOCKED")), 1)
        self.assertEqual(len(self.engine.logger.get_events(event_type="PROCESS_UNBLOCKED")), 1)

    def test_unblock_nonexistent_process_raises_error(self):
        """Verifica que intentar desbloquear un proceso que no esté en WAITING arroje error."""
        with self.assertRaises(InvalidProcessAttributeError):
            self.engine.unblock_process(pid=999)

    def test_run_invalid_cycles_argument(self):
        """Verifica que run() valide que los ciclos sean un entero mayor a cero."""
        with self.assertRaises(InvalidProcessAttributeError):
            self.engine.run(cycles=0)

        with self.assertRaises(InvalidProcessAttributeError):
            self.engine.run(cycles=-3)

    def test_get_status_snapshot_consistency(self):
        """Verifica que get_status() devuelva una instantánea coherente y completa del sistema."""
        p = self.engine.create_process(name="Inyección", priority=1, burst_time=2)
        self.engine.tick()

        status = self.engine.get_status()
        self.assertEqual(status["current_tick"], 1)
        self.assertFalse(status["is_paused"])
        self.assertEqual(status["total_registered_processes"], 1)
        self.assertEqual(status["process_distribution"]["RUNNING"], 1)
        self.assertEqual(status["process_distribution"]["READY"], 0)
        self.assertFalse(status["cpu"]["is_idle"])
        self.assertGreater(status["total_events"], 0)

    def test_event_logger_filtering_and_serialization(self):
        """Verifica el filtrado por PID y tipo de evento y la exportación de la bitácora."""
        p1 = self.engine.create_process(name="Tarea 1", priority=1, burst_time=1)
        p2 = self.engine.create_process(name="Tarea 2", priority=2, burst_time=1)
        self.engine.run(2)

        # Filtrar por PID 1
        p1_events = self.engine.logger.get_events(pid=p1.pid)
        for ev in p1_events:
            self.assertEqual(ev.pid, p1.pid)

        # Exportar a lista de diccionarios
        raw_list = self.engine.logger.to_list()
        self.assertIsInstance(raw_list, list)
        self.assertTrue(all("tick" in ev and "event_type" in ev for ev in raw_list))


if __name__ == "__main__":
    unittest.main()
