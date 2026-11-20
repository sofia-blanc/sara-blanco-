/**
 * AutoOS / Motor de recursos del laboratorio React.
 *
 * FUENTE DE VERDAD: SimulationState, BatteryState y VehicleDevice[] que posee App.tsx.
 * Este modelo NO lee RAM ni consumo físicos de Windows y NO representa la instancia
 * Python Kernel de Streamlit. El propósito es medir de forma reproducible los
 * efectos de las decisiones del scheduler sobre un vehículo virtual.
 *
 * MODELO DIDÁCTICO DE MEMORIA:
 * - Cada proceso admitido reserva memoryMb en su conjunto de trabajo.
 * - NUEVO no está admitido; TERMINADO libera su reserva;
 *   SUSPENDIDO libera RAM en este modelo (equivalente simplificado a swap-out).
 * - El exceso sobre 2048 MB se representa como demanda de SWAP estimada;
 *   no debe confundirse con páginas realmente asignadas por el kernel Python.
 *
 * MODELO ENERGÉTICO:
 * - Cada tick de conducción equivale a 1 minuto virtual acelerado.
 * - Potencia = tracción(velocidad) + dispositivos + procesos admitidos + auxiliares.
 * - Energía/tick (Wh) = potencia(W) / 60; descarga(%): Wh / 32000 * 100.
 * - Coeficientes son supuestos para demostración, NO homologación automotriz.
 */
import type { BatteryState, VehicleDevice, Process } from '../types/scheduler';
import type { SimulationState } from '../utils/schedulerEngine';
import { calculateMetrics, stepSimulationTick } from '../utils/schedulerEngine';
import type { Weather } from './scenarios';

export const SIM_RAM_MB = 2048;
export const SIM_BATTERY_WH = 32_000;
export const SIM_MINUTES_PER_TICK = 1;

export interface OSResourceSnapshot {
  tick: number;
  cpuDemandPct: number;
  cpuBusyPct: number;
  cpuExecutingPid: number | null;
  ramRequestedMb: number;
  ramPhysicalMb: number;
  ramFreeMb: number;
  swapRequestedMb: number;
  memoryPressurePct: number;
  batteryPct: number;
  batteryWhRemaining: number;
  consumedWh: number;
  totalPowerW: number;
  tractionPowerW: number;
  osPowerW: number;
  devicePowerW: number;
  otherPowerW: number;
  drainPctPerTick: number;
  readyCount: number;
  suspendedCount: number;
  completedCount: number;
  admittedCount: number;
  faultsCount: number;
  contextSwitches: number;
  processes: Array<{
    pid: number; name: string; state: string; memoryMb: number;
    cpuDemandPct: number; powerW: number; priority: number;
  }>;
}

export interface OSResourceSample {
  tick: number;
  cpuDemandPct: number;
  ramPhysicalMb: number;
  swapRequestedMb: number;
  batteryPct: number;
  totalPowerW: number;
}

export function admittedProcesses(state: SimulationState): Process[] {
  return state.processes.filter(p => p.state !== 'NUEVO' && p.state !== 'TERMINADO' && p.state !== 'SUSPENDIDO');
}

export function estimatePowerW(
  state: SimulationState, devices: VehicleDevice[], speedKmh: number, weather: Weather,
  saving: boolean,
): { total: number; traction: number; os: number; devices: number; other: number } {
  const speed = Math.min(120, Math.max(0, speedKmh));
  const factor = weather === 'lluvia' ? 1.18 : weather === 'niebla' ? 1.1 : 1;
  // Arrastre y rodadura: fórmula simplificada y fácil de explicar.
  const traction = speed === 0 ? 0 : Math.round((550 + 1.25 * speed * speed) * factor);
  const os = admittedProcesses(state).reduce((watts, proc) => watts + Math.max(0, proc.powerConsumptionWatts), 0);
  const deviceWatts = devices.reduce((watts, device) => watts + (device.status === 'desconectado' ? 0 : device.criticalLevel === 'critico' ? 18 : 9), 0);
  const other = saving ? 120 : 240; // ventilación y servicios auxiliares del vehículo
  return { total: traction + os + deviceWatts + other, traction, os, devices: deviceWatts, other };
}

