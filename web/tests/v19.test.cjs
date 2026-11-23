/** Pruebas del motor determinista V19 (sin navegador ni internet). */
const assert=require('node:assert/strict');
const {newDrivingGame,steerDrivingGame,advanceDrivingGame,lanePosition,SPAWN_EVERY_FRAMES,hazardCaption}=require('../src/simulation/drivingGameV19.ts');
let g=newDrivingGame();
assert.equal(g.lane,1);
assert.equal(steerDrivingGame(g,-1).lane,0);
assert.equal(steerDrivingGame(steerDrivingGame(g,-1),-1).lane,0);
assert.equal(steerDrivingGame(steerDrivingGame(g,1),1).lane,2);
assert.equal(lanePosition(1,.8),720);
assert.ok(lanePosition(0,.8)<lanePosition(1,.8));
assert.ok(lanePosition(2,.8)>lanePosition(1,.8));
let events=[];
for(let i=0;i<28;i++){
  const step=advanceDrivingGame(g);g=step.state;events.push(...step.incidents);
}
assert.equal(g.nextId,1,'Solo el primer obstáculo aparece antes del segundo spawn');
assert.equal(events.length,1);
assert.equal(events[0].kind,'obstacle');
assert.equal(events[0].collision,true,'Si no se cambia de carril, el obstáculo golpea');
assert.equal(g.collisions,1);
assert.equal(g.hazards.length,0,'Un obstáculo resuelto no se procesa dos veces');
let avoid=newDrivingGame();
for(let i=0;i<28;i++){
  if(i===10) avoid=steerDrivingGame(avoid,1);
  avoid=advanceDrivingGame(avoid).state;
}
assert.equal(avoid.collisions,0,'El jugador puede esquivar el obstáculo');
assert.equal(avoid.avoided,1);
const fastStart=newDrivingGame();
let slow=fastStart, fast=fastStart;
for(let i=0;i<12;i++){
  slow=advanceDrivingGame(slow,20).state;
  fast=advanceDrivingGame(fast,110).state;
}
assert.ok(slow.hazards.length>0 && fast.hazards.length>0);
assert.ok(fast.hazards[0].progress>slow.hazards[0].progress,'La velocidad cambia la aproximación de peligros');
assert.equal(SPAWN_EVERY_FRAMES,26);
assert.match(hazardCaption('camera'),/sensor/);
console.log('OK V19: carriles, límites, perspectiva, aparición, esquiva, colisión y eventos únicos.');
