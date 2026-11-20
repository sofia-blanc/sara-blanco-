# AutoOS — Confirmación de eventos Supabase (corrección puntual)

## Situación comprobada

El diagnóstico CLI guardó y leyó un evento real en `public.eventos`. Por ello están demostradas la conectividad y la escritura desde Python, **pero no necesariamente el flujo React → Streamlit**.

## Hallazgo del código

`CloudStatus` enviaba `autoos:cloud-event` mediante `sendCloudRequest`, pero dejaba en pantalla un mensaje de espera aunque el servidor devolviera `cloud.ok` y `cloud.ack`. En cambio, la consulta de `dispositivos` podía verse correcta aunque fallara el evento.

## Corrección

- Una solicitud obtiene un `requestId` único.
- El componente solo acepta la respuesta si `cloud.ack === requestId`.
- El resultado indica **CONFIRMADO**, **OPERACIÓN RECHAZADA** o **SIN CONFIRMACIÓN**, sin confundir un timeout con un fallo de la BD.
- El evento contiene un identificador visible en su mensaje, por ejemplo `Informe manual AutoOS [event_...]: ...`, que se puede buscar en el editor de la tabla `eventos`.
- Si no existe el componente Streamlit, se indica la situación y solo se usa el cliente directo si tiene una clave pública configurada.
- No se modifican `Auto/config.py`, `Auto/app.py`, RLS, la clave pública, Supabase ni el kernel.

## Instalación

Desde PowerShell en la raíz `AutoOS`:

```powershell
Expand-Archive -LiteralPath "$env:USERPROFILE\Downloads\AutoOS_Correccion_Confirmacion_Eventos.zip" -DestinationPath "." -Force
python .\tools\reparar_confirmacion_eventos.py
powershell -ExecutionPolicy Bypass -File .\tools\validar_v12.ps1
```

Si el validador termina bien, reiniciar completamente Streamlit:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Prueba manual obligatoria

1. Abrir **Nube / Supabase** desde la aplicación que inició Streamlit, no solo el servidor de Vite.
2. Pulsar **REGISTRAR EVENTO DE PRUEBA** una sola vez y leer el nuevo texto de confirmación.
3. Si aparece **CONFIRMADO**, buscar el identificador `event_...` en `Table Editor → public → eventos`.
4. Si aparece **OPERACIÓN RECHAZADA**, revisar el mensaje: en particular, el RBAC Python del perfil actual puede prohibir la operación aunque React muestre otro perfil. No desactivar RLS.
5. Si aparece **SIN CONFIRMACIÓN**, verificar que exista `Auto/bridge_component/index.html` y que el validador de V12 haya regenerado el bundle tras compilar.

## Limitaciones

Las pruebas del script y de sintaxis no verifican por sí solas la comunicación real en el navegador. El resultado debe comprobarse en Streamlit con la tabla remota abierta. Nunca compartir `secrets.toml` ni claves privadas.
