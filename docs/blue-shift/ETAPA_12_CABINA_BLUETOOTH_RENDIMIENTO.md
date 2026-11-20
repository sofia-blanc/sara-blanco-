# AutoOS — Etapa 12: experiencia de Cabina, BLE y rendimiento

## Objetivo
Convertir el menú en una navegación comprensible para la exposición del **sistema operativo vehicular** y corregir el comportamiento del botón BLE y la distribución de la interfaz sin modificar CPU, RAM, GPS, Supabase ni kernel Python.

## Archivos y responsabilidades

| Archivo | Responsabilidad |
|---|---|
| `web/src/components/CinematicMenu.tsx` | Vista previa con siete módulos, accesos reales y descripciones funcionales, sin ilustración SVG gigante. |
| `web/src/v12-finish.css` | Reduce animaciones continuas; muestra correctamente el menú, márgenes, modos claro/oscuro y contenedores. |
| `web/src/components/ModuleScene.tsx` | Nombre comprensible del módulo **Cabina y Telemetría**. |
| `web/src/components/CockpitExplorerV4.tsx` | Objetivo, entradas, salidas y pasos de uso de Cabina. |
| `web/src/components/CockpitToolSceneV6.tsx` | Orientación de herramientas del cockpit sin ocultar que parte de la telemetría es propia del cockpit heredado. |
| `web/src/App.tsx` | Solicita permiso `allow="bluetooth"` en el iframe interior. |
| `Auto/autoos_interactive.html`, `web/public/autoos_interactive.html` | Emparejamiento Web Bluetooth y diagnóstico visible; ambas copias deben ser iguales. |
| `Auto/app.py` | Elimina la etiqueta redundante «Interfaz cinematográfica» de Streamlit. |

## Qué hace Cabina y Telemetría

- **Objetivo:** supervisar instrumentos, sensores y funciones de confort del vehículo.
- **Entradas:** GNSS/GPS, cámara, LiDAR/radar, CAN-FD, 5G, HVAC, audio.
- **Salidas:** estados y alertas, controles con permisos y eventos de auditoría.
- **Uso:** seleccionar instrumento → inspeccionar datos → ejecutar acción → observar el cambio y consultar recursos e historial.
- **Límite del prototipo:** el Cockpit heredado mantiene algunos valores y lógica propios. No deben describirse como mediciones físicas del kernel Python.

## Bluetooth: qué funciona y qué no

Se solicita un dispositivo por `navigator.bluetooth.requestDevice()` **desde un clic del usuario** y se intenta conectar mediante GATT. Solo al recibir `server.connected` se muestra conectado. Si ocurre una desconexión se borra el estado. Se informa cuando no hay HTTPS, el navegador no expone Web Bluetooth, el iframe impide permisos, el usuario cancela o el dispositivo no admite GATT.

Web Bluetooth NO empareja auriculares Bluetooth Classic ni reproduce Spotify de forma automática. Para Spotify se utiliza su reproductor o el enlace QR independiente. En Streamlit Cloud, el iframe externo generado por la plataforma también puede imponer políticas de permisos que la aplicación no puede sobrepasar. Si se bloquea, se debe probar en Chrome/Edge con HTTPS/localhost o en una ventana de origen que permita BLE, sin prometer una conexión que no se realizó.

## Rendimiento

- Se retiró la ilustración SVG decorativa gigante del menú.
- El fondo queda estático; se cancelaron animaciones continuas de partículas, círculos, gradientes, sombras y selección.
- No se modificaron los intervalos del GPS, del planificador ni de la simulación.
- Se respeta `prefers-reduced-motion`.
- El cambio no puede garantizar un FPS concreto; conviene verificarlo en el equipo destino.

## Pruebas para la entrega

1. Iniciar AutoOS y recorrer siete opciones con teclado y mouse; abrir/cerrar módulo.
2. Cambiar tema en inicio y dentro de Cabina; revisar títulos y contraste.
3. En Cabina seleccionar GPS, LiDAR y Multimedia y comprobar que no haya desplazamiento horizontal.
4. Seleccionar Multimedia y pulsar Emparejar BLE: debe mostrarse selector del navegador o una razón visible de fallo. No puede afirmarse conectado si no hay GATT real.
5. Entrar en Simulación y Planificador: confirmar CPU, RAM, batería, procesos, historial.
6. Ejecutar `powershell -ExecutionPolicy Bypass -File .\tools\validar_v12.ps1` para probar cinco casos BLE simulados y los siete pasos anteriores.
7. Verificar conexión Supabase desde su módulo: ningún cambio visual certifica por sí mismo las credenciales.

## Recuperación

Antes de cambiar archivos el instalador deja copias bajo `.autoos_v12_backups/<fecha>/`, respetando rutas originales. En caso de problemas, restaurar el archivo correspondiente desde esa carpeta y volver a generar `Auto/autoos_unified.html`.
