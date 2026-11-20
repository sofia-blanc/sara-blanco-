# AutoOS V11 — arquitectura, efectos y guía de sustentación

## 1. Qué representa AutoOS

AutoOS es un **simulador didáctico de un sistema operativo vehicular**, no
software certificado para manejar un automóvil. Debemos explicar esto al
profesor: medimos recursos de un entorno virtual y contrastamos algunos
resultados con el motor Python de kernel, que es otra implementación.

## 2. Estructura y fuentes de verdad

```text
Streamlit Cloud / app.py
    └─ Auto/app.py (panel RTOS Python y componente bidireccional)
        └─ Auto/bridge_component/index.html (compilado)
            └─ React / web/src/App.tsx (único estado del vehículo virtual)
                ├─ Menú principal: components/CinematicMenu.tsx
                ├─ Cabecera: components/ModuleScene.tsx
                ├─ Inicio/GPS/Caja Negra/Supabase: components/AutoOSModulesV11.tsx
                ├─ Simulación: components/SimulationCenter.tsx
                ├─ Planificador: utilidades schedulerEngine.ts
                ├─ Recursos: simulation/resources.ts
                ├─ Navegación: simulation/navigation.ts
                ├─ Instrumentos heredados: autoos_interactive.html (iframe aislado)
                └─ Kernel Python espejo: kernelBridge.ts → Auto/bridge_react_kernel.py
```

- React calcula la demanda CPU, RAM estimada, SWAP, consumo, batería,
  subsistemas y ruta virtual. **App.tsx** es su fuente de verdad.
- El kernel Python conserva su **propio planificador y PIDs**. El puente
  crea procesos equivalentes cuando un mecánico autorizado sincroniza;
  NO sustituye automáticamente el scheduler React.
- La Caja Negra agrega eventos de React y de navegación; se puede
  exportar JSON. Su persistencia local usa `autoos_v11_blackbox`.
- Supabase se usa a través de `config.py` del servidor para lectura y
  registro de eventos; no se publica una clave de servicio en el HTML.

## 3. Demostración recomendada (5–7 minutos)

1. Inicio: explicar CPU (demanda ≠ utilización), RAM 2048 MB virtual,
   batería simulada y procesos admitidos.
2. GPS: elegir ruta de prueba, iniciar, avanzar o dejar 1,8 s/ciclo.
   Mostrar kilómetros, posición virtual, ETA y disminución de batería.
3. GPS: como mecánico inyectar fallo GNSS: el odómetro avanza pero la
   última coordenada válida queda congelada. Abrir Caja Negra.
4. Simulación: seleccionar sobrecarga de CPU, iniciar, suspender
   multimedia y ver el impacto en RAM, CPU y consumo.
5. Planificador: comprobar algoritmo RR, cola y Gantt. Si se tiene
   acceso a Streamlit, usar `Sincronizar kernel` y explicar el mapa de PIDs.
6. Supabase: ejecutar **Verificar conexión real** y guardar evento. Si
   el diagnóstico falla, mostrar por qué (secrets, RLS, red o tablas) en
   lugar de fingir que está ONLINE.
7. Cambiar a tema claro: explicar colores y contraste. Regresar al menú
   con efectos de entrada, salida y selección.

## 4. Cómo funciona el GPS

`createMission` define punto de origen; `advanceMission` actualiza un minuto
virtual. Las distancias y rutas son datos de ejemplo y el mapa SVG no es
cartografía real. La opción **Leer ubicación real** utiliza
`navigator.geolocation`, solo al solicitar autorización; no modifica la
ruta virtual, no envía coordenadas a Supabase y puede no funcionar en un
iframe si el navegador deniega permiso. OSM solo se abre con un clic.

Una misma llamada `handleSimulatorDriveTick` mueve los estados de CPU,
BMS, energía y GPS; si la simulación está abierta sus propios ticks son
los que avanzan el vehículo. Así evitamos dos relojes simultáneos.

## 5. Colores, movimiento y accesibilidad

`v11-reload.css` incluye fondo oceánico, personaje geométrico original,
selección blanca/rosa con diagonales, fondos animados y respuesta táctil.
El menú admite flechas, Enter y números 1–7, más `prefers-reduced-motion`.
El modo claro utiliza texto oscuro sobre fondo claro en contenidos, pero
la cabecera permanece azul oscuro, evitando título blanco invisible.

## 6. Supabase — qué existe y cómo diagnosticar

- Streamlit: `Auto/config.py` busca `[supabase] url/key` o variables de
  entorno. El botón de V11 llama `test_supabase_connection_py`, que
  consulta la tabla `dispositivos` realmente.
- `Auto/app.py` escucha `autoos:cloud-test`, `autoos:cloud-event` y `autoos:cloud-report`. El
  registro manual respeta el permiso **Python** `proceso.crear`.
- React directo: `web/src/supabaseClient.ts` utiliza URL + clave pública
  Vite y RLS. En el paquete de Streamlit puede no estar configurado:
  el servidor puede seguir conectado por su propio mecanismo.
- Nunca poner `service_role` o claves privadas en `web/.env`, JS o GitHub.
- El informe de simulación se envía a Python al finalizar; el servidor valida
  su tamaño, escenario y estructura en `Auto/v11_cloud_bridge.py`, lo
  conserva localmente y **solo indica éxito Cloud si Supabase confirma
  la escritura**. Una copia local no demuestra persistencia remota.
- Un indicador `online` requiere una consulta exitosa; claves presentes
  por sí solas no son evidencia de conectividad.

## 7. Límites honestos para la entrega

- No son datos de un vehículo real. No sustituye un GPS automotriz.
- El kernel Python y el simulador React son dos motores con puente de
  sincronización, no un RTOS físico único.
- El tema de Persona 3 Reload es una referencia artística; los gráficos,
  el avatar abstracto y los efectos sintetizados son originales de AutoOS.
- Los controles de Spotify dependen de disponibilidad, permisos de su
  proveedor y de la interacción del usuario; no podemos garantizar
  reproducción en todos los navegadores.
- No prometer “0 bugs”. Ejecutar la lista de validación y documentar
  resultados de una prueba real en Streamlit Cloud.

## 8. Qué explicar si el profesor pregunta por el código

| Pregunta | Ubicación y explicación |
|---|---|
| ¿Quién controla el estado? | `App.tsx`, estados `simState`, `devices`, `battery`, `mission`. |
| ¿Cómo se asigna CPU? | `schedulerEngine.ts`: FCFS, RR, prioridad apropiativa. |
| ¿Cómo se representa memoria? | `simulation/resources.ts`: suma `memoryMb`, límites 2048 MB y SWAP estimada. |
| ¿Qué cambia al conducir? | `handleSimulatorDriveTick`: potencia/energía, tick, GPS. |
| ¿Cómo se almacena historial? | `missionEvents` + `simState.events`, exportación JSON y almacenamiento local. |
| ¿Dónde se conecta a Supabase? | `Auto/config.py` + protocolo `Auto/app.py`. |
| ¿Dónde está la seguridad? | Rol validado en Python por `tiene_permiso`; React solo controla la navegación visual. |
| ¿Cómo llega al profesor? | `npm run build` → `build_streamlit_bundle.py` → `Auto/bridge_component/index.html` → `app.py` de Streamlit. |
