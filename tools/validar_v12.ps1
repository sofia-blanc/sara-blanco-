# AUTOOS V12 - comprobacion funcional sin caracteres dependientes de codificacion.
# Reutiliza los 7 pasos de V11 y suma pruebas de Bluetooth.
$ErrorActionPreference = 'Stop'
$Raiz = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Push-Location $Raiz
try {
    Write-Host 'AutoOS V12: pruebas BLE simuladas (5 escenarios)' -ForegroundColor Cyan
    & node '.\tools\test_bluetooth_v12.cjs'
    if ($LASTEXITCODE -ne 0) { throw 'Pruebas BLE de V12 fallaron' }
    Write-Host 'AutoOS V12: siete pasos de compilacion y kernel' -ForegroundColor Cyan
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\tools\validar_entrega_v11.ps1'
    if ($LASTEXITCODE -ne 0) { throw 'Validacion V11/React incompleta' }
    Write-Host 'OK: V12 compilo y sus pruebas terminaron. Validar BLE fisico y nube manualmente.' -ForegroundColor Green
} finally {
    Pop-Location
}
