// Ejecutor mínimo de pruebas TS usando la dependencia de desarrollo TypeScript.
const fs = require('node:fs');
const Module = require('node:module');

/**
 * Aislamiento exclusivo de pruebas.
 *
 * report.ts importa el cliente Supabase para guardar informes en produccion.
 * En este runner (Node.js, sin navegador ni Vite) solo probamos reportAsText:
 * no se necesita una conexion real ni las variables import.meta.env.
 *
 * Interceptamos SOLAMENTE ese import del modulo de reportes, sin modificar
 * supabaseClient.ts ni la logica productiva de AutoOS.
 * Las pruebas de integracion Supabase deben ejecutarse por separado.
 */
const originalLoad = Module._load;
Module._load = function loadWithTestIsolation(request, parent, isMain) {
  const isReportModule = /[\\/]simulation[\\/]report\.ts$/.test(parent?.filename ?? '');
  if (isReportModule && request === '../supabaseClient') {
    return { saveSimulationReportToSupabase: async () => false };
  }
  return originalLoad.call(this, request, parent, isMain);
};
const ts = require('typescript');
require.extensions['.ts'] = function (mod, filename) {
  const js = ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true },
  }).outputText;
  mod._compile(js, filename);
};
require('./scenarios.test.ts');

require('./resources.test.ts');

require('./navigation.test.ts');
require('./v15.test.cjs'); // AUTOOS_V15_APLICADO

require('./v16.test.cjs'); // AUTOOS V16, escenarios y permisos

require('./v17.test.cjs'); // AUTOOS V17, rutas y checkpoints

require('./v19.test.cjs'); // AUTOOS V19 minijuego interactivo
require('./v20.test.cjs'); // AUTOOS V20 rutas sin clic
require('./v21.test.cjs'); // AUTOOS V21 estado y cruces
