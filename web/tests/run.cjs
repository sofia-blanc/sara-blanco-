// Ejecutor mínimo de pruebas TS usando la dependencia de desarrollo TypeScript.
const fs = require('node:fs');
const ts = require('typescript');
require.extensions['.ts'] = function (mod, filename) {
  const js = ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true },
  }).outputText;
  mod._compile(js, filename);
};
require('./scenarios.test.ts');
