# AutoOS - Preflight de publicacion (solo lectura).
# No modifica archivos, no realiza commit, push ni despliegue.
$ErrorActionPreference = 'Stop'
$Raiz = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Errores = New-Object System.Collections.Generic.List[string]
$Advertencias = New-Object System.Collections.Generic.List[string]

Push-Location $Raiz
try {
    Write-Host 'AUTOOS - PREPARACION DE ENTREGA (solo lectura)' -ForegroundColor Cyan

    # 1. Verificar que estemos en un repositorio Git.
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        $Errores.Add('Git no esta instalado o no figura en PATH.')
    } else {
        & git rev-parse --is-inside-work-tree *> $null
        if ($LASTEXITCODE -ne 0) {
            $Errores.Add('Esta carpeta no es un repositorio Git. No publiques desde aqui.')
        } else {
            $Rama = (& git branch --show-current).Trim()
            $Commit = (& git rev-parse --short HEAD).Trim()
            Write-Host "Rama actual: $Rama   Commit: $Commit"
            if ($Rama -eq 'main') {
                $Advertencias.Add('Estás en main: crea una rama de entrega antes de agregar archivos o publicar.')
            }
            $Pendientes = @(& git status --porcelain)
            Write-Host "Cambios locales pendientes: $($Pendientes.Count)"
            if ($Pendientes.Count -eq 0) {
                $Advertencias.Add('No hay cambios locales. Confirma que la V14 ya esté incluida en esta rama.')
            }
            $Stage = @(& git diff --cached --name-only)
            $ArchivosPeligrosos = @($Stage | Where-Object {
                $_ -match '(^|/)(secrets\.toml|\.env(\..*)?)$' -and $_ -notmatch '\.example$'
            })
            if ($ArchivosPeligrosos.Count -gt 0) {
                $Errores.Add('Hay archivos de secretos staged para commit. Desmárcalos antes de publicar.')
            }
            $Track = @(& git ls-files)
            $SecretosRastreados = @($Track | Where-Object {
                $_ -match '(^|/)(secrets\.toml|\.env(\..*)?)$' -and $_ -notmatch '\.example$'
            })
            if ($SecretosRastreados.Count -gt 0) {
                $Errores.Add('El repositorio tiene archivos de secretos versionados. Deben eliminarse del indice; rota claves si fueron publicadas.')
            }
            & git check-ignore -q -- '.streamlit/secrets.toml'
            if ($LASTEXITCODE -ne 0) {
                $Errores.Add('Git no ignora .streamlit/secrets.toml.')
            }
            & git check-ignore -q -- 'web/.env'
            if ($LASTEXITCODE -ne 0) {
                $Errores.Add('Git no ignora web/.env.')
            }
        }
    }

    # 2. Validar entradas y recursos publicables.
    $Obligatorios = @(
        'app.py',
        'Auto/app.py',
        'Auto/autoos_unified.html',
        'Auto/bridge_component/index.html',
        'web/package.json',
        'web/package-lock.json',
        'web/src/App.tsx',
        'tools/build_streamlit_bundle.py',
        'Auto/blackbox_cloud_sync.py',
        'web/src/cloud/blackboxSync.ts',
        'docs/ETAPA_14_CAJA_NEGRA_SUPABASE.md'
    )
    foreach ($Rel in $Obligatorios) {
        if (-not (Test-Path -LiteralPath $Rel -PathType Leaf)) {
            $Errores.Add("Archivo requerido no encontrado: $Rel")
        }
    }

    # 3. Un bundle muy pequeno puede indicar una compilacion incompleta.
    if (Test-Path -LiteralPath 'Auto/autoos_unified.html' -PathType Leaf) {
        $Tamano = (Get-Item -LiteralPath 'Auto/autoos_unified.html').Length
        Write-Host ("HTML integrado: {0:N1} KB" -f ($Tamano / 1024.0))
        if ($Tamano -lt 100000) {
            $Advertencias.Add('Auto/autoos_unified.html es inusualmente pequeño; regenera el bundle antes de publicar.')
        }
    }

    # 4. Los secretos solo son necesarios en ejecucion. No se leen ni se imprimen.
    if (Test-Path -LiteralPath '.streamlit/secrets.toml' -PathType Leaf) {
        Write-Host 'Configuracion local de Streamlit: presente (contenido no inspeccionado).'
    } else {
        $Advertencias.Add('No existe .streamlit/secrets.toml local. Si usas Supabase, configura los secretos de Streamlit.')
    }

    # 5. El estado remoto NO puede verificarse sin desplegar.
    $Advertencias.Add('PENDIENTE MANUAL: verificar la URL publica, sus secrets y el flujo de eventos en Supabase Cloud.')
    $Advertencias.Add('PENDIENTE MANUAL: probar tema claro/oscuro, GPS, simulacion, roles, Caja Negra y botones.')
    $Advertencias.Add('PENDIENTE MANUAL: comprobar que no exista un PR del equipo con cambios incompatibles.')

    Write-Host ''
    foreach ($M in $Advertencias) { Write-Host "AVISO: $M" -ForegroundColor Yellow }
    foreach ($E in $Errores) { Write-Host "ERROR: $E" -ForegroundColor Red }
    if ($Errores.Count -gt 0) {
        Write-Host "NO LISTO: $($Errores.Count) bloqueo(s) de entrega." -ForegroundColor Red
        exit 1
    }
    Write-Host 'PRECHECK APROBADO: no se detectaron bloqueos en los archivos y Git examinados.' -ForegroundColor Green
    Write-Host 'Esto NO certifica el funcionamiento de Streamlit Cloud ni sustituye las pruebas manuales.' -ForegroundColor Yellow
} finally {
    Pop-Location
}
