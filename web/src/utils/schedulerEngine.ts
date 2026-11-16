import { AlgorithmType, GanttSlot, Process, SchedulerMetrics, SimulationEvent } from '../types/scheduler';

export interface SimulationState {
  currentTime: number;
  algorithm: AlgorithmType;
  quantum: number;
  quantumRemaining: number;
  processes: Process[];
  readyQueue: Process[];
  runningProcess: Process | null;
  ganttSlots: GanttSlot[];
  events: SimulationEvent[];
  isFinished: boolean;
  contextSwitchCount: number;
  totalIdleTime: number;
  preemptedProcessId: number | null;
}

export function createInitialSimulationState(
  initialProcs: Process[],
  algorithm: AlgorithmType = 'RR',
  quantum: number = 2
): SimulationState {
  const clonedProcesses: Process[] = initialProcs.map(p => ({
    ...p,
    remainingTime: p.burstTime,
    state: 'NUEVO',
    waitingTime: 0,
    turnaroundTime: 0,
    startTime: undefined,
    completionTime: undefined,
    responseTime: undefined,
    suspendedDueToBattery: false,
  }));

  // Initial check for processes that arrived at t = 0
  const ready: Process[] = [];
  clonedProcesses.forEach(p => {
    if (p.arrivalTime === 0) {
      p.state = 'LISTO';
      ready.push(p);
    }
  });

  sortReadyQueue(ready, algorithm);

  return {
    currentTime: 0,
    algorithm,
    quantum,
    quantumRemaining: quantum,
    processes: clonedProcesses,
    readyQueue: ready,
    runningProcess: null,
    ganttSlots: [],
    events: [
      {
        id: 'evt-init',
        time: 0,
        timestamp: new Date().toLocaleTimeString(),
        type: 'STATE_CHANGE',
        message: `Simulador iniciado con algoritmo [${getAlgorithmName(algorithm)}]${algorithm === 'RR' ? ` (Quantum = ${quantum})` : ''}.`,
        severity: 'info',
      },
    ],
    isFinished: false,
    contextSwitchCount: 0,
    totalIdleTime: 0,
    preemptedProcessId: null,
  };
}

export function getAlgorithmName(alg: AlgorithmType): string {
  switch (alg) {
    case 'FCFS':
      return 'FCFS (First-Come, First-Served)';
    case 'RR':
      return 'Round Robin (Turno Rotativo)';
    case 'PRIORITY':
      return 'Prioridad No Apropiativa';
    case 'PRIORITY_PREEMPTIVE':
      return 'Prioridad Apropiativa (Preemptive)';
  }
}

/**
 * Sorts or reorders ready queue based on algorithm.
 */
export function sortReadyQueue(queue: Process[], algorithm: AlgorithmType): void {
  if (algorithm === 'PRIORITY' || algorithm === 'PRIORITY_PREEMPTIVE') {
    // Priority: lower number = higher priority (1 is highest, 5 is lowest)
    // Tie-breaker: earlier arrival time, then PID
    queue.sort((a, b) => {
      if (a.priority !== b.priority) {
        return a.priority - b.priority;
      }
      if (a.arrivalTime !== b.arrivalTime) {
        return a.arrivalTime - b.arrivalTime;
      }
      return a.pid - b.pid;
    });
  } else if (algorithm === 'FCFS') {
    queue.sort((a, b) => {
      if (a.arrivalTime !== b.arrivalTime) {
        return a.arrivalTime - b.arrivalTime;
      }
      return a.pid - b.pid;
    });
  }
  // For RR, queue is maintained in FIFO order as processes arrive and are pushed back to the tail
}

/**
 * Execute 1 single simulation time unit tick (t -> t + 1)
 */
