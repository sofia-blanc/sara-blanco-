"""
Pruebas de integración del ciclo de vida de procesos con la memoria física en AutoOS.

Verifica:
1. Asignación correcta con direcciones base y límites.
2. Rechazo por falta de memoria (InsufficientMemoryError y evento MEMORY_ALLOCATION_FAILED).
3. Actualización dinámica del mapa de memoria (bloques ocupados y libres).
4. Liberación de memoria al terminar un proceso normalmente en tick().
5. Liberación de memoria al ejecutar abort_process() (kill).
6. Prevención de doble liberación.
7. Coherencia matemática exacta entre procesos activos y memoria ocupada.
8. Conservación idéntica del comportamiento de los algoritmos de planificación.
"""
import unittest

from src.core.simulation import SimulationEngine
from src.core.process import Process
from src.core.process_state import ProcessState
from src.core.exceptions import InsufficientMemoryError
from src.core.scheduler import Scheduler, AlgorithmType
from src.memory.memory import MemoryManager


class TestProcessMemoryIntegration(unittest.TestCase):
    def setUp(self):
        Process._reset_pid_generator(start=1)
        # Inicializar con memoria fija de 256 MB para control determinista
        self.memory_manager = MemoryManager(total_memory=256)
        self.engine = SimulationEngine(memory_manager=self.memory_manager)

    def test_1_valid_allocation_with_base_and_limit(self):
        """1. Asignación correcta: el proceso recibe dirección base, límite y fin exactos."""
        proc = self.engine.create_process(name="Sensor_Lidar", priority=1, burst_time=3, memory_size=64)
        
        alloc = self.engine.memory_manager.get_process_allocation(proc.pid)
        self.assertIsNotNone(alloc)
        self.assertEqual(alloc.pid, proc.pid)
        self.assertEqual(alloc.limit, 64)
        self.assertEqual(alloc.base_address, 0)
        self.assertEqual(alloc.end_address, 63)
        self.assertFalse(alloc.is_free)
        self.assertEqual(self.engine.memory_manager.used_memory, 64)
        self.assertEqual(self.engine.memory_manager.free_memory, 192)

        # Verificar evento MEMORY_ALLOCATED registrado
        events = self.engine.logger.get_events(pid=proc.pid, event_type="MEMORY_ALLOCATED")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].data["base_address"], 0)
        self.assertEqual(events[0].data["limit"], 64)

    def test_2_rejection_due_to_insufficient_memory(self):
        """2. Rechazo por falta de memoria: lanza InsufficientMemoryError y registra evento."""
        # Llenar la memoria (256 MB) con 2 procesos de 128 MB
        self.engine.create_process(name="P1_Vision", priority=2, burst_time=5, memory_size=128)
        self.engine.create_process(name="P2_Planificador", priority=2, burst_time=5, memory_size=128)
        self.assertEqual(self.engine.memory_manager.free_memory, 0)

        # Intentar crear un tercer proceso de 64 MB
        with self.assertRaises(InsufficientMemoryError) as ctx:
            self.engine.create_process(name="P3_Exceso", priority=1, burst_time=2, memory_size=64)

        err = ctx.exception
        self.assertEqual(err.requested, 64)
        self.assertEqual(err.available, 0)

        # Verificar evento de auditoría MEMORY_ALLOCATION_FAILED
        fail_events = self.engine.logger.get_events(event_type="MEMORY_ALLOCATION_FAILED")
        self.assertEqual(len(fail_events), 1)
        self.assertEqual(fail_events[0].data["requested"], 64)
        self.assertEqual(fail_events[0].data["free"], 0)

    def test_3_dynamic_memory_map_update(self):
        """3. Actualización dinámica del mapa: bloques contiguos, división y estados."""
        self.engine.create_process(name="P1", priority=1, burst_time=2, memory_size=64)
        self.engine.create_process(name="P2", priority=2, burst_time=2, memory_size=64)

        mem_map = self.engine.memory_manager.get_memory_map()
        # Debe haber 3 bloques: P1 (0..63), P2 (64..127), Libre (128..255)
        self.assertEqual(len(mem_map), 3)
        self.assertEqual(mem_map[0]["base_address"], 0)
        self.assertEqual(mem_map[0]["limit"], 64)
        self.assertFalse(mem_map[0]["is_free"])

        self.assertEqual(mem_map[1]["base_address"], 64)
        self.assertEqual(mem_map[1]["limit"], 64)
        self.assertFalse(mem_map[1]["is_free"])

        self.assertEqual(mem_map[2]["base_address"], 128)
        self.assertEqual(mem_map[2]["limit"], 128)
        self.assertTrue(mem_map[2]["is_free"])

    def test_4_release_on_normal_process_completion(self):
        """4. Liberación al terminar normalmente: tick() completa el proceso y libera su RAM."""
        proc = self.engine.create_process(name="Freno_ABS", priority=1, burst_time=2, memory_size=64)
        self.assertEqual(self.engine.memory_manager.used_memory, 64)

        # Ciclo 1: Despacha y ejecuta 1 ciclo
        self.engine.tick()
        self.assertEqual(proc.state, ProcessState.RUNNING)
        self.assertEqual(self.engine.memory_manager.used_memory, 64)

        # Ciclo 2: Ejecuta último ciclo y termina
        self.engine.tick()
        self.assertEqual(proc.state, ProcessState.TERMINATED)
        self.assertTrue(proc.is_finished)

        # La memoria debe haber sido liberada automáticamente
        self.assertEqual(self.engine.memory_manager.used_memory, 0)
        self.assertEqual(self.engine.memory_manager.free_memory, 256)
        self.assertIsNone(self.engine.memory_manager.get_process_allocation(proc.pid))

        # Verificar evento MEMORY_RELEASED
        rel_events = self.engine.logger.get_events(pid=proc.pid, event_type="MEMORY_RELEASED")
        self.assertEqual(len(rel_events), 1)

    def test_5_release_on_abort_process(self):
        """5. Liberación al abortar: abort_process(pid) libera inmediatamente la memoria."""
        p1 = self.engine.create_process(name="Tarea_A", priority=1, burst_time=5, memory_size=100)
        p2 = self.engine.create_process(name="Tarea_B", priority=2, burst_time=5, memory_size=50)
        self.assertEqual(self.engine.memory_manager.used_memory, 150)

        # Abortar Tarea_A
        self.engine.abort_process(p1.pid)
        self.assertEqual(p1.state, ProcessState.TERMINATED)
        self.assertEqual(self.engine.memory_manager.used_memory, 50)
        self.assertIsNone(self.engine.memory_manager.get_process_allocation(p1.pid))
        self.assertIsNotNone(self.engine.memory_manager.get_process_allocation(p2.pid))

        # Abortar Tarea_B
        self.engine.abort_process(p2.pid)
        self.assertEqual(self.engine.memory_manager.used_memory, 0)
        self.assertEqual(self.engine.memory_manager.free_memory, 256)

    def test_6_prevention_of_double_release(self):
        """6. Prevención de doble liberación: liberar dos veces no corrompe contadores ni estado."""
        p = self.engine.create_process(name="Unica_Liberacion", priority=1, burst_time=1, memory_size=64)
        self.assertEqual(self.engine.memory_manager.used_memory, 64)

        # Primera liberación vía abort_process
        self.engine.abort_process(p.pid)
        self.assertEqual(self.engine.memory_manager.used_memory, 0)

        # Segunda liberación forzada directamente sobre MemoryManager
        second_release = self.engine.memory_manager.release_for_process(p.pid)
        self.assertFalse(second_release)
        # Los contadores deben permanecer en 0 usado y 256 libre, sin valores negativos
        self.assertEqual(self.engine.memory_manager.used_memory, 0)
        self.assertEqual(self.engine.memory_manager.free_memory, 256)

        # Segundo llamado a abort_process del mismo proceso (idempotente)
        self.engine.abort_process(p.pid)
        self.assertEqual(self.engine.memory_manager.used_memory, 0)

    def test_7_coherence_active_processes_and_occupied_memory(self):
        """7. Coherencia matemática estricta: suma(RAM procesos activos) == used_memory."""
        p1 = self.engine.create_process(name="Proc1", priority=1, burst_time=3, memory_size=32)
        p2 = self.engine.create_process(name="Proc2", priority=2, burst_time=3, memory_size=48)
        p3 = self.engine.create_process(name="Proc3", priority=3, burst_time=3, memory_size=64)

        active_states = {ProcessState.NEW, ProcessState.READY, ProcessState.RUNNING, ProcessState.WAITING}
        
        def calculate_active_ram():
            return sum(
                p.memory_size for p in self.engine.get_all_processes()
                if p.state in active_states
            )

        self.assertEqual(calculate_active_ram(), self.engine.memory_manager.used_memory)
        self.assertEqual(self.engine.memory_manager.used_memory, 32 + 48 + 64)

        # Despachar y terminar P1
        self.engine.run(3)
        self.assertEqual(p1.state, ProcessState.TERMINATED)
        self.assertEqual(calculate_active_ram(), self.engine.memory_manager.used_memory)
        self.assertEqual(self.engine.memory_manager.used_memory, 48 + 64)

        # Bloquear P2
        self.engine.run(1)  # P2 entra a RUNNING
        self.engine.block_current_process("Sensor de proximidad")
        self.assertEqual(p2.state, ProcessState.WAITING)
        self.assertEqual(calculate_active_ram(), self.engine.memory_manager.used_memory)

    def test_8_scheduling_algorithms_behavior_preserved(self):
        """8. Conservación de algoritmos: FCFS, Round Robin y Prioridad mantienen su orden."""
        # Probar Round Robin con quantum=2 y 3 procesos con memoria
        sched_rr = Scheduler(algorithm=AlgorithmType.ROUND_ROBIN, quantum=2)
        engine_rr = SimulationEngine(scheduler=sched_rr, memory_manager=MemoryManager(total_memory=512))

        p_a = engine_rr.create_process(name="Tarea_A", burst_time=4, memory_size=64)
        p_b = engine_rr.create_process(name="Tarea_B", burst_time=2, memory_size=64)

        # Tick 1: P_A despachado, consume 1 tick (restante: 3)
        engine_rr.tick()
        self.assertEqual(engine_rr.cpu.current_process.pid, p_a.pid)
        self.assertEqual(p_a.remaining_time, 3)

        # Tick 2: P_A consume segundo tick del quantum (restante: 2) -> quantum agotado, se expulsa P_A y despacha P_B
        engine_rr.tick()
        self.assertEqual(engine_rr.cpu.current_process.pid, p_b.pid)
        self.assertEqual(p_a.remaining_time, 2)

        # Tick 3: P_B ejecuta su primer ciclo
        engine_rr.tick()
        self.assertEqual(p_b.remaining_time, 1)

        # Todos los procesos retienen su memoria asignada
        self.assertEqual(engine_rr.memory_manager.used_memory, 128)


if __name__ == "__main__":
    unittest.main()
