/* AUTOOS V16: reglas de juego y permisos, sin depender del DOM. */
const assert=require('node:assert/strict');
const {decisionCheckpoint,canRunMission,maySimulate}=require('../src/simulation/missionGameV16.ts');
assert.equal(decisionCheckpoint(0,0),false);
assert.equal(decisionCheckpoint(4,0),false);
assert.equal(decisionCheckpoint(5,0),true);
assert.equal(decisionCheckpoint(5,1),false);
assert.equal(decisionCheckpoint(10,1),true);
assert.equal(decisionCheckpoint(43,8),false);
assert.equal(canRunMission(true,false,85),true);
assert.equal(canRunMission(true,false,0),false);
assert.equal(canRunMission(false,false,45),false);
assert.equal(canRunMission(true,true,45),false);
assert.equal(maySimulate('mecanico'),true);
assert.equal(maySimulate('admin'),true);
assert.equal(maySimulate('pasajero'),false);
assert.equal(maySimulate('conductor'),false);
// Integración de reglas de decisión con el motor del planificador, no solo la UI.
const { initialScenarioState, applyScenarioAction } = require('../src/simulation/engine.ts');
const devices=[{ id:'gps', code:'DEV_GPS_01',name:'GPS',subsystem:'Navegación',status:'operativo',health:100,criticalLevel:'esencial',bus:'CAN' }];
const session=initialScenarioState('battery', devices);
const saved=applyScenarioAction(session.state,'power_save');
assert.ok(saved.events[0].message.includes('Ahorro extremo'));
assert.ok(saved.processes.some(p=>p.state==='SUSPENDIDO'));
const gps=initialScenarioState('gps',devices);
assert.equal(gps.devices[0].status,'falla');
const recovered=applyScenarioAction(gps.state,'restart_gps');
assert.ok(recovered.events[0].message.includes('GPS reiniciado'));
console.log('OK V16: checkpoints, batería, permisos, proceso suspendido y decisiones registradas.');
