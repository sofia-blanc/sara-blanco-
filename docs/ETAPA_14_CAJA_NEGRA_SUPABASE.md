# AutoOS V14 — Caja Negra sincronizada con Supabase

## 1. Problema observado

El historial de Caja Negra en React mostraba `ARRIVAL`, `DISPATCH`, `COMPLETION`, `GPS` y `RUTA`, pero en `public.eventos` de Supabase aparecían únicamente los eventos creados por el botón manual y registros antiguos. **La conexión manual ya estaba probada**: lectura, INSERT y lectura del mismo registro.

## 2. Qué cambia

- `web/src/App.tsx` observa la misma lista de eventos de Simulación y GPS, sin crear otro planificador o reloj.
- `web/src/cloud/blackboxSync.ts` mantiene una cola de eventos en el navegador. Se envían lotes de hasta **6 eventos** cada **3,5 segundos** cuando hay un puente Streamlit disponible.
- Para no saturar Supabase, los mensajes rutinarios de avance de ruta se reducen a uno cada cinco ticks; fallas de GPS y alertas **no** se filtran.
- `tools/streamlit_component_bootstrap.js` acepta el nuevo mensaje `autoos:blackbox-batch`.
- `Auto/app.py` lo recibe desde el componente, verifica permisos del lado Python y devuelve un acuse independiente de «Verificar conexión real».
- `Auto/blackbox_cloud_sync.py` valida IDs, longitudes, clase de evento, tick, CPU, RAM y batería. Consulta primero `detalles.autoos_id` para evitar que un reintento duplique registros ya visibles en Supabase; después realiza el INSERT.
- La Caja Negra muestra **confirmados**, **pendientes** y botón **Reintentar pendientes**. Un fallo no se presenta como éxito y los eventos pendientes siguen disponibles localmente.

### Datos de la tabla

Los eventos se guardan en `public.eventos` con este formato aproximado:

| Columna | Valor |
|---|---|
| `tipo_evento` | `simulacion` |
| `severidad` | `info`, `advertencia` o `critico` |
| `mensaje` | `AutoOS Caja Negra T13 DISPATCH: CPU asignada ...` |
| `detalles` | `origen: caja_negra_autoos`, `autoos_id`, `clase`, `tick`, `bateria_pct`, `cpu_demanda_pct`, `ram_estimada_mb`, `tipo_medicion` |
| `resuelto` | `true` para eventos informativos |

**Nota académica:** CPU/RAM y batería provienen del modelo **React**. No son mediciones del sistema físico ni del kernel Python. El kernel Python sigue siendo una simulación separada con sincronización explícita.

## 3. Instalación en PowerShell

Desde la raíz de AutoOS, sobre la V12 con la corrección manual de eventos:

```powershell
Expand-Archive -LiteralPath "$env:USERPROFILE\Downloads\AutoOS_V14_Caja_Negra_Supabase.zip" -DestinationPath "." -Force
python .\tools\instalar_autoeventos_v14.py
powershell -ExecutionPolicy Bypass -File .\tools\validar_v12.ps1
```

El instalador comprueba los puntos de integración antes de modificar el proyecto y crea respaldos en `.autoos_v14_backup/`. Ejecutarlo otra vez no duplica cambios. Los secretos y la configuración de Supabase **no se modifican**.

## 4. Prueba de extremo a extremo

1. Iniciar `streamlit run app.py` y entrar como perfil de Mecánico en la sesión autorizada del servidor.
2. Abrir **Simulación**, escoger sobrecarga CPU y avanzar 8–15 ticks; opcionalmente iniciar una ruta GPS.
3. Abrir **Caja Negra**. Comprobar eventos y observar el contador **pendientes**; después observar cómo aumentan los **confirmados**.
4. Abrir **Supabase → Table Editor → public → eventos** y buscar `AutoOS Caja Negra`. Ordenar por `creado_en` descendente. Los campos `detalles.autoos_id` deben corresponder a los eventos sincronizados.
5. Pulsar **Reintentar pendientes** solo si hay eventos pendientes; el servidor comprueba `autoos_id` para reducir duplicaciones.
6. Si aparece «RBAC: ...», consultar el perfil real del servidor Streamlit. Cambiar el selector visual de React no concede permisos de Python.

**Límites**: sin red, los mensajes quedan en `localStorage` de ese navegador y se intentarán enviar luego. La cola tiene un máximo de 240 eventos para evitar crecimiento sin límites. La deduplicación se apoya en `detalles.autoos_id` y en la lectura permitida por RLS; no equivale a una garantía transaccional de exactamente una vez con dos sesiones escribiendo simultáneamente. El cierre definitivo de sesión y la limpieza del navegador pueden perder mensajes pendientes.

## 5. Seguridad y despliegue

No se exponen claves secretas al navegador. La credencial vive en `st.secrets` del servidor. El puente pide permiso `proceso.crear` a Python, como en el guardado manual existente. No desactivar RLS. Para Streamlit Cloud, recompilar y subir el nuevo `Auto/bridge_component/index.html`, además del código Python y React. No subir `.streamlit/secrets.toml`.

## 6. Archivos

Se modifican `Auto/app.py`, `web/src/App.tsx`, `web/src/components/AutoOSModulesV11.tsx`, `web/src/kernelBridge.ts`, `tools/streamlit_component_bootstrap.js`. Se agregan `Auto/blackbox_cloud_sync.py`, `web/src/cloud/blackboxSync.ts` y `AutoOS_1/tests/test_v14_blackbox_cloud_sync.py`.

## 7. Comprobaciones antes de publicación

`python -m unittest discover -s AutoOS_1/tests -p 'test_v14_blackbox_cloud_sync.py'`, `npm run lint`, `npm run test:sim`, `npm run build` y `python tools/build_streamlit_bundle.py`. Deben terminar sin errores. Comprobar visualmente el modo claro, el historial y el estado de nube **en la URL del despliegue**, no solo localmente.
