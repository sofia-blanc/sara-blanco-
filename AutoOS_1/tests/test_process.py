"""
Pruebas unitarias para el PCB y la máquina de estados de AutoOS (Etapa 1).
"""
import unittest

from src.core.process_state import ProcessState
from src.core.exceptions import (
    InvalidStateTransitionError,
    InvalidProcessPriorityError,
    InvalidProcessAttributeError,
)
from src.core.process import Process


class TestProcessLifecycleAndPCB(unittest.TestCase):
    """Suite de pruebas para validar el Bloque de Control de Proceso (PCB) y transiciones."""

    def setUp(self):
        """Reinicia el generador de PIDs antes de cada prueba para mantener aislamiento."""
        Process._reset_pid_generator(start=1)

    def test_process_creation_and_unique_pid(self):
        """Verifica la asignación secuencial y única de PIDs y los valores por defecto."""
        p1 = Process(name="Control de Frenado ABS", priority=1, burst_time=5)
        p2 = Process(name="Inyección de Combustible", priority=2, burst_time=3)
        p3 = Process(name="Infoentretenimiento")  # defaults: priority=3, burst=1

        self.assertEqual(p1.pid, 1)
        self.assertEqual(p2.pid, 2)
        self.assertEqual(p3.pid, 3)

        self.assertEqual(p1.state, ProcessState.NEW)
        self.assertEqual(p1.burst_time, 5)
        self.assertEqual(p1.remaining_time, 5)
        self.assertFalse(p1.is_finished)

        # Verificar inmutabilidad del PID
        with self.assertRaises(AttributeError):
            p1.pid = 999  # No se permite reasignar el PID

    def test_priority_range_and_validation(self):
        """Valida que la prioridad respete la escala de 1 (Crítica) a 5 (Baja)."""
        # Prioridades válidas en los límites
        p_critico = Process(name="Freno de Emergencia", priority=1)
        p_bajo = Process(name="Luz Ambiental", priority=5)

        self.assertEqual(p_critico.priority, 1)
        self.assertEqual(p_bajo.priority, 5)

        # Prioridades inválidas (< 1 o > 5)
        with self.assertRaises(InvalidProcessPriorityError):
            Process(name="Sensor Lidar", priority=0)

        with self.assertRaises(InvalidProcessPriorityError):
            Process(name="Radio FM", priority=6)

        with self.assertRaises(InvalidProcessPriorityError):
            Process(name="Climatizador", priority=-3)

        # Modificación válida de prioridad en tiempo de ejecución
        p_bajo.priority = 2
        self.assertEqual(p_bajo.priority, 2)

        # Modificación inválida
        with self.assertRaises(InvalidProcessPriorityError):
            p_bajo.priority = 10

    def test_invalid_attributes_on_creation(self):
        """Valida que no se puedan crear procesos con nombres vacíos o ráfagas <= 0."""
        with self.assertRaises(InvalidProcessAttributeError):
            Process(name="", priority=2, burst_time=2)

        with self.assertRaises(InvalidProcessAttributeError):
            Process(name="   ", priority=2, burst_time=2)

        with self.assertRaises(InvalidProcessAttributeError):
            Process(name="Monitoreo Batería", priority=2, burst_time=0)

        with self.assertRaises(InvalidProcessAttributeError):
            Process(name="Monitoreo Batería", priority=2, burst_time=-5)

    def test_canonical_lifecycle_transitions(self):
        """
        Prueba el ciclo de vida canónico completo de un proceso de SO:
        NEW -> READY -> RUNNING -> READY (expulsión) -> RUNNING -> WAITING (bloqueo)
            -> READY (desbloqueo) -> RUNNING -> TERMINATED (finalización).
        """
        p = Process(name="Navegación GPS", priority=2, burst_time=4)
        self.assertEqual(p.state, ProcessState.NEW)

        # 1. NEW -> READY (Admisión al sistema)
        p.admit()
        self.assertEqual(p.state, ProcessState.READY)

        # 2. READY -> RUNNING (Despacho a CPU)
        p.dispatch()
        self.assertEqual(p.state, ProcessState.RUNNING)

        # 3. RUNNING -> READY (Preempción / fin de quantum)
        p.preempt()
        self.assertEqual(p.state, ProcessState.READY)

        # 4. READY -> RUNNING (Re-despacho a CPU)
        p.dispatch()
        self.assertEqual(p.state, ProcessState.RUNNING)

        # 5. RUNNING -> WAITING (Espera de datos de satélite / E/S)
        p.block()
        self.assertEqual(p.state, ProcessState.WAITING)

        # 6. WAITING -> READY (Datos recibidos, vuelve a cola de listos)
        p.unblock()
        self.assertEqual(p.state, ProcessState.READY)

        # 7. READY -> RUNNING (Despacho final)
        p.dispatch()
        self.assertEqual(p.state, ProcessState.RUNNING)

        # 8. RUNNING -> TERMINATED (Finalización de tarea)
        p.terminate()
        self.assertEqual(p.state, ProcessState.TERMINATED)
        self.assertTrue(p.is_finished)

    def test_abort_from_new_ready_and_waiting(self):
        """Verifica que un proceso pueda ser abortado directamente desde NEW, READY o WAITING."""
        # Abortar desde NEW
        p0 = Process(name="Tarea Cancelada 0", priority=2)
        p0.terminate()
        self.assertEqual(p0.state, ProcessState.TERMINATED)
        self.assertTrue(p0.is_finished)

        # Abortar desde READY
        p1 = Process(name="Tarea Cancelada 1", priority=3)
        p1.admit()
        p1.terminate()
        self.assertEqual(p1.state, ProcessState.TERMINATED)

        # Abortar desde WAITING
        p2 = Process(name="Tarea Cancelada 2", priority=3)
        p2.admit()
        p2.dispatch()
        p2.block()
        p2.terminate()
        self.assertEqual(p2.state, ProcessState.TERMINATED)

    def test_strict_invalid_transitions_rejection(self):
        """Verifica que las transiciones ilegales sean rechazadas con InvalidStateTransitionError."""
        p = Process(name="Control de Tracción", priority=1)

        # Desde NEW no se puede ir directo a RUNNING ni WAITING
        with self.assertRaises(InvalidStateTransitionError):
            p.dispatch()  # NEW -> RUNNING (ilegal: debe admitirse primero)

        with self.assertRaises(InvalidStateTransitionError):
            p.block()     # NEW -> WAITING (ilegal)

        # Pasamos a READY
        p.admit()


        # Desde READY no se puede ir a WAITING
        with self.assertRaises(InvalidStateTransitionError):
            p.block()     # READY -> WAITING (ilegal: solo un proceso en ejecución se bloquea)

        # Pasamos a RUNNING y luego a WAITING
        p.dispatch()
        p.block()

        # Desde WAITING no se puede ir directo a RUNNING (debe pasar por READY)
        with self.assertRaises(InvalidStateTransitionError):
            p.dispatch()  # WAITING -> RUNNING (ilegal)

    def test_terminated_is_a_terminal_state(self):
        """Verifica que un proceso TERMINATED no pueda cambiar de estado bajo ninguna circunstancia."""
        p = Process(name="Tarea Efímera", priority=3)
        p.admit()
        p.dispatch()
        p.terminate()

        self.assertEqual(p.state, ProcessState.TERMINATED)

        # Intentar cualquier transición desde TERMINATED debe fallar
        with self.assertRaises(InvalidStateTransitionError):
            p.admit()

        with self.assertRaises(InvalidStateTransitionError):
            p.dispatch()

        with self.assertRaises(InvalidStateTransitionError):
            p.preempt()

        with self.assertRaises(InvalidStateTransitionError):
            p.block()

        with self.assertRaises(InvalidStateTransitionError):
            p.unblock()

        with self.assertRaises(InvalidStateTransitionError):
            p.terminate()

        # Tampoco debe permitirse modificar su prioridad
        with self.assertRaises(InvalidStateTransitionError):
            p.priority = 1

    def test_cpu_tick_consumption_and_auto_termination(self):
        """Verifica el consumo de ciclos de CPU y la transición automática a TERMINATED."""
        p = Process(name="Sensor de Presión de Llantas", priority=3, burst_time=3)
        
        # Consumir ticks sin estar en RUNNING debe fallar
        with self.assertRaises(InvalidStateTransitionError):
            p.consume_cpu_tick()  # En estado NEW

        p.admit()
        with self.assertRaises(InvalidStateTransitionError):
            p.consume_cpu_tick()  # En estado READY

        p.dispatch()  # Ahora en RUNNING

        # Tick 1: restante pasa de 3 a 2
        rem1 = p.consume_cpu_tick()
        self.assertEqual(rem1, 2)
        self.assertEqual(p.state, ProcessState.RUNNING)

        # Tick 2: restante pasa de 2 a 1
        rem2 = p.consume_cpu_tick()
        self.assertEqual(rem2, 1)
        self.assertEqual(p.state, ProcessState.RUNNING)

        # Tick 3: restante llega a 0 -> Se auto-termina
        rem3 = p.consume_cpu_tick()
        self.assertEqual(rem3, 0)
        self.assertEqual(p.state, ProcessState.TERMINATED)
        self.assertTrue(p.is_finished)

        # Un tick adicional cuando ya está TERMINATED debe fallar
        with self.assertRaises(InvalidStateTransitionError):
            p.consume_cpu_tick()

    def test_to_dict_serialization_for_future_integration(self):
        """Valida que to_dict() devuelva la estructura de datos requerida por el Dashboard y Supabase."""
        p = Process(name="Detección de Peatones", priority=1, burst_time=4)
        p.admit()
        p.dispatch()
        p.consume_cpu_tick()  # Quedan 3 ticks

        data = p.to_dict()

        self.assertIsInstance(data, dict)
        self.assertEqual(data["pid"], 1)
        self.assertEqual(data["name"], "Detección de Peatones")
        self.assertEqual(data["priority"], 1)
        self.assertEqual(data["state"], "RUNNING")
        self.assertEqual(data["burst_time"], 4)
        self.assertEqual(data["remaining_time"], 3)
        self.assertFalse(data["is_finished"])


if __name__ == "__main__":
    unittest.main()
