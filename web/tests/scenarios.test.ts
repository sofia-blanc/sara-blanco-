import assert from 'node:assert/strict';
import type { VehicleDevice } from '../src/types/scheduler';
import { initialScenarioState, applyScenarioAction, insertWorkload, applyWeather, suspendCategories } from '../src/simulation/engine';
import { SCENARIOS } from '../src/simulation/scenarios';
import { createInitialSimulationState, stepSimulationTick } from '../src/utils/schedulerEngine';
import { reportAsText, type AutoOSReport } from '../src/simulation/report';
import { INITIAL_VEHICLE_PROCESSES } from '../src/utils/presets';

const devices: VehicleDevice[] = [
  { id: '1', code: 'DEV_GPS_01', name: 'GPS', subsystem: 'Navegación', status: 'operativo', health: 100, criticalLevel: 'esencial', bus: 'CAN-Bus Principal' },
  { id: '2', code: 'DEV_CAM_FRONT', name: 'Cámara', subsystem: 'Visión', status: 'operativo', health: 100, criticalLevel: 'critico', bus: 'Automotive Ethernet' },
  { id: '3', code: 'DEV_LIDAR_01', name: 'LIDAR', subsystem: 'Sensores', status: 'operativo', health: 100, criticalLevel: 'critico', bus: 'Automotive Ethernet' },
  { id: '4', code: 'DEV_COM_V2X', name: 'V2X', subsystem: 'Comunicación', status: 'operativo', health: 100, criticalLevel: 'esencial', bus: 'Automotive Ethernet' },
];

assert.equal(SCENARIOS.length, 8);
for (const scenario of SCENARIOS) {
 const fresh = initialScenarioState(scenario.id, devices);
 assert.ok(fresh.state.processes.length >= INITIAL_VEHICLE_PROCESSES.length, scenario.id);
 assert.equal(fresh.state.algorithm,'PRIORITY_PREEMPTIVE');
 assert.equal(fresh.battery.level, scenario.battery);
 assert.ok(fresh.state.events[0].message.includes(scenario.title.toUpperCase()));
}
let gps = initialScenarioState('gps', devices);
assert.equal(gps.devices.find((d)=>d.code==='DEV_GPS_01')!.status, 'falla');
assert.ok(gps.state.processes.find((p) => p.name.includes('diagnóstico')));
const cpu = initialScenarioState('cpu',devices);
assert.ok(cpu.state.processes.some((p) => p.cpuUsagePct === 78));
const beforeMedia = cpu.state.readyQueue.length;
const suspended = applyScenarioAction(cpu.state, 'suspend_media');
assert.ok(suspended.processes.some((p) => p.category==='multimedia' && p.state==='SUSPENDIDO'));
assert.ok(suspended.readyQueue.length < beforeMedia);
assert.ok(!suspended.readyQueue.some((p) => p.category==='multimedia'));
const prioritized = applyScenarioAction(cpu.state, 'prioritize');
assert.equal(prioritized.algorithm, 'PRIORITY_PREEMPTIVE');
assert.ok(prioritized.readyQueue.every((p,i,a) => i===0 || a[i-1].priority<=p.priority));
const offline = applyScenarioAction(gps.state, 'offline_navigation');
assert.ok(offline.processes.some((p) => p.name.includes('navegación local')));
const afterFaultWeather = applyWeather(devices, 'niebla');
assert.equal(afterFaultWeather.find((d) => d.code==='DEV_LIDAR_01')!.status,'degradado');
assert.equal(applyWeather(afterFaultWeather, 'soleado').find((d) => d.code==='DEV_LIDAR_01')!.status, 'operativo');
const init = createInitialSimulationState(INITIAL_VEHICLE_PROCESSES.map((p) => ({...p,waitingTime:0,turnaroundTime:0})), 'PRIORITY_PREEMPTIVE',2);
let after = insertWorkload(init,'cpu');
assert.ok(after.readyQueue.some((p) => p.cpuUsagePct===78));
after=stepSimulationTick(after,false);
assert.ok(after.currentTime>0);
const report: AutoOSReport = {
 id: 'test-1', scenario: 'cpu', title: 'Sobrecarga de CPU', startedAt: new Date().toISOString(), completedAt: new Date().toISOString(),
 diagnosis: 'Carga excesiva', initial: { battery: 80, speed: 60, weather: 'soleado', cpuLoad: 100, usedMemory: 1200, running: 3, suspended: 0, failures: [], scheduler: 'RR', tick: 0 },
 final: { battery: 79, speed: 35, weather: 'soleado', cpuLoad: 22, usedMemory: 128, running: 1, suspended: 2, failures: [], scheduler: 'PRIORITY_PREEMPTIVE', tick: 5 },
 actions: [{time: '10:00', choice: 'Suspender multimedia', effect: 'Multimedia suspendida'}], recommendations: ['Revisar procesos'], status: 'ESTABLE',
};
const reportText = reportAsText(report);
assert.ok(reportText.includes('Sobrecarga de CPU') && reportText.includes('Suspender multimedia') && reportText.includes('22 %'));
for (const scenario of SCENARIOS) {
 let current = initialScenarioState(scenario.id, devices).state;
 for (let i = 0; i < 10 && !current.isFinished; i++) current = stepSimulationTick(current, false);
 assert.ok(current.currentTime > 0, scenario.id);
}
console.log('OK: informes, 8 escenarios, fallos, prioridad, suspensión, carga, navegación, clima y tick del planificador.');
