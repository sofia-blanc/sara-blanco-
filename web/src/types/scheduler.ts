export type ProcessState = 'NUEVO' | 'LISTO' | 'EJECUTANDO' | 'BLOQUEADO' | 'TERMINADO' | 'SUSPENDIDO';

export type UserRole = 'mecanico' | 'conductor' | 'pasajero';

export type ProcessPriority = 1 | 2 | 3 | 4 | 5; // 1 = Crítica, 5 = Muy Baja

export type AlgorithmType = 'FCFS' | 'RR' | 'PRIORITY' | 'PRIORITY_PREEMPTIVE';

export type ProcessCategory = 'seguridad' | 'control' | 'sensor' | 'confort' | 'multimedia';

export interface Process {
  pid: number;
  name: string;
  category: ProcessCategory;
  arrivalTime: number;
  burstTime: number;
  remainingTime: number;
  priority: ProcessPriority; // 1 (crítico) to 5 (muy bajo)
  critical: boolean;
  color: string;
  state: ProcessState;
  // Metrics calculated during/after simulation
  startTime?: number;
  completionTime?: number;
  waitingTime: number;
  turnaroundTime: number;
  responseTime?: number;
  // Low battery handling
  suspendedDueToBattery?: boolean;
  powerConsumptionWatts: number; // Watts drawn while running
  cpuUsagePct: number;
  memoryMb: number;
}

export interface GanttSlot {
  id: string;
  processId: number | null; // null for idle
  processName: string;
  start: number;
  end: number;
  color: string;
  isCritical: boolean;
  isIdle: boolean;
  quantumUsed?: number;
}

export interface SimulationEvent {
  id: string;
  time: number;
  timestamp: string;
  type: 'DISPATCH' | 'PREEMPTION' | 'COMPLETION' | 'ARRIVAL' | 'BATTERY_ALERT' | 'CRITICAL_INJECT' | 'STATE_CHANGE' | 'QUANTUM_EXPIRED';
  message: string;
  pid?: number;
  severity: 'info' | 'warning' | 'critical' | 'success';
}

export interface SchedulerMetrics {
  currentTime: number;
  cpuUtilization: number; // 0 - 100%
  averageWaitingTime: number;
  averageTurnaroundTime: number;
  averageResponseTime: number;
  completedCount: number;
  totalProcesses: number;
  throughput: number; // processes per unit time
  contextSwitches: number;
}

export interface BatteryState {
  level: number; // 0 - 100%
  voltage: number; // e.g. 395V
  temperature: number; // °C
  isLowBatteryMode: boolean;
  isCriticalBatteryMode: boolean;
  autoThrottlingEnabled: boolean;
  powerSavingWattsSaved: number;
}
