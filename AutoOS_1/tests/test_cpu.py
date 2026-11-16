"""
Pruebas unitarias para la CPU uniprocesador y exclusión mutua de AutoOS (Etapa 2).
"""
import unittest

from src.core.process_state import ProcessState
from src.core.process import Process
from src.core.cpu import CPU
from src.core.exceptions import (
    CPUBusyError,
    InvalidStateTransitionError,
    InvalidProcessAttributeError,
)


class TestCPUUniprocessorAndMutualExclusion(unittest.TestCase):
    """Suite de pruebas para verificar el funcionamiento de la CPU y la exclusión mutua."""

    def setUp(self):
        """Reinicia el contador de PIDs y crea una instancia limpia de CPU antes de cada prueba."""
        Process._reset_pid_generator(start=1)
        self.cpu = CPU()

    def test_cpu_initializes_idle(self):
        """Verifica que la CPU inicie libre y con sus contadores de métricas en cero."""
        self.assertTrue(self.cpu.is_idle)
        self.assertIsNone(self.cpu.current_process)
        self.assertEqual(self.cpu.total_ticks, 0)
        self.assertEqual(self.cpu.busy_ticks, 0)
        self.assertEqual(self.cpu.idle_ticks, 0)

    def test_load_ready_process_transitions_to_running(self):
        """Verifica que un proceso en estado READY se cargue y pase a RUNNING."""
        p = Process(name="Control de Estabilidad", priority=1, burst_time=4)
        p.admit()  # NEW -> READY

        self.cpu.load_process(p)

        self.assertFalse(self.cpu.is_idle)
        self.assertIs(self.cpu.current_process, p)
        self.assertEqual(p.state, ProcessState.RUNNING)

    def test_reject_process_not_in_ready_state(self):
        """Verifica que la CPU rechace cargar procesos que no estén en estado READY."""
        # 1. Proceso en NEW
        p_new = Process(name="Sensor Lidar", priority=2, burst_time=3)
        with self.assertRaises(InvalidStateTransitionError):
            self.cpu.load_process(p_new)
        self.assertTrue(self.cpu.is_idle)
        self.assertEqual(p_new.state, ProcessState.NEW)

        # 2. Proceso en WAITING
        p_waiting = Process(name="Lectura Radar", priority=2, burst_time=3)
        p_waiting.admit()
        p_waiting.dispatch()
        p_waiting.block()
        with self.assertRaises(InvalidStateTransitionError):
            self.cpu.load_process(p_waiting)
        self.assertTrue(self.cpu.is_idle)
        self.assertEqual(p_waiting.state, ProcessState.WAITING)

        # 3. Proceso en TERMINATED
        p_term = Process(name="Tarea Concluida", priority=3, burst_time=1)
        p_term.admit()
        p_term.terminate()
        with self.assertRaises(InvalidStateTransitionError):
            self.cpu.load_process(p_term)
        self.assertTrue(self.cpu.is_idle)
        self.assertEqual(p_term.state, ProcessState.TERMINATED)

    def test_reject_load_when_cpu_is_busy(self):
        """Verifica que la CPU rechace un segundo proceso si ya está ejecutando uno (Exclusión mutua)."""
        p1 = Process(name="Frenado Autónomo", priority=1, burst_time=5)
        p1.admit()
        self.cpu.load_process(p1)

        p2 = Process(name="Acelerador", priority=2, burst_time=3)
        p2.admit()

        # Debe lanzar CPUBusyError
        with self.assertRaises(CPUBusyError) as context:
            self.cpu.load_process(p2)

        self.assertEqual(context.exception.current_pid, p1.pid)
        self.assertEqual(context.exception.incoming_pid, p2.pid)

    def test_cpu_preserves_original_process_and_states_on_load_failure(self):
        """
        Verifica que tras un intento fallido de carga por CPU ocupada:
        - El proceso original siga en RUNNING y en la CPU.
        - El proceso rechazado conserve su estado READY sin corromperse.
        """
        p1 = Process(name="Dirección Asistida", priority=1, burst_time=4)
        p1.admit()
        self.cpu.load_process(p1)

        p2 = Process(name="Luces Automáticas", priority=4, burst_time=2)
        p2.admit()

        try:
            self.cpu.load_process(p2)
        except CPUBusyError:
            pass

        # Verificar integridad de estados
        self.assertIs(self.cpu.current_process, p1)
        self.assertEqual(p1.state, ProcessState.RUNNING)
        self.assertEqual(p2.state, ProcessState.READY)
        self.assertFalse(self.cpu.is_idle)

    def test_tick_consumes_exact_cycle_of_active_process(self):
        """Verifica que cada invocación a tick() descuente exactamente 1 ciclo del proceso activo."""
        p = Process(name="Inyección Electrónica", priority=2, burst_time=3)
        p.admit()
        self.cpu.load_process(p)

        # Tick 1
        rem1 = self.cpu.tick()
        self.assertEqual(rem1, 2)
        self.assertEqual(p.remaining_time, 2)
        self.assertEqual(self.cpu.total_ticks, 1)
        self.assertEqual(self.cpu.busy_ticks, 1)
        self.assertEqual(self.cpu.idle_ticks, 0)
        self.assertFalse(self.cpu.is_idle)

        # Tick 2
        rem2 = self.cpu.tick()
        self.assertEqual(rem2, 1)
        self.assertEqual(p.remaining_time, 1)
        self.assertEqual(self.cpu.total_ticks, 2)
        self.assertEqual(self.cpu.busy_ticks, 2)
        self.assertFalse(self.cpu.is_idle)

    def test_cpu_becomes_idle_when_process_terminates(self):
        """Verifica que la CPU quede libre en cuanto el proceso agota su tiempo de ráfaga."""
        p = Process(name="Actualización Odómetro", priority=3, burst_time=2)
        p.admit()
        self.cpu.load_process(p)

        self.cpu.tick()  # Ciclo 1 (queda 1)
        self.assertFalse(self.cpu.is_idle)

        self.cpu.tick()  # Ciclo 2 (llega a 0)

        # El proceso debe estar TERMINATED y la CPU libre
        self.assertEqual(p.state, ProcessState.TERMINATED)
        self.assertTrue(p.is_finished)
        self.assertTrue(self.cpu.is_idle)
        self.assertIsNone(self.cpu.current_process)

    def test_can_load_second_process_after_first_finishes(self):
        """Verifica que se pueda ejecutar un segundo proceso una vez finalizado el primero."""
        p1 = Process(name="Tarea 1", priority=2, burst_time=1)
        p1.admit()
        self.cpu.load_process(p1)
        self.cpu.tick()  # p1 termina

        self.assertTrue(self.cpu.is_idle)

        p2 = Process(name="Tarea 2", priority=1, burst_time=2)
        p2.admit()
        self.cpu.load_process(p2)

        self.assertFalse(self.cpu.is_idle)
        self.assertIs(self.cpu.current_process, p2)
        self.assertEqual(p2.state, ProcessState.RUNNING)

        self.cpu.tick()
        self.assertEqual(p2.remaining_time, 1)

    def test_safe_preemption_and_cpu_release(self):
        """Verifica el desalojo seguro por preempción (RUNNING -> READY) dejando la CPU libre."""
        p = Process(name="Control Crucero", priority=3, burst_time=5)
        p.admit()
        self.cpu.load_process(p)

        preempted = self.cpu.preempt_process()

        self.assertIs(preempted, p)
        self.assertEqual(p.state, ProcessState.READY)
        self.assertTrue(self.cpu.is_idle)
        self.assertIsNone(self.cpu.current_process)

    def test_safe_blocking_and_cpu_release(self):
        """Verifica el desalojo seguro por bloqueo de E/S (RUNNING -> WAITING) dejando la CPU libre."""
        p = Process(name="Lectura Ultrasonido", priority=2, burst_time=4)
        p.admit()
        self.cpu.load_process(p)

        blocked = self.cpu.block_process()

        self.assertIs(blocked, p)
        self.assertEqual(p.state, ProcessState.WAITING)
        self.assertTrue(self.cpu.is_idle)
        self.assertIsNone(self.cpu.current_process)

    def test_idle_ticks_accounting(self):
        """Verifica que los ticks con CPU ociosa se contabilicen correctamente sin generar excepciones."""
        self.assertTrue(self.cpu.is_idle)
        result = self.cpu.tick()

        self.assertIsNone(result)
        self.assertEqual(self.cpu.total_ticks, 1)
        self.assertEqual(self.cpu.idle_ticks, 1)
        self.assertEqual(self.cpu.busy_ticks, 0)

    def test_invalid_parameter_rejected(self):
        """Verifica que load_process rechace parámetros que no sean instancias de Process."""
        with self.assertRaises(InvalidProcessAttributeError):
            self.cpu.load_process("no_es_un_proceso")  # type: ignore

    def test_to_dict_metrics_serialization(self):
        """Verifica la serialización de estado y métricas de uso de CPU."""
        p = Process(name="Monitoreo Térmico", priority=2, burst_time=3)
        p.admit()
        self.cpu.load_process(p)
        self.cpu.tick()  # 1 busy tick

        snapshot = self.cpu.to_dict()

        self.assertFalse(snapshot["is_idle"])
        self.assertEqual(snapshot["total_ticks"], 1)
        self.assertEqual(snapshot["busy_ticks"], 1)
        self.assertEqual(snapshot["idle_ticks"], 0)
        self.assertEqual(snapshot["utilization_percentage"], 100.0)
        self.assertIsNotNone(snapshot["current_process"])
        self.assertEqual(snapshot["current_process"]["name"], "Monitoreo Térmico")


if __name__ == "__main__":
    unittest.main()
