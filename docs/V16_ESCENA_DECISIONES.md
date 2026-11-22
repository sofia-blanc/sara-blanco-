# AutoOS V16 — Escena jugable y decisiones integradas

## Objetivo

Transformar el **Centro de Simulación** en una misión vehicular a pantalla ancha, con un vehículo claramente visible, HUD de recursos y decisiones dentro de la misma escena. Se conserva el laboratorio avanzado, el informe técnico y la bitácora; no se reinventa el kernel ni la conexión con Supabase.

## Arquitectura y archivos

| Archivo | Responsabilidad |
| --- | --- |
| `web/src/components/MissionStageV16.tsx` | Dibujo SVG original, HUD, estados, punto de decisión, botones y accesibilidad. **No almacena un segundo modelo de recursos**. |
| `web/src/simulation/missionGameV16.ts` | Reglas puras: permisos de laboratorio, checkpoints a intervalos de 5 ticks y parada por batería a cero. |
| `web/src/components/SimulationCenter.tsx` | Propietario de la sesión, reloj, velocidad, decisiones e informes. Reutiliza callbacks `onStart`, `onAction`, `onDriveTick`. |
| `web/src/App.tsx` | Origen de verdad de CPU/RAM/batería/procesos/dispositivos y sus eventos; **no se modifica** en V16. |
| `web/src/v16-mission.css` | Layout ancho, overlay de decisiones, adaptabilidad y animación ligera con reducción de movimiento. |
| `web/tests/v16.test.cjs` | Pruebas de checkpoints, límite de batería y permisos. |
| `web/src/main.tsx` | Importa el CSS del módulo V16. |
| `web/tests/run.cjs` | Añade las pruebas V16 a la suite habitual. |

## Flujo técnico real

1. El usuario elige un escenario en `SCENARIOS` y presiona **Iniciar escenario** dentro de la escena.
2. Puedes cambiar de escenario durante la sesión seleccionando otra tarjeta y pulsando **Cargar escenario seleccionado**; eso reinicia el laboratorio de forma explícita. `SimulationCenter.start` invoca `onStart`, implementado por `App.handleSimulatorStart` en React. El escenario restablece estados mediante `initialScenarioState`.
3. Cada segundo de demostración representa un minuto virtual: `onDriveTick` calcula la potencia con `estimatePowerW`, aplica un tick con `advanceOperatingSystemTick`, descuenta batería con `batteryAfterEnergyTick`, actualiza procesos y, si hay ruta activa, su posición virtual.
4. Al cumplir **5 ticks virtuales por decisión**, `decisionCheckpoint()` pausa el avance para solicitar una elección en la escena.
5. El usuario pulsa una opción del escenario. `SimulationCenter.choose` invoca `onAction`; el `handleSimulatorAction` de App aplica `applyScenarioAction` y, según el caso, cambia batería, algoritmo, velocidad o salud de dispositivos.
6. La opción elegida se añade a `decisions`, y el informe técnico generado al finalizar contiene la lista de decisiones y sus explicaciones.
7. Los eventos del planificador se muestran en Caja Negra. Si el puente bidireccional de Streamlit y Supabase están activos, V14 envía los eventos relevantes a la nube. **La aparición en el servidor debe verificarse; no se presupone conexión**.

## Ejemplo explicable al profesor: batería crítica

- Escenario `Batería crítica` comienza en 12% con velocidad virtual inicial del escenario.
- Elegir **Activar ahorro extremo** dispara `power_save`. El modelo V9 calcula el consumo con modo de ahorro y el planificador suspende tareas no críticas según sus políticas.
- Elegir **Reducir velocidad** limita a 35 km/h, con una demanda de tracción estimada inferior.
- Elegir **Continuar sin cambios** deja constancia de la decisión sin borrar las alertas.
- La batería **no continúa descontándose** al agotarse; la sesión queda pausada.

## Roles y permisos

La V16 **no confunde el rol de React con un usuario autenticado en el servidor**.

- Administrador y Mecánico: pueden iniciar escenarios, responder, modificar condiciones del laboratorio y generar informes.
- Conductor y Pasajero: no pueden controlar el laboratorio; disponen de los módulos permitidos por `accessPolicyV15.ts`.
- Los endpoints Python siguen aplicando autenticación y autorización independientes.

El componente llama a `maySimulate()` para mostrar controles activos solamente a roles autorizados; `SimulationCenter` también verifica los permisos antes de ejecutar la acción.

## Rendimiento y accesibilidad

- SVG propio, sin imágenes remotas ni fondos de video; la ilustración no depende de cargas externas.
- Se anima únicamente el desplazamiento gráfico de las marcas de carretera mientras la misión está en marcha.
- `prefers-reduced-motion: reduce` desactiva toda animación decorativa.
- Los botones son HTML reales, tienen estado `disabled` cuando corresponde y se puede navegar mediante teclado.
- Móvil/tableta: el panel de decisiones se apila bajo la información de ruta y evita recortes.

## Límites

- No es GPS vial ni telemetría de un vehículo físico. CPU/RAM son estimaciones de la simulación React. Para reservas del kernel Python, consultar su monitor RTOS.
- El progreso se mide en ticks del SO, no tiempo físico real.
- El CSS de Streamlit y los elementos embebidos del Cockpit antiguo no se modifican por esta actualización.

## Prueba de aceptación V16

1. Ejecutar `npm run lint`, `npm run test:sim`, `npm run build` y `python tools/build_streamlit_bundle.py`.
2. Abrir Streamlit en local; comprobar escena mayor de 600px en escritorio y que no haya desplazamiento horizontal al 100% de zoom.
3. Iniciar `Batería crítica` como Mecánico; detenerse en tick 5 automáticamente.
4. Elegir **Activar ahorro extremo**, comprobar cambio de procesos / consumo y que el reloj se reanude.
5. Repetir con **Pérdida de GPS**; elegir reiniciar GPS y observar el estado del receptor.
6. Finalizar informe y comprobar que registre decisiones y el estado inicial/final.
7. Abrir Caja Negra y confirmar que hay eventos del planificador; si Supabase está disponible, buscar eventos en `public.eventos`.
8. Seleccionar Pasajero y comprobar que no puede dirigir la simulación.
9. Activar modo claro/oscuro y comprobar los textos (el escenario mantiene su propio fondo oscuro para contraste).
10. Verificar el aspecto visual en el navegador: la sintaxis correcta de código no sustituye pruebas de UI.

## Cómo retirar V16

El instalador guarda copias de los archivos modificados en `.autoos_v16_backups/FECHA/`. Para revertir, recupera esos archivos y elimina únicamente los archivos nuevos V16. No hagas `git reset --hard` sobre un directorio con cambios de otras personas.
