import unittest
from src.core.scheduler import Scheduler, AlgorithmType
from src.core.process import Process
from src.core.process_state import ProcessState
from src.core.cpu import CPU

class TestSchedulingAlgorithms(unittest.TestCase):
    def setUp(self):
        self.cpu = CPU()

    def test_fcfs_order(self):
        """Prueba que en FCFS el despacho respeta el orden estricto de llegada ignorando prioridad."""
        sched = Scheduler(algorithm=AlgorithmType.FCFS)
        p1 = Process(name="P1_LowPrio", priority=5, burst_time=4)
        p1.transition_to(ProcessState.READY)
        p2 = Process(name="P2_HighPrio", priority=1, burst_time=2)
        p2.transition_to(ProcessState.READY)
        
        sched.add_process(p1)
        sched.add_process(p2)
        
        first = sched.get_next_process()
        self.assertEqual(first.pid, p1.pid)
        second = sched.get_next_process()
        self.assertEqual(second.pid, p2.pid)

    def test_priority_scheduling(self):
        """Prueba que en Prioridad se despacha antes la prioridad numérica menor (1 = Crítica)."""
        sched = Scheduler(algorithm=AlgorithmType.PRIORITY)
        p1 = Process(name="P1_LowPrio", priority=4, burst_time=4)
        p1.transition_to(ProcessState.READY)
        p2 = Process(name="P2_Critica", priority=1, burst_time=2)
        p2.transition_to(ProcessState.READY)
        
        sched.add_process(p1)
        sched.add_process(p2)
        
        # Prioridad 1 debe despacharse antes que Prioridad 4
        first = sched.get_next_process()
        self.assertEqual(first.pid, p2.pid)
        second = sched.get_next_process()
        self.assertEqual(second.pid, p1.pid)

    def test_round_robin_quantum_tick(self):
        """Prueba la rotación de quantum en Round Robin."""
        sched = Scheduler(algorithm=AlgorithmType.ROUND_ROBIN, quantum=2)
        p1 = Process(name="P1", priority=3, burst_time=5)
        p1.transition_to(ProcessState.READY)
        p2 = Process(name="P2", priority=3, burst_time=3)
        p2.transition_to(ProcessState.READY)
        
        sched.add_process(p1)
        sched.add_process(p2)
        
        # Despachar a CPU
        dispatched = sched.dispatch(self.cpu)
        self.assertEqual(dispatched.pid, p1.pid)
        self.assertEqual(sched.quantum_remaining, 2)

        # 1er tick
        sched.handle_round_robin_tick(self.cpu)
        self.assertEqual(sched.quantum_remaining, 1)

        # 2do tick: expira quantum, se desaloja P1 y despacha P2
        next_dispatched = sched.handle_round_robin_tick(self.cpu)
        self.assertIsNotNone(next_dispatched)
        self.assertEqual(next_dispatched.pid, p2.pid)
        self.assertEqual(self.cpu.current_process.pid, p2.pid)

    def test_low_battery_simulator(self):
        """Prueba que el modo batería baja suspende procesos no esenciales (prioridad >= 4)."""
        sched = Scheduler(algorithm=AlgorithmType.PRIORITY)
        p_vital = Process(name="Frenos_ABS", priority=1, burst_time=3)
        p_vital.transition_to(ProcessState.READY)
        p_confort = Process(name="Multimedia_Audio", priority=5, burst_time=6)
        p_confort.transition_to(ProcessState.READY)
        
        sched.add_process(p_vital)
        sched.add_process(p_confort)
        self.assertEqual(sched.ready_count, 2)
        
        # Activar batería baja
        suspended = sched.set_low_battery_mode(True)
        self.assertIn(p_confort.pid, suspended)
        self.assertEqual(sched.ready_count, 1) # Solo queda el proceso vital
        self.assertEqual(sched.peek_next_process().pid, p_vital.pid)
        
        # Desactivar batería baja
        restored = sched.set_low_battery_mode(False)
        self.assertIn(p_confort.pid, restored)
        self.assertEqual(sched.ready_count, 2)

    def test_critical_process_injection_preemption(self):
        """Prueba la inyección de proceso crítico con desalojo (preemption) de CPU."""
        sched = Scheduler(algorithm=AlgorithmType.PRIORITY)
        p_normal = Process(name="GPS_Mapas", priority=3, burst_time=8)
        p_normal.transition_to(ProcessState.READY)
        sched.add_process(p_normal)
        sched.dispatch(self.cpu)
        self.assertEqual(self.cpu.current_process.pid, p_normal.pid)
        
        # Inyectar proceso crítico (Frenado Autónomo)
        p_crit = Process(name="Frenado_Emergencia_AEB", priority=1, burst_time=2)
        p_crit.transition_to(ProcessState.READY)
        sched.inject_critical_process(p_crit, cpu=self.cpu, preemptive=True)
        
        # La CPU debe tener ahora el proceso crítico cargado
        self.assertEqual(self.cpu.current_process.pid, p_crit.pid)
        # El proceso normal debe haber vuelto a la cola de listos
        self.assertEqual(sched.ready_count, 1)
        self.assertEqual(sched.peek_next_process().pid, p_normal.pid)

if __name__ == '__main__':
    unittest.main()