export function stepSimulationTick(
  prevState: SimulationState,
  isLowBatteryActive: boolean = false
): SimulationState {
  if (prevState.isFinished) {
    return prevState;
  }

  const state: SimulationState = {
    ...prevState,
    processes: prevState.processes.map(p => ({ ...p })),
    readyQueue: prevState.readyQueue.map(p => ({ ...p })),
    runningProcess: prevState.runningProcess ? { ...prevState.runningProcess } : null,
    ganttSlots: prevState.ganttSlots.map(s => ({ ...s })),
    events: [...prevState.events],
    preemptedProcessId: null,
  };

  const t = state.currentTime;

  // 1. Process Arrivals at current time t (if t > 0, arrival at t = 0 was handled in init or previous ticks)
  state.processes.forEach(proc => {
    if (proc.arrivalTime === t && proc.state === 'NUEVO') {
      if (isLowBatteryActive && (proc.category === 'multimedia' || proc.priority >= 4)) {
        proc.state = 'SUSPENDIDO';
        proc.suspendedDueToBattery = true;
        state.events.unshift({
          id: `evt-arr-susp-${proc.pid}-${t}`,
          time: t,
          timestamp: new Date().toLocaleTimeString(),
          type: 'BATTERY_ALERT',
          message: `Proceso '${proc.name}' (PID ${proc.pid}) llegó pero fue SUSPENDIDO por política de Ahorro de Batería.`,
          pid: proc.pid,
          severity: 'warning',
        });
      } else {
        proc.state = 'LISTO';
        state.readyQueue.push(proc);
        state.events.unshift({
          id: `evt-arr-${proc.pid}-${t}`,
          time: t,
          timestamp: new Date().toLocaleTimeString(),
          type: 'ARRIVAL',
          message: `Proceso '${proc.name}' (PID ${proc.pid}, Prioridad ${proc.priority}) llegó a la cola de listos.`,
          pid: proc.pid,
          severity: 'info',
        });
      }
    }
  });

  // Re-sort ready queue if algorithm demands sorting (Priority)
  sortReadyQueue(state.readyQueue, state.algorithm);

  // 2. Check Preemption in Priority Preemptive
  if (state.algorithm === 'PRIORITY_PREEMPTIVE' && state.runningProcess && state.readyQueue.length > 0) {
    const highestCandidate = state.readyQueue[0];
    if (highestCandidate.priority < state.runningProcess.priority) {
      // Preemption event!
      const preempted = state.runningProcess;
      preempted.state = 'LISTO';
      state.readyQueue.push(preempted);
      sortReadyQueue(state.readyQueue, state.algorithm);

      state.preemptedProcessId = preempted.pid;
      state.contextSwitchCount += 1;

      state.events.unshift({
        id: `evt-preempt-${preempted.pid}-${t}`,
        time: t,
        timestamp: new Date().toLocaleTimeString(),
        type: 'PREEMPTION',
        message: `⚡ DESALOJO PREEMPTIVO! Proceso crítico '${highestCandidate.name}' (Prio ${highestCandidate.priority}) desaloja a '${preempted.name}' (Prio ${preempted.priority}) en CPU.`,
        pid: preempted.pid,
        severity: 'critical',
      });

      // Update in master processes array
      const mIdx = state.processes.findIndex(p => p.pid === preempted.pid);
      if (mIdx !== -1) {
        state.processes[mIdx].state = 'LISTO';
        state.processes[mIdx].remainingTime = preempted.remainingTime;
      }

      state.runningProcess = null;
    }
  }

  // 3. Dispatch if CPU is idle
  if (!state.runningProcess && state.readyQueue.length > 0) {
    const nextProc = state.readyQueue.shift()!;
    nextProc.state = 'EJECUTANDO';
    if (nextProc.startTime === undefined) {
      nextProc.startTime = t;
      nextProc.responseTime = t - nextProc.arrivalTime;
    }
    state.runningProcess = nextProc;
    state.quantumRemaining = state.quantum;
    state.contextSwitchCount += 1;

    // Update master array
    const mIdx = state.processes.findIndex(p => p.pid === nextProc.pid);
    if (mIdx !== -1) {
      state.processes[mIdx].state = 'EJECUTANDO';
      if (state.processes[mIdx].startTime === undefined) {
        state.processes[mIdx].startTime = t;
        state.processes[mIdx].responseTime = t - nextProc.arrivalTime;
      }
    }

    state.events.unshift({
      id: `evt-disp-${nextProc.pid}-${t}`,
      time: t,
      timestamp: new Date().toLocaleTimeString(),
      type: 'DISPATCH',
      message: `CPU asignada a PID ${nextProc.pid} ('${nextProc.name}') | Ráfaga restante: ${nextProc.remainingTime}s.`,
      pid: nextProc.pid,
      severity: nextProc.critical ? 'critical' : 'success',
    });
  }

  // 4. Record execution tick in Gantt
  if (state.runningProcess) {
    const active = state.runningProcess;
    
    // Add or merge into Gantt slots
    const lastSlot = state.ganttSlots[state.ganttSlots.length - 1];
    if (lastSlot && lastSlot.processId === active.pid && lastSlot.end === t) {
      lastSlot.end = t + 1;
    } else {
      state.ganttSlots.push({
        id: `gantt-${active.pid}-${t}`,
        processId: active.pid,
        processName: active.name,
        start: t,
        end: t + 1,
        color: active.color,
        isCritical: active.critical,
        isIdle: false,
      });
    }

    // Execute 1 unit of CPU
    active.remainingTime -= 1;
    state.quantumRemaining -= 1;

    // Update in master processes array
    const mIdx = state.processes.findIndex(p => p.pid === active.pid);
    if (mIdx !== -1) {
      state.processes[mIdx].remainingTime = active.remainingTime;
    }

    // Check if process finished
    if (active.remainingTime <= 0) {
      active.state = 'TERMINADO';
      active.completionTime = t + 1;
      active.turnaroundTime = active.completionTime - active.arrivalTime;
      active.waitingTime = active.turnaroundTime - active.burstTime;

      if (mIdx !== -1) {
        state.processes[mIdx].state = 'TERMINADO';
        state.processes[mIdx].completionTime = t + 1;
        state.processes[mIdx].turnaroundTime = active.turnaroundTime;
        state.processes[mIdx].waitingTime = active.waitingTime;
      }

      state.events.unshift({
        id: `evt-done-${active.pid}-${t + 1}`,
        time: t + 1,
        timestamp: new Date().toLocaleTimeString(),
        type: 'COMPLETION',
        message: `Proceso '${active.name}' (PID ${active.pid}) completó ejecución exitosamente. [Retorno: ${active.turnaroundTime}s, Espera: ${active.waitingTime}s]`,
        pid: active.pid,
        severity: 'success',
      });

      state.runningProcess = null;
    } else if (state.algorithm === 'RR' && state.quantumRemaining <= 0) {
      // Quantum expired in Round Robin
      active.state = 'LISTO';
      state.readyQueue.push(active);

      if (mIdx !== -1) {
        state.processes[mIdx].state = 'LISTO';
        state.processes[mIdx].remainingTime = active.remainingTime;
      }

      state.events.unshift({
        id: `evt-qexp-${active.pid}-${t + 1}`,
        time: t + 1,
        timestamp: new Date().toLocaleTimeString(),
        type: 'QUANTUM_EXPIRED',
        message: `Quantum expiró para '${active.name}' (PID ${active.pid}). Reingresa al final de la cola circular. Restante: ${active.remainingTime}s.`,
        pid: active.pid,
        severity: 'info',
      });

      state.runningProcess = null;
    }
  } else {
    // CPU was Idle during this unit
    state.totalIdleTime += 1;
    const lastSlot = state.ganttSlots[state.ganttSlots.length - 1];
    if (lastSlot && lastSlot.isIdle && lastSlot.end === t) {
      lastSlot.end = t + 1;
    } else {
      state.ganttSlots.push({
        id: `gantt-idle-${t}`,
        processId: null,
        processName: 'CPU Inactiva (Idle)',
        start: t,
        end: t + 1,
        color: '#334155', // slate-700
        isCritical: false,
        isIdle: true,
      });
    }
  }

  // 5. Check if all processes are finished
  state.currentTime = t + 1;
  const unfinished = state.processes.filter(p => p.state !== 'TERMINADO' && p.state !== 'SUSPENDIDO');
  if (unfinished.length === 0 && !state.runningProcess && state.readyQueue.length === 0) {
    state.isFinished = true;
    state.events.unshift({
      id: `evt-fin-${state.currentTime}`,
      time: state.currentTime,
      timestamp: new Date().toLocaleTimeString(),
      type: 'STATE_CHANGE',
      message: `Planificación completada en tiempo t = ${state.currentTime}s. Todos los procesos activos finalizaron.`,
      severity: 'success',
    });
  }

  return state;
}

