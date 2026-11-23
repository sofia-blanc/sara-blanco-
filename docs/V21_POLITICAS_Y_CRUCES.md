# AutoOS V21 — Dos cruces y protección de energía persistente

**Corrección a V20.** La misión mantiene sus 20 minutos virtuales, pero solo presenta dos bifurcaciones: **minutos 8 y 16**, con avisos en 6–8 y 14–16. No interrumpe la conducción ni exige hacer clic. Termina después del minuto 20 con dos decisiones de cruce en el informe. Las intervenciones adicionales del centro técnico no cambian el calendario de cruces.

## Caso corregido: batería crítica

1. Iniciar escenario «Batería crítica», mover el vehículo al carril izquierdo antes del minuto 8.
2. En el minuto 8 se selecciona `power_save` (ahorro extremo) y `App.handleSimulatorAction` aplica `makeBattery(prev.level,true)` y suspende procesos multimedia/confort; ambos cambios permanecen en el estado compartido.
3. Antes del minuto 16, mover al carril derecho. En ese cruce se selecciona `ignore`, que aquí significa **no hacer cambios adicionales**. V21 registra la elección, mantiene la política ya activada y **no ejecuta** la penalización de 6 puntos ni la parada forzada de V18.
4. La batería sigue consumiéndose por tracción y servicios restantes; el ahorro NO garantiza energía infinita. Si llega a cero, la misión se detiene. Los choques, límites de impactos y fallas críticas siguen siendo consecuencias reales del juego.
5. Se verifica «AHORRO EXTREMO ACTIVO» en el tablero, y en Caja Negra un evento de continuación con ahorro persistente.

## Instalación

Extrae `AutoOS_V21_Ahorro_Persistente.zip` dentro de la **raíz ya existente** del proyecto AutoOS, no dentro de `AutoOS_1` ni de la carpeta anidada. Después ejecuta:

```powershell
python .\tools\aplicar_v21.py
powershell -ExecutionPolicy Bypass -File .\tools\validar_v21.ps1
```

El script guarda respaldo en `.autoos_v21_backup` y aborta sin escribir si la versión no coincide. Reconstruir desde Vite es obligatorio: Streamlit lee HTML compilado en `Auto/autoos_unified.html` y `Auto/bridge_component/index.html`.

## Alcance de pruebas

Se añaden pruebas puras de los cruces, persistencia de ahorro, fin de ruta y contrato estático de UI, más el validador TypeScript/Vite. La conducción y sincronización con Supabase requieren prueba manual en la instancia real antes de entregar. El kernel Python y secretos no se modifican.
