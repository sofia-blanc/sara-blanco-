@echo off
setlocal
cd /d "%~dp0web"
where node >nul 2>nul
if errorlevel 1 (
  echo ERROR: Debes instalar Node.js 20 o superior desde https://nodejs.org/
  pause
  exit /b 1
)
if not exist node_modules\vite (
  echo Instalando dependencias la primera vez. Requiere conexion a Internet...
  call npm install
  if errorlevel 1 (
    echo ERROR en npm install. Revisa tu conexion y vuelve a intentarlo.
    pause
    exit /b 1
  )
)
echo.
echo AUTOOS SIMULATION CENTER: abre http://localhost:3000
start "" "http://localhost:3000"
call npm run dev
pause