/**
 * Calculates real-time metrics
 */
export function calculateMetrics(state: SimulationState): SchedulerMetrics {
  const completed = state.processes.filter(p => p.state === 'TERMINADO');
  const count = completed.length;
  const total = state.processes.length;

  const totalWait = completed.reduce((acc, p) => acc + (p.waitingTime || 0), 0);
  const totalTAT = completed.reduce((acc, p) => acc + (p.turnaroundTime || 0), 0);
  const totalResp = completed.reduce((acc, p) => acc + (p.responseTime || 0), 0);

  const busyTime = state.currentTime - state.totalIdleTime;
  const cpuUtilization = state.currentTime > 0 ? (busyTime / state.currentTime) * 100 : 0;
  const throughput = state.currentTime > 0 ? count / state.currentTime : 0;

  return {
    currentTime: state.currentTime,
    cpuUtilization: Math.min(100, Math.max(0, parseFloat(cpuUtilization.toFixed(1)))),
    averageWaitingTime: count > 0 ? parseFloat((totalWait / count).toFixed(2)) : 0,
    averageTurnaroundTime: count > 0 ? parseFloat((totalTAT / count).toFixed(2)) : 0,
    averageResponseTime: count > 0 ? parseFloat((totalResp / count).toFixed(2)) : 0,
    completedCount: count,
    totalProcesses: total,
    throughput: parseFloat(throughput.toFixed(3)),
    contextSwitches: state.contextSwitchCount,
  };
}

/**
 * Run a full simulation statically until completion to compare algorithms side-by-side
 */
export function runStaticSimulation(
  initialProcs: Process[],
  algorithm: AlgorithmType,
  quantum: number = 2
): { state: SimulationState; metrics: SchedulerMetrics } {
  let simState = createInitialSimulationState(initialProcs, algorithm, quantum);
  let guard = 0;
  const maxTicks = 500;

  while (!simState.isFinished && guard < maxTicks) {
    simState = stepSimulationTick(simState, false);
    guard++;
  }

  const metrics = calculateMetrics(simState);
  return { state: simState, metrics };
}
