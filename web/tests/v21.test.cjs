/** V21: cruces espaciados y decisiones que respetan protecciones previas. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {
  JUNCTION_MINUTES_V21, nextJunctionMinute, isRouteJunctionDue,
  minutesToDrivingForkV21, forkVisibleWhileDrivingV21, preserveEnergySavingOnIgnore,
} = require('../src/simulation/routeDrivingV21.ts');
assert.deepEqual([...JUNCTION_MINUTES_V21], [8,16]);
assert.equal(nextJunctionMinute(0),8);
assert.equal(nextJunctionMinute(1),16);
assert.equal(nextJunctionMinute(2),null,'No existe un tercer cruce');
assert.equal(nextJunctionMinute(-1),null);
assert.equal(isRouteJunctionDue(5,0),false,'No hay cruce en el minuto 5');
assert.equal(isRouteJunctionDue(8,0),true);
assert.equal(isRouteJunctionDue(8,1),false);
assert.equal(isRouteJunctionDue(16,1),true);
assert.equal(isRouteJunctionDue(20,2),false,'El minuto final no fuerza otro cruce');
assert.equal(minutesToDrivingForkV21(6,0),2);
assert.equal(minutesToDrivingForkV21(14,1),2);
assert.equal(minutesToDrivingForkV21(17,2),null);
assert.equal(forkVisibleWhileDrivingV21(5,0,true),false);
assert.equal(forkVisibleWhileDrivingV21(6,0,true),true);
assert.equal(forkVisibleWhileDrivingV21(8,0,false),false);
assert.equal(forkVisibleWhileDrivingV21(19,2,true),false);
// Persistencia de una política: no debe apagar una protección vigente.
assert.equal(preserveEnergySavingOnIgnore('battery','ignore',true,true,6),true);
assert.equal(preserveEnergySavingOnIgnore('battery','ignore',true,true,0),false);
assert.equal(preserveEnergySavingOnIgnore('battery','ignore',true,false,6),false);
assert.equal(preserveEnergySavingOnIgnore('battery','ignore',false,true,6),false,
  'Un ahorro automático por batería baja no es prueba de elección previa');
assert.equal(preserveEnergySavingOnIgnore('gps','ignore',true,true,6),false,
  'No se silencian otros escenarios de seguridad');
assert.equal(preserveEnergySavingOnIgnore('battery','reduce_speed',true,true,6),false);
const center=fs.readFileSync(path.join(__dirname,'../src/components/SimulationCenter.tsx'),'utf8');
const stage=fs.readFileSync(path.join(__dirname,'../src/components/MissionStageV17.tsx'),'utf8');
assert.match(center,/AUTOOS_V21_POLITICAS_PERSISTENTES/);
assert.match(center,/setRouteChoices\(0\)/,'La nueva misión reinicia los cruces');
assert.match(center,/setPowerSaveActive\(false\)/,'La nueva misión reinicia el ahorro elegido');
assert.match(center,/isRouteJunctionDue\(elapsed, routeChoices\)/);
assert.match(center,/preserveEnergySavingOnIgnore\(activeId, id, powerSaveActive,/);
assert.match(center,/setRouteChoices\(\(count\) => count \+ 1\)/);
assert.match(center,/routeChoices >= 2/);
assert.match(stage,/AUTOOS_V21_CRUCES_LIMITADOS/);
assert.match(stage,/junctionIndex: number/);
assert.match(stage,/powerSaveActive: boolean/);
assert.match(stage,/v21-saving-status/);
assert.doesNotMatch(stage,/onClick=\{\(\)=>p\.onSelect\(/);
console.log('OK V21: solo cruces en 8 y 16; ahorro extremo persiste; continuar sin cambios no penaliza ahorro ya activo.');
