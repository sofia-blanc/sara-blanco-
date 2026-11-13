import type { BatteryState, Process, VehicleDevice } from '../types/scheduler';
import { INITIAL_VEHICLE_PROCESSES } from '../utils/presets';
import { createInitialSimulationState, type SimulationState } from '../utils/schedulerEngine';
import { scenarioById, type ScenarioId, type SimulationAction, type Weather } from './scenarios';

/** Mutaciones puras para que el panel y el planificador compartan el mismo estado. */
export function simEvent(state: SimulationState, message: string, severity: 'info' | 'warning' | 'critical' | 'success' = 'info'): SimulationState {
  return {
    ...state,
    events: [{
      id: `evt-sim-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      time: state.currentTime,
      timestamp: new Date().toLocaleTimeString('es-CO'),
      type: 'STATE_CHANGE' as const, message, severity,
    }, ...state.events].slice(0, 350),
  };
}

export function makeBattery(level: number, saving = false): BatteryState {
  const normalized = Math.min(100, Math.max(0, level));
  return {
    level: normalized,
    voltage: Math.round(340 + normalized / 100 * 60),
    temperature: normalized <= 10 ? 48 : 29,
    isLowBatteryMode: saving,
    isCriticalBatteryMode: normalized <= 10,
    autoThrottlingEnabled: true,
    powerSavingWattsSaved: saving ? 90 : 0,
  };
}

export function markFault(devices: VehicleDevice[], code: string, weatherFault = false): VehicleDevice[] {
  return devices.map((device) => device.code !== code ? device : {
    ...device,
    status: weatherFault ? 'degradado' as const : 'falla' as const,
    health: weatherFault ? 65 : 12,
    activeDtc: weatherFault ? 'WX-VISIBILITY' : 'SIM-FAULT-01',
    failureMode: weatherFault ? 'Visibilidad reducida en simulación' : 'Falla inyectada por laboratorio AutoOS',
  });
}

export function recoverFault(devices: VehicleDevice[], code: string): VehicleDevice[] {
  return devices.map((device) => device.code !== code ? device : {
    ...device, status: 'operativo' as const, health: 98, activeDtc: null, failureMode: null,
  });
}

/** Crea una tarea real dentro de la cola del scheduler, no solo un indicador visual. */
export function insertWorkload(state: SimulationState, kind: 'cpu' | 'diagnostic' | 'offline' | 'backup'): SimulationState {
  const nextPid = Math.max(1000, ...state.processes.map((p) => p.pid)) + 1;
  const cfg = {
    cpu: { name: 'Simulación: proceso de fondo intensivo', category: 'multimedia' as const, priority: 4 as const, cpu: 78, memory: 896, burst: 26, watts: 65 },
    diagnostic: { name: 'AutoOS: diagnóstico de dispositivo', category: 'control' as const, priority: 1 as const, cpu: 30, memory: 96, burst: 8, watts: 15 },
    offline: { name: 'AutoOS: navegación local / caché', category: 'control' as const, priority: 2 as const, cpu: 16, memory: 192, burst: 12, watts: 10 },
    backup: { name: 'AutoOS: fusión de sensores redundantes', category: 'sensor' as const, priority: 1 as const, cpu: 32, memory: 224, burst: 12, watts: 27 },
  }[kind];
  const proc: Process = {
    pid: nextPid, name: cfg.name, category: cfg.category, arrivalTime: state.currentTime,
    burstTime: cfg.burst, remainingTime: cfg.burst, priority: cfg.priority,
    critical: cfg.priority === 1, color: kind === 'cpu' ? '#f59e0b' : '#06b6d4',
    state: 'LISTO', powerConsumptionWatts: cfg.watts, cpuUsagePct: cfg.cpu, memoryMb: cfg.memory,
    waitingTime: 0, turnaroundTime: 0,
  };
  const readyQueue = [...state.readyQueue, proc];
  if (state.algorithm === 'PRIORITY_PREEMPTIVE' || state.algorithm === 'PRIORITY') readyQueue.sort((a, b) => a.priority - b.priority);
  return simEvent({
    ...state,
    processes: [...state.processes, proc], readyQueue,
    isFinished: false,
  }, `PID ${nextPid} creado: ${proc.name}. Demanda de CPU ${cfg.cpu} % y memoria ${cfg.memory} MB.`, kind === 'cpu' ? 'warning' : 'info');
}

/** Conserva la consistencia entre procesos maestros, cola listos y proceso ejecutándose. */
export function suspendCategories(state: SimulationState, categories: Process['category'][]): SimulationState {
  const active = state.processes.map((p) =>
    categories.includes(p.category) && p.state !== 'TERMINADO' && p.state !== 'SUSPENDIDO'
      ? { ...p, state: 'SUSPENDIDO' as const, suspendedDueToBattery: true }
      : p
  );
  const blocked = new Set(active.filter((p) => p.state === 'SUSPENDIDO').map((p) => p.pid));
  const removed = active.filter((p) => blocked.has(p.pid)).length;
  const queue = state.readyQueue.filter((p) => !blocked.has(p.pid));
  const running = state.runningProcess && !blocked.has(state.runningProcess.pid) ? state.runningProcess : null;
  return simEvent({
    ...state, processes: active, readyQueue: queue, runningProcess: running,
    quantumRemaining: running ? state.quantumRemaining : state.quantum,
    isFinished: false,
  }, `Política del SO aplicada: ${removed} procesos no esenciales quedan suspendidos y fuera de la cola.`, 'warning');
}

export function prioritizeCritical(state: SimulationState): SimulationState {
  const procs = state.processes.map((p) => ({
    ...p,
    priority: (p.category === 'seguridad' ? 1 : p.priority) as Process['priority'],
  }));
  const byPid = new Map(procs.map((p) => [p.pid, p]));
  const ready = state.readyQueue.map((p) => byPid.get(p.pid) || p).sort((a, b) => a.priority - b.priority || a.arrivalTime - b.arrivalTime);
  return simEvent({ ...state, algorithm: 'PRIORITY_PREEMPTIVE', processes: procs, readyQueue: ready,
    runningProcess: state.runningProcess ? (byPid.get(state.runningProcess.pid) || state.runningProcess) : null,
  }, 'Scheduler cambiado a PRIORITY_PREEMPTIVE. Prioridad 1 garantizada a tareas de seguridad.');
}

export function initialScenarioState(id: ScenarioId, originalDevices: VehicleDevice[]): { state: SimulationState; devices: VehicleDevice[]; battery: BatteryState } {
  const scenario = scenarioById(id);
  const originals: Process[] = INITIAL_VEHICLE_PROCESSES.map((p) => ({ ...p, waitingTime: 0, turnaroundTime: 0 }));
  let state = createInitialSimulationState(originals, 'PRIORITY_PREEMPTIVE', 2);
  let devices: VehicleDevice[] = originalDevices.map((d) => ({ ...d, activeDtc: null, failureMode: null, status: 'operativo' as const }));
  if (scenario.faultDevice) {
    devices = markFault(devices, scenario.faultDevice);
    state = insertWorkload(state, 'diagnostic');
  }
  if (scenario.stressCpu) state = insertWorkload(state, 'cpu');
  if (scenario.weather !== 'soleado') devices = markFault(devices, 'DEV_LIDAR_01', true);
  state = simEvent(state, `ESCENARIO ${scenario.title.toUpperCase()}: ${scenario.cause}`, scenario.risk === 'Alto' ? 'critical' : 'info');
  return { state, devices, battery: makeBattery(scenario.battery, false) };
}

export function applyScenarioAction(state: SimulationState, action: SimulationAction): SimulationState {
  switch (action) {
    case 'power_save': return simEvent(suspendCategories(state, ['multimedia', 'confort']), 'Ahorro extremo activado: CPU y memoria no críticas liberadas.', 'success');
    case 'suspend_media': return suspendCategories(state, ['multimedia']);
    case 'limit_comfort': return suspendCategories(state, ['confort']);
    case 'prioritize': return prioritizeCritical(state);
    case 'sensor_backup': return insertWorkload(prioritizeCritical(state), 'backup');
    case 'offline_navigation':
    case 'local_mode': return insertWorkload(state, 'offline');
    case 'reduce_speed': return simEvent(state, 'Conductor virtual redujo velocidad a un máximo de 35 km/h. Se modifica el consumo energético por ciclo.', 'success');
    case 'ignore': return simEvent(state, 'El usuario decidió no intervenir. La anomalía y su riesgo permanecen activos.', 'warning');
    case 'isolate_camera': return simEvent(state, 'Cámara frontal aislada para evitar lecturas inválidas.', 'warning');
    case 'restart_gps': return simEvent(state, 'Receptor GPS reiniciado; diagnóstico virtual indica dispositivo restablecido.', 'success');
    case 'restart_network': return simEvent(state, 'Módem V2X reiniciado y enlace virtual restablecido.', 'success');
  }
}

export function applyWeather(devices: VehicleDevice[], weather: Weather): VehicleDevice[] {
  if (weather === 'soleado') return devices.map((d) => d.activeDtc === 'WX-VISIBILITY'
    ? { ...d, status: 'operativo' as const, health: 98, activeDtc: null, failureMode: null } : d);
  return devices.some((d) => d.code === 'DEV_LIDAR_01' && d.status === 'falla')
    ? devices : markFault(devices, 'DEV_LIDAR_01', true);
}
