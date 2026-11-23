# AutoOS V21: verifica TypeScript, pruebas, bundle Streamlit y ausencia de archivos de secretos.
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Push-Location $root
try {
  Write-Host 'AUTOOS V21 - validar cruces y ahorro persistente' -ForegroundColor Cyan
  Push-Location '.\web'
  try {
    npm ci
    if ($LASTEXITCODE -ne 0) {throw 'Falló npm ci'}
    npm run lint
    if ($LASTEXITCODE -ne 0) {throw 'Falló TypeScript'}
    $oldNodeOptions=$env:NODE_OPTIONS
    try {
      $env:NODE_OPTIONS='--experimental-strip-types'
      npm run test:sim
      if ($LASTEXITCODE -ne 0) {throw 'Fallaron pruebas'}
    } finally {$env:NODE_OPTIONS=$oldNodeOptions}
    npm run build
    if ($LASTEXITCODE -ne 0) {throw 'Falló compilación Vite'}
  } finally {Pop-Location}
  python .\tools\build_streamlit_bundle.py
  if ($LASTEXITCODE -ne 0) {throw 'Falló creación del bundle Streamlit'}
  foreach ($file in @('.\Auto\autoos_unified.html','.\Auto\bridge_component\index.html')) {
    if (-not (Test-Path $file)) {throw "Falta bundle: $file"}
    $html=[IO.File]::ReadAllText((Resolve-Path $file).Path)
    if (-not $html.Contains('v21-saving-status')) {throw "Bundle sin cambios V21: $file"}
  }
  Write-Host 'OK: TypeScript, pruebas, compilación y bundles V21 correctos.' -ForegroundColor Green
  Write-Host 'PENDIENTE: probar conducción de 20 min, colisiones y Supabase en navegador.' -ForegroundColor Yellow
} finally {Pop-Location}
