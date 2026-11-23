# AutoOS V19 — minijuego interactivo y sistema operativo simulado

## 1. Qué se entregó

La simulación V18 se convierte en un minijuego de **tres carriles** que funciona dentro de la misma aplicación Streamlit/React y conserva los escenarios V15–V18, el planificador, la batería del modelo, los periféricos, Caja Negra y la sincronización ya existente.

### Controles

- **Flecha izquierda**: desplazarse un carril a la izquierda.
- **Flecha derecha**: desplazarse un carril a la derecha.
- **Flecha arriba**: aumentar 5 km/h de velocidad virtual.
- **Flecha abajo**: reducir 5 km/h de velocidad virtual.
- **Botones ←/→**: alternativa visible para ratón y pantalla táctil.
- Para usar las flechas, haz clic en la zona de la carretera si el foco se ha ido a otra parte de Streamlit. El minijuego enfoca la escena al comenzar.

## 2. Reglas de la partida

1. Elegir un escenario e iniciar.
2. Conducir y esquivar obstáculos que se aproximan por carriles.
3. El motor genera obstáculos en una secuencia reproducible y con perspectiva; **no hay objetos colocados aleatoriamente con resultados impredecibles**.
4. Un choque produce una interrupción de seguridad: detiene el vehículo, reduce la batería del estado compartido y registra un evento crítico.
5. La recuperación requiere pulsar el botón específico; reanuda a 30 km/h.
6. Tras **tres impactos**, la partida se considera fallida; hay que reiniciar o generar informe.
7. Cada cinco minutos virtuales, las bifurcaciones V17 siguen apareciendo y la simulación se pausa para decidir.
8. Elegir «Continuar sin cambios» en batería crítica conserva la penalización V18 y detiene el vehículo.
9. Al completar **20 minutos virtuales**, se genera automáticamente el informe si no existe un checkpoint pendiente.

El reloj acelerado es didáctico: **1 segundo real = 1 minuto virtual**. El movimiento de obstáculos se calcula más frecuentemente para que el control lateral sea interactivo.

## 3. Conexión técnica con el SO

| Acción | Código | Efecto real del modelo compartido |
|---|---|---|
| Cambiar de carril | `steerDrivingGame` → `onGameEvent` | Evento `STATE_CHANGE` del planificador React |
| Avanzar | `handleSimulatorDriveTick` | Ejecuta el tick del SO, modifica energía, batería, GPS y recursos |
| Esquivar | `advanceDrivingGame` → `onGameEvent` | Deja evento de ruta completada sin choque |
| Colisionar con obstáculo | `SimulationCenter` → `onBattery` / `onGameEvent` | Detención, penalización energética, evento crítico |
| Interferencia ADAS | `onFault('DEV_CAM_FRONT')` | Falla del dispositivo y carga de diagnóstico |
| Sobrecarga CPU | `onCpuStress` | Inserta proceso de carga en el planificador |
| Elegir ahorro extremo | `choose` → `onAction('power_save')` | Suspende multimedia/confort en el motor existente |
| Continuar sin cambios | `choose` (V18) | Velocidad 0, penalización BMS y evento de riesgo |

**No se fabrican valores de CPU ni RAM para el juego.** Las métricas del HUD vienen de `resources`, calculados por el sistema que usa `App.tsx`.

## 4. Archivos modificados

- `web/src/simulation/drivingGameV19.ts`: reglas puras de carriles, obstáculos, perspectiva, colisión y esquiva.
- `web/src/components/MissionStageV17.tsx`: SVG del automóvil y obstáculos, controles, avisos y checkpoints.
- `web/src/components/SimulationCenter.tsx`: estado de juego, temporizador, colisiones, recuperación y resultado.
- `web/src/App.tsx`: única puerta para registrar eventos del minijuego en `simState.events`.
- `web/src/v19-minigame.css`: estilo y respuesta de la escena.
- `web/tests/v19.test.cjs`: pruebas del motor de conducción.
- `web/tests/run.cjs`: ejecución de V19 junto a las pruebas anteriores.
- `web/src/main.tsx`: inclusión de estilos.

## 5. Por qué se diseñó así

**¿Por qué carriles discretos y no física 3D?** Porque permite decisiones controlables con teclado, pruebas deterministas y colisiones inequívocas sin añadir dependencias pesadas. Es la solución idónea para mostrar interacción con el planificador de forma verificable.

**¿Por qué el motor está separado de React?** Las funciones de `drivingGameV19.ts` reciben estado y devuelven estado; pueden probarse en Node sin navegador. React se limita a dibujar el resultado y ejecutar acciones de usuario.

**¿Por qué las colisiones no modifican CPU/RAM directamente?** Para evitar valores falsos o divergentes. Las consecuencias pasan por los callbacks existentes de `App.tsx`, que son los responsables del estado de procesos, energía y periféricos.

**¿Qué pasa si se cierra el navegador?** La partida activa existe en memoria del cliente; los informes previos siguen su flujo de almacenamiento, pero la posición instantánea no se recupera automáticamente. No se promete persistencia de partida entre sesiones.

**¿Los eventos están garantizados en Supabase?** No necesariamente. Se registran en el modelo de eventos React y pasan por el mecanismo de Caja Negra/puente existente. La sincronización final depende de conexión, permisos y confirmaciones de la nube; debe revisarse en la pestaña Caja Negra/Supabase.

**¿Es software para un vehículo real?** No. Es una simulación académica del comportamiento de sistemas operativos y subsistemas vehiculares, sin interfaces de conducción física ni certificación de seguridad automotriz.

## 6. Prueba de aceptación para el martes

1. Iniciar **Batería crítica** con perfil Mecánico.
2. Antes del primer checkpoint, usar ← / → y comprobar que el SVG cambia de carril.
3. Permanecer en carril central ante el primer cono, observar colisión y **parada de seguridad**.
4. Pulsar recuperar; comprobar que la velocidad pasa a 30 km/h.
5. Dejar correr hasta la bifurcación del minuto 5; elegir **ahorro extremo** y observar cambios en recursos.
6. Repetir en misión nueva y elegir **continuar sin cambios**; verificar parada y penalización BMS.
7. En Caja Negra filtrar por `[MINIJUEGO]`, verificar los eventos de cambio de carril y choque.
8. Comprobar **pendientes/confirmados** en la sincronización Supabase y consultar `public.eventos` si la conexión está disponible.
9. Repetir en perfil Pasajero: confirmar que no permite iniciar ni controlar laboratorios técnicos.
10. Tras la prueba, ejecutar `npm run lint`, `npm run test:sim`, `npm run build` y `python tools/build_streamlit_bundle.py`; confirmar que `Auto/bridge_component/index.html` contiene `v19-steering`.
