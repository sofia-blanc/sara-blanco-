"""
Pruebas unitarias para el Planificador por Prioridad de AutoOS (Etapa 3).
"""
import unittest

from src.core.process_state import ProcessState
from src.core.process import Process
from src.core.cpu import CPU
from src.core.scheduler import Scheduler
from src.core.exceptions import (
    DuplicateProcessError,
    InvalidStateTransitionError,
    InvalidProcessAttributeError,
)


class TestPriorityScheduler(unittest.TestCase):
    """Suite de pruebas para validar la cola de listos y la política del Scheduler."""

    def setUp(self):
        """Reinicia el contador de PIDs y crea instancias frescas de CPU y Scheduler."""
        Process._reset_pid_generator(start=1)
        self.cpu = CPU()
        self.scheduler = Scheduler()

    def test_empty_scheduler_behavior(self):
        """Verifica el comportamiento de una cola de listos vacía."""
        self.assertTrue(self.scheduler.is_empty)
        self.assertEqual(self.scheduler.ready_count, 0)
        self.assertIsNone(self.scheduler.peek_next_process())
        self.assertIsNone(self.scheduler.get_next_process())

        # Despacho con cola vacía
        dispatched = self.scheduler.dispatch(self.cpu)
        self.assertIsNone(dispatched)
        self.assertTrue(self.cpu.is_idle)

    def test_priority_ordering_selection(self):
        """
        Verifica que los procesos se seleccionen en estricto orden de prioridad
        (menor número = mayor prioridad: 1 antes que 2, 2 antes que 3, etc.).
        """
        # Se crean procesos y se admiten a READY
        p_baja = Process(name="Climatizador", priority=5)
        p_media = Process(name="Control Luces", priority=3)
        p_critica = Process(name="Frenado ABS", priority=1)
        p_alta = Process(name="Dirección Asistida", priority=2)

        p_baja.admit()
        p_media.admit()
        p_critica.admit()
        p_alta.admit()

        # Se encolan en orden desordenado
        self.scheduler.add_process(p_baja)     # Prioridad 5
        self.scheduler.add_process(p_media)    # Prioridad 3
        self.scheduler.add_process(p_critica)  # Prioridad 1
        self.scheduler.add_process(p_alta)     # Prioridad 2

        self.assertEqual(self.scheduler.ready_count, 4)

        # La extracción debe ser: 1, 2, 3, 5
        self.assertEqual(self.scheduler.get_next_process().pid, p_critica.pid)
        self.assertEqual(self.scheduler.get_next_process().pid, p_alta.pid)
        self.assertEqual(self.scheduler.get_next_process().pid, p_media.pid)
        self.assertEqual(self.scheduler.get_next_process().pid, p_baja.pid)
        self.assertTrue(self.scheduler.is_empty)

    def test_fifo_tie_breaking_for_equal_priorities(self):
        """
        Verifica que en caso de igualdad de prioridad numérica,
        se respete estrictamente la política FIFO (orden de llegada).
        """
        p1 = Process(name="Tarea A", priority=2)
        p2 = Process(name="Tarea B", priority=2)
        p3 = Process(name="Tarea C", priority=2)

        p1.admit()
        p2.admit()
        p3.admit()

        # Llegan en orden p1 -> p2 -> p3
        self.scheduler.add_process(p1)
        self.scheduler.add_process(p2)
        self.scheduler.add_process(p3)

        # Deben salir exactamente en orden p1 -> p2 -> p3
        self.assertIs(self.scheduler.get_next_process(), p1)
        self.assertIs(self.scheduler.get_next_process(), p2)
        self.assertIs(self.scheduler.get_next_process(), p3)

    def test_mixed_priority_and_fifo_tie_breaking(self):
        """
        Verifica un escenario mixto de prioridades con múltiples empates.
        """
        p_crit_1 = Process(name="Freno 1", priority=1)
        p_med_1 = Process(name="Radio 1", priority=3)
        p_crit_2 = Process(name="Freno 2", priority=1)
        p_med_2 = Process(name="Radio 2", priority=3)

        for p in [p_crit_1, p_med_1, p_crit_2, p_med_2]:
            p.admit()
            self.scheduler.add_process(p)

        # Orden esperado: p_crit_1 (prio 1, llegó 1ro), p_crit_2 (prio 1, llegó 2do),
        # p_med_1 (prio 3, llegó 1ro), p_med_2 (prio 3, llegó 2do)
        self.assertIs(self.scheduler.get_next_process(), p_crit_1)
        self.assertIs(self.scheduler.get_next_process(), p_crit_2)
        self.assertIs(self.scheduler.get_next_process(), p_med_1)
        self.assertIs(self.scheduler.get_next_process(), p_med_2)

    def test_reject_processes_not_in_ready_state(self):
        """Verifica que solo se admitan procesos en estado READY."""
        # 1. Proceso en NEW
        p_new = Process(name="Proceso Nuevo", priority=2)
        with self.assertRaises(InvalidStateTransitionError):
            self.scheduler.add_process(p_new)

        # 2. Proceso en RUNNING
        p_running = Process(name="Proceso Ejecutando", priority=2)
        p_running.admit()
        p_running.dispatch()
        with self.assertRaises(InvalidStateTransitionError):
            self.scheduler.add_process(p_running)

        # 3. Proceso en WAITING
        p_waiting = Process(name="Proceso Bloqueado", priority=2)
        p_waiting.admit()
        p_waiting.dispatch()
        p_waiting.block()
        with self.assertRaises(InvalidStateTransitionError):
            self.scheduler.add_process(p_waiting)

        # 4. Proceso en TERMINATED
        p_term = Process(name="Proceso Terminado", priority=2)
        p_term.admit()
        p_term.terminate()
        with self.assertRaises(InvalidStateTransitionError):
            self.scheduler.add_process(p_term)

        self.assertTrue(self.scheduler.is_empty)

    def test_prevent_duplicate_processes_in_queue(self):
        """Verifica que no se pueda agregar dos veces el mismo proceso a la cola de listos."""
        p = Process(name="Sensor Lidar", priority=2)
        p.admit()

        self.scheduler.add_process(p)
        self.assertEqual(self.scheduler.ready_count, 1)

        # Intento de duplicación
        with self.assertRaises(DuplicateProcessError) as ctx:
            self.scheduler.add_process(p)

        self.assertEqual(ctx.exception.pid, p.pid)
        self.assertEqual(self.scheduler.ready_count, 1)

    def test_dispatch_to_idle_cpu(self):
        """Verifica el despacho exitoso del proceso con mayor prioridad a una CPU ociosa."""
        p1 = Process(name="Tarea Normal", priority=3, burst_time=4)
        p2 = Process(name="Tarea Urgente", priority=1, burst_time=2)
        p1.admit()
        p2.admit()

        self.scheduler.add_process(p1)
        self.scheduler.add_process(p2)

        # Despacho
        dispatched = self.scheduler.dispatch(self.cpu)

        # Debe despachar a p2 (mayor prioridad)
        self.assertIs(dispatched, p2)
        self.assertFalse(self.cpu.is_idle)
        self.assertIs(self.cpu.current_process, p2)
        self.assertEqual(p2.state, ProcessState.RUNNING)

        # p1 sigue en la cola de listos
        self.assertEqual(self.scheduler.ready_count, 1)
        self.assertIs(self.scheduler.peek_next_process(), p1)

    def test_safe_retry_when_cpu_is_busy(self):
        """
        Verifica que si la CPU está ocupada, dispatch() retorne None de forma segura
        sin perder elementos de la cola ni alterar ningún estado.
        """
        # Cargar manualmente un proceso a la CPU
        p_active = Process(name="Proceso en Ejecución", priority=4, burst_time=5)
        p_active.admit()
        self.cpu.load_process(p_active)

        # Encolar un proceso de máxima prioridad en el planificador
        p_waiting = Process(name="Alerta Crítica", priority=1, burst_time=1)
        p_waiting.admit()
        self.scheduler.add_process(p_waiting)

        # Intentar despacho
        result = self.scheduler.dispatch(self.cpu)

        # Garantías:
        self.assertIsNone(result)
        # La CPU sigue con el proceso original
        self.assertIs(self.cpu.current_process, p_active)
        self.assertEqual(p_active.state, ProcessState.RUNNING)
        # El proceso en cola no se perdió y sigue en READY
        self.assertEqual(self.scheduler.ready_count, 1)
        self.assertIs(self.scheduler.peek_next_process(), p_waiting)
        self.assertEqual(p_waiting.state, ProcessState.READY)

    def test_non_preemptive_policy(self):
        """
        Verifica la política no apropiativa: la llegada de un proceso de prioridad 1
        no desaloja a un proceso de prioridad 5 que ya está ejecutándose en la CPU.
        """
        p_low = Process(name="Música de Fondo", priority=5, burst_time=3)
        p_low.admit()
        self.cpu.load_process(p_low)

        p_crit = Process(name="Sensor de Impacto", priority=1, burst_time=1)
        p_crit.admit()
        self.scheduler.add_process(p_crit)

        # La CPU sigue ejecutando el de baja prioridad
        self.assertIs(self.cpu.current_process, p_low)
        self.cpu.tick()
        self.assertEqual(p_low.remaining_time, 2)
        self.assertIs(self.cpu.current_process, p_low)

    def test_requeue_after_preemption(self):
        """
        Verifica que un proceso expulsado de la CPU (preempt) y retornado a READY
        pueda volver a encolarse en el Scheduler respetando las reglas de prioridad.
        """
        p1 = Process(name="Tarea Reversible", priority=2, burst_time=5)
        p1.admit()
        self.cpu.load_process(p1)
        self.cpu.tick()  # consumió 1 tick

        # Expulsar de CPU -> vuelve a READY
        preempted = self.cpu.preempt_process()
        self.assertEqual(preempted.state, ProcessState.READY)

        # Reingreso al planificador
        self.scheduler.add_process(preempted)
        self.assertEqual(self.scheduler.ready_count, 1)
        self.assertIs(self.scheduler.peek_next_process(), preempted)

        # Ahora puede ser despachado de nuevo
        dispatched = self.scheduler.dispatch(self.cpu)
        self.assertIs(dispatched, p1)
        self.assertEqual(p1.state, ProcessState.RUNNING)

    def test_get_ready_processes_inspection(self):
        """Verifica que get_ready_processes() entregue una copia ordenada sin alterar la cola."""
        p_b = Process(name="B", priority=3)
        p_a = Process(name="A", priority=1)
        p_c = Process(name="C", priority=2)

        for p in [p_b, p_a, p_c]:
            p.admit()
            self.scheduler.add_process(p)

        view = self.scheduler.get_ready_processes()
        self.assertEqual([p.name for p in view], ["A", "C", "B"])
        # La cola interna sigue conteniendo los 3 elementos
        self.assertEqual(self.scheduler.ready_count, 3)

    def test_to_dict_serialization(self):
        """Verifica que to_dict() devuelva los metadatos de la cola en formato compatible con JSON."""
        p = Process(name="Telemetría", priority=2, burst_time=3)
        p.admit()
        self.scheduler.add_process(p)

        data = self.scheduler.to_dict()
        self.assertEqual(data["ready_count"], 1)
        self.assertFalse(data["is_empty"])
        self.assertEqual(len(data["ready_processes"]), 1)
        self.assertEqual(data["ready_processes"][0]["name"], "Telemetría")


if __name__ == "__main__":
    unittest.main()