export function buildOSResourceSnapshot(
  state: SimulationState,
  battery: BatteryState,
  devices: VehicleDevice[],
  speedKmh: number,
  weather: Weather,
  consumedWh = 0,
): OSResourceSnapshot {
  const admitted = admittedProcesses(state);
  const ramRequestedMb = admitted.reduce((total, p) => total + Math.max(0, p.memoryMb), 0);
  const ramPhysicalMb = Math.min(SIM_RAM_MB, ramRequestedMb);
  const power = estimatePowerW(state, devices, speedKmh, weather, battery.isLowBatteryMode);
  const metrics = calculateMetrics(state);
  return {
    tick: state.currentTime,
    cpuDemandPct: admitted.reduce((value, proc) => value + Math.max(0, proc.cpuUsagePct), 0),
    cpuBusyPct: metrics.cpuUtilization,
    cpuExecutingPid: state.runningProcess?.pid ?? null,
    ramRequestedMb,
    ramPhysicalMb,
    ramFreeMb: Math.max(0, SIM_RAM_MB - ramPhysicalMb),
    swapRequestedMb: Math.max(0, ramRequestedMb - SIM_RAM_MB),
    memoryPressurePct: Math.round((ramPhysicalMb / SIM_RAM_MB) * 100),
    batteryPct: battery.level,
    batteryWhRemaining: SIM_BATTERY_WH * battery.level / 100,
    consumedWh,
    totalPowerW: power.total,
    tractionPowerW: power.traction,
    osPowerW: power.os,
    devicePowerW: power.devices,
    otherPowerW: power.other,
    drainPctPerTick: power.total / 60 * SIM_MINUTES_PER_TICK / SIM_BATTERY_WH * 100,
    readyCount: state.readyQueue.length,
    suspendedCount: state.processes.filter((p) => p.state === 'SUSPENDIDO').length,
    completedCount: state.processes.filter((p) => p.state === 'TERMINADO').length,
    admittedCount: admitted.length,
    faultsCount: devices.filter((d) => d.status !== 'operativo').length,
    contextSwitches: state.contextSwitchCount,
    processes: admitted.map(p => ({ pid: p.pid, name: p.name, state: p.state, memoryMb: p.memoryMb,
      cpuDemandPct: p.cpuUsagePct, powerW: p.powerConsumptionWatts, priority: p.priority })),
  };
}

/** Aplicado una vez por tick de conducción; preserva el modo de ahorro elegido. */
export function batteryAfterEnergyTick(battery: BatteryState, energyWh: number): BatteryState {
  const level = Math.max(0, battery.level - Math.max(0, energyWh) / SIM_BATTERY_WH * 100);
  return {
    ...battery,
    level,
    voltage: Math.round(340 + level * .6),
    isCriticalBatteryMode: level <= 10,
    isLowBatteryMode: battery.isLowBatteryMode || level <= 10,
    temperature: Math.min(65, battery.temperature + (energyWh > 150 ? 0.03 : 0)),
  };
}

export function toResourceSample(snapshot: OSResourceSnapshot): OSResourceSample {
  return {
    tick: snapshot.tick, cpuDemandPct: snapshot.cpuDemandPct,
    ramPhysicalMb: snapshot.ramPhysicalMb, swapRequestedMb: snapshot.swapRequestedMb,
    batteryPct: snapshot.batteryPct, totalPowerW: snapshot.totalPowerW,
  };
}

/**
 * Permite seguir midiendo consumos después de terminar las tareas finitas.
 * Cuando todas terminaron, la CPU queda ociosa pero el vehículo aún puede
 * circular: el reloj y la batería deben continuar avanzando juntos.
 */
export function advanceOperatingSystemTick(state: SimulationState, batterySaving: boolean): SimulationState {
  if (!state.isFinished) return stepSimulationTick(state, batterySaving);
  const slots = state.ganttSlots.map((slot) => ({ ...slot }));
  const last = slots[slots.length - 1];
  if (last?.isIdle && last.end === state.currentTime) last.end += 1;
  else slots.push({
    id: `gantt-vehicle-idle-${state.currentTime}`,
    processId: null,
    processName: 'CPU ociosa (vehículo sigue en ruta)',
    start: state.currentTime,
    end: state.currentTime + 1,
    color: '#334155',
    isCritical: false,
    isIdle: true,
  });
  return {
    ...state,
    currentTime: state.currentTime + 1,
    totalIdleTime: state.totalIdleTime + 1,
    ganttSlots: slots,
  };
}
