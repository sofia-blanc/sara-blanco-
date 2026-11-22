# AUTOOS V17 — Simulación de caminos y portada renovada

## 1. Objetivo del cambio

Esta etapa responde a las observaciones del profesor: el inicio no debe dejar
espacios vacíos; la escena debe mostrar un automóvil convincente; y las
**decisiones deben presentarse como rutas alternativas en un checkpoint**, no
como una lista fija de botones presente en toda la conducción.

## 2. Componentes nuevos

- `web/src/components/MissionStageV17.tsx`: escena visual de la misión. Tiene una
  carretera vectorial, un vehículo original, HUD compartido y una bifurcación
  visual con 2–3 caminos. Los botones existen en el DOM **solo** durante `fork`.
- `web/src/simulation/missionGameV17.ts`: reglas puras `missionViewV17`,
  `routePathsV17`, `minutesUntilForkV17`, `canChoosePathV17`.
- `web/src/components/VehicleHeroV17.tsx`: ilustración estática de la portada,
  con etiquetas visuales de GPS, sensores y BMS.
- `web/src/assets/vehicle_rear_v17.webp`: ilustración original de vehículo,
  optimizada a WebP para cargar dentro de Streamlit.
- `web/src/v17-final.css`: presentación responsive de la escena y de Inicio.
- `web/src/v17-assets.d.ts`: declaración TypeScript para la imagen `?inline` de Vite.
- `web/tests/v17.test.cjs`: pruebas que impiden mostrar elecciones antes del
  checkpoint y las impiden con batería agotada.

## 3. Integración de la lógica anterior

No creamos otra batería, procesador ni planificador. `SimulationCenter.tsx`
continúa recibiendo `battery`, `devices`, `resources`, `state` y los callbacks
`onStart`, `onAction`, `onDriveTick` desde `App.tsx`.

Al pulsar un camino ocurre esta secuencia:

1. `MissionStageV17` consulta `canChoosePathV17` y llama `onSelect(id)`.
2. `SimulationCenter.choose(id)` comprueba además `checkpointDue` y el rol.
3. `onAction(id)` aplica efectos en el motor React (procesos, prioridades,
   dispositivos o estado energético, según el escenario y la acción).
4. `SimulationCenter` agrega la decisión al informe y reanuda el viaje si la
   batería permite continuar.
5. Los cambios y eventos pasan por la Caja Negra existente y su sincronización
   V14 con Streamlit/Supabase. No se hacen consultas directas desde la escena.

**Importante:** CPU y RAM son *estimaciones del modelo virtual*. El kernel
Python se muestra por separado en el panel técnico. No se controla un carro
físico ni se consulta un GPS real desde esta escena.

## 4. Máquina de estados de la experiencia

| Estado | Condición | Pantalla / Acciones |
|---|---|---|
| `ready` | No ha iniciado | Botón Iniciar |
| `driving` | Sesión y reloj activos | Carretera + próxima bifurcación; SIN decisiones |
| `paused` | Usuario pausó | Resume el trayecto; SIN decisiones |
| `fork` | Checkpoint de 5 minutos virtuales | Camino 1, 2 o 3; las opciones pausan el reloj |
| `exhausted` | Batería virtual 0 % | Vehículo detenido, opción Reiniciar |
| `finished` | Informe de sesión generado | Mensaje de finalización |

`minutesUntilForkV17` depende de los minutos transcurridos y el número de
respuestas confirmadas. Es decir, no hay un segundo reloj decorativo.

## 5. Accesibilidad, rendimiento y despliegue

- Los caminos son botones HTML accesibles por teclado y con etiquetas completas.
- El vehículo es un WebP transparente generado de forma original y cargado con
  `?inline`. Así la compilación Vite lo integra en el JS y
  `tools/build_streamlit_bundle.py` lo incluye en el HTML único.
- Solo se anima una línea vectorial de calzada, respetando
  `prefers-reduced-motion`. La imagen del carro es estática.
- Sin assets de Persona 3 Reload: se emplea una composición original inspirada
  en la tipografía inclinada, jerarquías y paleta de videojuegos.
- La portada agranda el automóvil, aumenta el ancho del preview, reduce el
  tamaño relativo del menú y limita el lienzo para eliminar huecos innecesarios.
- Los estilos están encapsulados bajo `#root .v17-...`.

## 6. Prueba para la sustentación

1. Abrir AutoOS con perfil Mecánico o Administrador.
2. Simulación → Batería crítica → Iniciar simulación.
3. Comprobar que NO aparezca ninguna decisión durante los primeros 4 minutos.
4. En el minuto 5, observar que el auto se detiene y aparecen caminos.
5. Elegir **Activar ahorro extremo**: debe aplicarse la política energética,
   suspender tareas no críticas y quedar un evento.
6. Revisar CPU/RAM/batería, Planificador, Caja Negra y los registros remotos en
   `public.eventos` de Supabase.
7. Probar Pausar/Reanudar, un escenario con 2 opciones, batería a cero,
   perfil Pasajero (sin permisos) y modo claro/oscuro.

## 7. Compatibilidad y seguridad

El instalador se ejecuta desde la raíz del repositorio y verifica los marcadores
V16 antes de modificar los componentes. Crea copias en `.autoos_v17_backup`;
**esta carpeta no debe incluirse en Git**. No se modifican claves, políticas RLS,
`Auto/blackbox_cloud_sync.py`, el kernel Python ni la estructura de Supabase.

Antes de fusionar a `main`, completar `tools/validar_v17.ps1` y una prueba real
con navegador. La ejecución de pruebas no equivale a garantía de cero errores.
