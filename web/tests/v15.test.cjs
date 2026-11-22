/** AUTOOS V15 — pruebas de la matriz de permisos y decisiones, en Node. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const ts=require('typescript');
const Module=require('node:module');
function loadTs(file){
  const full=path.resolve(__dirname,'../src/simulation',file);
  const code=ts.transpileModule(fs.readFileSync(full,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
  const mod=new Module(full,module);mod.filename=full;mod.paths=module.paths;mod._compile(code,full);return mod.exports;
}
const p=loadTs('accessPolicyV15.ts');
const decisions=loadTs('missionDecisionsV15.ts');
assert.deepEqual(p.visibleModules('pasajero'),['HOME','COCKPIT']);
assert.equal(p.canOpenModule('admin','CLOUD'),true);
assert.equal(p.canOpenModule('mecanico','CLOUD'),false);
assert.equal(p.canOpenModule('conductor','GPS'),true);
assert.equal(p.canOpenModule('conductor','SIMULATOR'),false);
assert.equal(p.canOpenModule('pasajero','BLACKBOX'),false);
assert.equal(p.canExecute('conductor','mission.slow'),true);
assert.equal(p.canExecute('conductor','sensor.inject'),false);
assert.equal(p.canExecute('mecanico','sensor.inject'),true);
assert.equal(p.canExecute('mecanico','cloud.diagnose'),false);
assert.equal(p.canExecute('admin','cloud.diagnose'),true);
assert.equal(p.canExecute('pasajero','mission.start'),false);
assert.equal(p.canExecute('mecanico','audit.read'),true);
assert.equal(p.canExecute('??','sensor.inject'),false);
const ids=new Set(decisions.MISSION_OPTIONS.map(x=>x.id));
assert.equal(ids.size,decisions.MISSION_OPTIONS.length);
for(const v of decisions.MISSION_OPTIONS){
 assert.equal(p.canExecute('admin',v.permission),true,`Administrador no admite ${v.id}`);
 assert.ok(v.label.length>5&&v.detail.length>10);
}
console.log('OK V15: perfiles, denegacion por defecto, privilegios y decisiones de navegacion.');
