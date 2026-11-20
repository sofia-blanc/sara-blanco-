# AutoOS — Verificación final y publicación estable

**Objetivo:** publicar la versión que ya funciona en el equipo, preservando la conexión comprobada con Supabase y sin agregar nuevas funciones.

## Estado demostrado en la sesión de pruebas

- La Caja Negra de React registra eventos `DISPATCH`, `COMPLETION`, `STATE_CHANGE`, GPS y otros.
- El indicador de sincronización mostró **24 confirmados y 0 pendientes**.
- Una consulta directa en Supabase `public.eventos` devolvió eventos `AutoOS Caja Negra T...`, con detalles de tick y origen `caja_negra_autoos`.
- El flujo React -> Streamlit/Python -> Supabase funciona al menos para los eventos observados. **Esto no demuestra todavía la recuperación automática del historial de Supabase dentro de Caja Negra al reiniciar**.
- Los contadores de RAM/CPU/batería corresponden al **modelo de simulación React**, no a la memoria física del computador ni a una medición del kernel Python.

## Paso 1. Ejecutar controles locales

Desde la raíz del proyecto en PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\validar_v12.ps1
powershell -ExecutionPolicy Bypass -File .\tools\verificar_entrega_final.ps1
```

El segundo comando es **solo lectura**: revisa rutas, existencia de archivos, `.gitignore`, estado Git y artefactos compilados. No sube, modifica ni despliega nada. Si aparecen errores, no publiques.

## Paso 2. Verificación visual (manual)

| Módulo | Prueba mínima para la sustentación | Resultado |
|---|---|---|
| Inicio | Todos los módulos abren y vuelven al menú sin errores de navegación | Pendiente |
| Apariencia | Modo claro y oscuro: títulos, formularios y controles legibles | Pendiente |
| GPS | Inicia ruta, cambia ubicación simulada, recalcula y registra pérdida de señal | Pendiente |
| Cabina | Los sensores abren su herramienta correcta; los paneles no se recortan ni desbordan | Pendiente |
| Multimedia | Botones muestran respuesta; Web Bluetooth indica si está bloqueado o no soportado | Pendiente |
| Simulación | Cambian CPU, RAM, procesos y batería; no hay doble avance de ticks | Pendiente |
| Planificador | PID, colas y Gantt explican las decisiones de CPU | Pendiente |
| Caja Negra | Genera eventos, confirma sincronización y reintenta solo si hay pendientes | Pendiente |
| Supabase | Aparecen eventos *automáticos nuevos* en la tabla real | Pendiente |
| Roles | Un rol sin autorización no escribe eventos protegidos | Pendiente |
| Reinicio | Tras cerrar la app, eventos remotos siguen en Supabase; comprobar aparte si se recuperan en UI | Pendiente |

## Paso 3. Confirmar eventos recientes en Supabase

En SQL Editor:

```sql
SELECT creado_en, severidad, mensaje,
       detalles->>'autoos_id' AS autoos_id,
       detalles->>'origen' AS origen
FROM public.eventos
WHERE mensaje LIKE 'AutoOS Caja Negra%'
ORDER BY creado_en DESC
LIMIT 30;
```

Confirmar que aparezcan **nuevos** registros después del ensayo de la simulación. Para buscar repetidos:

```sql
SELECT detalles->>'autoos_id' AS autoos_id, COUNT(*) AS total
FROM public.eventos
WHERE detalles->>'origen' = 'caja_negra_autoos'
  AND detalles ? 'autoos_id'
GROUP BY detalles->>'autoos_id'
HAVING COUNT(*) > 1
ORDER BY total DESC;
```

Si la segunda consulta devuelve filas, reportar posibles duplicados: la comprobación de id de la V14 reduce duplicaciones, pero no equivale a una restricción única transaccional.

## Paso 4. Preparación para GitHub

```powershell
git status --short
git branch --show-current
git remote -v
git diff --check
```

- Revisar **todos** los cambios antes de `git add`; no añadir secretos `.streamlit/secrets.toml`, `web/.env`, tokens, bases de datos temporales, capturas privadas ni respaldos `.autoos_*`.
- Verificar que los cambios de Julián y otros integrantes estén incorporados o se integren a través de un Pull Request.
- No hacer `git push --force`, no sobreescribir `main`, y no mezclar una rama vieja sin revisar diferencias.
- Incluir `Auto/autoos_unified.html`, `Auto/bridge_component/index.html`, `Auto/blackbox_cloud_sync.py`, `web/src/cloud/blackboxSync.ts` y los demás archivos editados, no solo CSS.
- La rama remota `main` puede estar más antigua que lo que se prueba en el computador: un build local aprobado **no** significa que la versión pública esté actualizada.

**Recomendación:** crear una rama `release/autoos-v14-estable` desde la rama local que contiene V14, subir esa rama y abrir un PR hacia `main`. Revisar el PR con el equipo antes de fusionarlo.

## Paso 5. Streamlit Cloud

- Entrada: archivo raíz `app.py`, rama `main` **después de la fusión del PR**.
- En la configuración de la aplicación, registrar en `Secrets` la sección `[supabase]` con `url` y **clave pública**. Nunca subir el archivo local.
- Revisar la dependencia `supabase` en `requirements.txt` si el código Python la necesita en Cloud; no asumir que porque `pip install supabase` funcionó localmente ya se instaló en el despliegue.
- Abrir la **URL pública** y repetir GPS, Simulación, Caja Negra y la consulta SQL de eventos automáticos. Abrir el enlace exacto que usa el profesor, no solo la página raíz.
- Verificar la versión publicada en un navegador privado para descartar caché local.

## Criterio de cierre

La entrega estará lista cuando se hayan completado las pruebas de módulos, la compilación, la lectura/escritura de eventos en Supabase desde la **URL pública**, la revisión de permisos y la revisión del PR con el equipo. Anotar errores residuales en README, en lugar de afirmar que no hay bugs.
