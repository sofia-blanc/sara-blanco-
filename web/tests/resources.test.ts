/**
 * Pruebas del contrato didáctico de recursos (V9).
 * Probar aquí evita que un futuro rediseño vuelva a mostrar números ficticios
 * desconectados de procesos, RAM, batería o planificación.
 */
import assert from 'node:assert/strict';
import { INITIAL_VEHICLE_PROCESSES } from '../src/utils/presets';
import { createInitialSimulationState, stepSimulationTick } from '../src/utils/schedulerEngine';
import { suspendCategories, insertWorkload } from '../src/simulation/engine';
import {
  admittedProcesses, estimatePowerW, buildOSResourceSnapshot,
  batteryAfterEnergyTick, advanceOperatingSystemTick, SIM_RAM_MB,
} from '../src/simulation/resources';
import type { VehicleDevice, BatteryState } from '../src/types/scheduler';

const battery: BatteryState = {
  level: 80, voltage: 388, temperature: 28, isLowBatteryMode: false,
  isCriticalBatteryMode: false, autoThrottlingEnabled: true, powerSavingWattsSaved: 0,
};
const devices: VehicleDevice[] = [{
  id: 'd1', code: 'DEV_GPS_01', name: 'GPS', subsystem: 'Navegación',
  status: 'operativo', health: 98, criticalLevel: 'esencial', bus: 'CAN-Bus Principal',
}];
const init = createInitialSimulationState(
  INITIAL_VEHICLE_PROCESSES.map(p => ({ ...p, waitingTime: 0, turnaroundTime: 0 })),
  'RR', 2,
);
const a = buildOSResourceSnapshot(init, battery, devices, 55, 'soleado');
assert.equal(a.ramRequestedMb, 128, 'Solo el PID 101 llega al tiempo cero');
assert.equal(a.processes.length, 1);
assert.equal(a.ramFreeMb + a.ramPhysicalMb, SIM_RAM_MB);

const stressed = insertWorkload(init, 'cpu');
const b = buildOSResourceSnapshot(stressed, battery, devices, 55, 'soleado');
assert.ok(b.ramRequestedMb > a.ramRequestedMb, 'El proceso de estrés reserva RAM');
assert.ok(b.cpuDemandPct > a.cpuDemandPct, 'El proceso de estrés aumenta demanda CPU');
assert.ok(b.osPowerW > a.osPowerW, 'El proceso de estrés aumenta potencia del SO');
assert.equal(b.processes.some(p => p.memoryMb === 896), true);

// Saturación RAM y SWAP: admitimos dos copias adicionales de carga pesada.
let pressure = insertWorkload(insertWorkload(stressed, 'cpu'), 'cpu');
const saturated = buildOSResourceSnapshot(pressure, battery, devices, 65, 'soleado');
assert.equal(saturated.ramPhysicalMb, SIM_RAM_MB);
assert.ok(saturated.swapRequestedMb > 0);
assert.equal(saturated.ramRequestedMb, saturated.ramPhysicalMb + saturated.swapRequestedMb);

// Multimedia inicia en t=5. Suspenderla debe liberar su memoria y potencia.
let withMedia = init;
for (let i = 0; i < 6; i++) withMedia = stepSimulationTick(withMedia, false);
const before = buildOSResourceSnapshot(withMedia, battery, devices, 55, 'soleado');
assert.ok(admittedProcesses(withMedia).some(p => p.category === 'multimedia'));
const suspended = suspendCategories(withMedia, ['multimedia']);
const after = buildOSResourceSnapshot(suspended, battery, devices, 55, 'soleado');
assert.ok(after.ramRequestedMb < before.ramRequestedMb, 'Suspender multimedia libera memoria estimada');
assert.ok(after.osPowerW < before.osPowerW, 'Suspender multimedia reduce potencia del SO');
assert.ok(after.suspendedCount > before.suspendedCount);

// Energía conserva unidades: W * 1/60 h = Wh. Menor velocidad => menor descarga.
const fast = estimatePowerW(withMedia, devices, 100, 'soleado', false);
const slow = estimatePowerW(withMedia, devices, 35, 'soleado', false);
assert.ok(fast.total > slow.total);
const next = batteryAfterEnergyTick(battery, fast.total / 60);
assert.ok(next.level < battery.level && next.level > 0);
assert.ok(batteryAfterEnergyTick(battery, 0).level === battery.level);

// Vehículo sigue consumiendo después de finalizar un lote de procesos.
const completed = { ...init, isFinished: true, currentTime: 8, totalIdleTime: 1 };
const idle = advanceOperatingSystemTick(completed, false);
assert.equal(idle.currentTime, 9);
assert.equal(idle.totalIdleTime, 2);
assert.equal(idle.isFinished, true);
console.log('OK: recursos V9 -> CPU, RAM/SWAP, procesos, energía, batería e inactividad.');
