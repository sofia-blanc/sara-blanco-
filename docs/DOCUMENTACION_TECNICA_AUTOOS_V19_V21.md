# AutoOS V21 — Documentación técnica del minijuego y su integración con el sistema operativo

**Proyecto:** AutoOS — simulador académico de sistema operativo vehicular
**Versión documentada:** V21, acumulando los cambios de V19 y V20
**Fecha de entrega:** 24 de noviembre de 2026
**Tecnologías de esta parte:** React, TypeScript, SVG, Vite, Streamlit y kernel didáctico Python
**Alcance:** conducción interactiva, peligros y colisiones, bifurcaciones por carril, políticas de batería y vínculo con las métricas/eventos del SO simulado.

> **Nota de alcance.** AutoOS no conduce un automóvil físico. La CPU, RAM, procesos, batería y sensores del panel representan un **modelo académico**. El kernel de enseñanza escrito en Python tampoco reemplaza el kernel del sistema operativo anfitrión. Esta guía complementa el manual técnico V18 y reemplaza sus indicaciones antiguas sobre las bifurcaciones dentro del *minijuego*: en V21 ya no se pausa cada cinco minutos para elegir mediante clic.

## 1. Objetivo y evolución del código

El propósito del minijuego es que el usuario **controle** un automóvil virtual y observe decisiones que repercuten en el modelo de sistema operativo: consumo energético, procesos, estado de periféricos, seguridad y registro de eventos. La interfaz no debe limitarse a reproducir una animación.

| Versión | Contribución | Problema resuelto |
|---|---|---|
| **V19** | Motor determinista de tres carriles, obstáculos, esquiva, choques, recuperación y eventos | La escena pasa de demostración a interacción jugable. |
| **V20** | Selección automática de ruta según el carril y señalización anticipada | El conductor deja de depender de botones de bifurcación que pausaban la conducción. |
| **V21** | Cruces exclusivos en los minutos virtuales **8 y 16** y protección de ahorro energético persistente | Se evitan cruces excesivos y una parada injustificada después de elegir ahorro extremo y posteriormente «Continuar sin cambios». |

Una misión jugable tiene como meta **20 minutos virtuales**. Para este laboratorio, aproximadamente **un segundo real equivale a un minuto virtual**, mientras que el motor de obstáculos actualiza su estado mediante fotogramas más frecuentes.

## 2. Arquitectura y responsabilidades

```text
Jugador (teclas ← → ↑ ↓ o botones laterales)
              |
              v
MissionStageV17.tsx  — HUD, vehículo y carretera SVG, mensajes y controles
              |
              v
SimulationCenter.tsx — estado de la misión, temporizadores, rutas, incidencias,
                        decisión de ahorro, pausa, recuperación e informe
        |                                  |
        v                                  v
drivingGameV19.ts                routeDrivingV20.ts / routeDrivingV21.ts
(carriles, peligros y choques)     (ruta por carril, calendario de cruces,
                                   conservación del ahorro)
              |
              v
App.tsx — callbacks que afectan el estado compartido del simulador
        |                              |
        v                              v
Recursos / batería / procesos       Eventos simState / Caja Negra
        |                              |
        v                              v
Paneles del simulador              Puente Streamlit → Python → Supabase*

*Solo cuando configuración, conexión, permisos y confirmaciones lo permiten.
```

Se distingue **estado del minijuego** de **estado de recursos del sistema**:

- El estado del minijuego representa carril, obstáculos y contadores de impactos/esquivas.
- Los valores de CPU, RAM, batería y procesos son los del modelo compartido; no hay un contador ficticio independiente creado únicamente para la pantalla de conducción.
- El puente Streamlit y el kernel Python forman parte de la arquitectura general. No debe afirmarse que cada cambio de carril ejecute directamente una instrucción del kernel Python: el evento nace en React y su integración posterior depende del flujo de la aplicación.

## 3. Archivos y funciones que se deben conocer

| Archivo | Funciones, componentes o responsabilidad |
|---|---|
| `web/src/simulation/drivingGameV19.ts` | `newDrivingGame`, `steerDrivingGame`, `advanceDrivingGame`, `lanePosition`, `hazardCaption`. Motor puro y determinista. |
| `web/src/simulation/routeDrivingV20.ts` | `routeIndexFromLane`. Calcula qué opción de ruta corresponde al carril elegido. También conserva funciones de calendario V20, **superadas por V21 en la misión vigente**. |
| `web/src/simulation/routeDrivingV21.ts` | `JUNCTION_MINUTES_V21`, `nextJunctionMinute`, `isRouteJunctionDue`, `minutesToDrivingForkV21`, `forkVisibleWhileDrivingV21`, `preserveEnergySavingOnIgnore`. |
| `web/src/components/SimulationCenter.tsx` | Coordina el juego: estado, avance, `choose`, cruces automáticos, ahorro elegido, incidentes, reanudación y cierre de misión. |
| `web/src/components/MissionStageV17.tsx` | Dibuja carretera, coche y peligros en SVG; escucha teclado y muestra telemetría, rutas próximas, ahorro activo e incidentes. El nombre del archivo es heredado, pero incluye funciones V21. |
| `web/src/App.tsx` | Integra callbacks `onGameBatteryLoss` / `onGameEvent` con la batería y eventos del modelo compartido; procesa acciones de escenario como `power_save`. |
| `web/src/main.tsx` | Importa las hojas CSS acumuladas de V19, V20 y V21. |
| `web/src/v19-minigame.css`, `v20-conduccion.css`, `v21-conduccion.css` | Estilos de conducción, vista previa de los cruces y estado de ahorro. |
| `web/tests/v19.test.cjs`, `v20.test.cjs`, `v21.test.cjs` | Pruebas de motor, correspondencia ruta-carril, calendario de cruces y conservación de políticas. |
| `web/tests/run.cjs` | Incluye esas pruebas en la suite del proyecto. |
| `tools/validar_v21.ps1` | Ejecuta instalación de dependencias frontend, comprobación TypeScript, tests, compilación y regeneración del bundle Streamlit. |
| `tools/build_streamlit_bundle.py` | Integra los recursos generados por Vite en los HTML usados por Streamlit. |
| `Auto/autoos_unified.html` y `Auto/bridge_component/index.html` | Artefactos compilados que deben actualizarse después de modificar React/TypeScript y antes del despliegue. |

**Nota para mantenimiento:** los instaladores `tools/aplicar_v19.py`, `aplicar_v20.py` y `aplicar_v21.py` usan carpetas `.autoos_vXX_payload/` temporales. No son dependencias normales de ejecución; después de instalar, el código operativo está en `web/src/` y en los archivos compilados.

## 4. Funcionamiento de la conducción V19

### 4.1 Estado del minijuego

`DrivingGameState` incluye:

- `lane`: carril **0, 1 o 2** (izquierda, centro, derecha).
- `frame`: contador de actualizaciones del motor de conducción.
- `hazards`: elementos que avanzan desde el horizonte hacia el vehículo.
- `collisions` y `avoided`: impactos y objetos esquivados.
- `nextId`: identificador del siguiente peligro.

El juego comienza en el **carril central**. `steerDrivingGame` suma o resta un carril y limita el resultado al intervalo `[0, 2]`, por lo que no permite salir de la carretera lateralmente mediante el teclado.

### 4.2 Reloj y peligros

`advanceDrivingGame` actualiza los obstáculos aproximadamente cada **120 ms**, siempre que la misión esté activa, autorizada, avanzando y con velocidad y batería suficientes. Los peligros se generan con un patrón **determinista**, útil para repetir pruebas. La velocidad virtual influye en su aproximación.

Los tipos definidos son `obstacle` (objeto físico), `energy` (zona de alto consumo), `camera` (interferencia ADAS) y `cpu` (sobrecarga de procesamiento). Cuando un peligro llega al umbral de encuentro, se compara su carril con el del conductor:

```text
Si carril_del_peligro == carril_del_vehículo:
    registrar colisión
Si no:
    registrar esquiva
```

El juego informa el incidente a `SimulationCenter`. Una colisión activa la parada de seguridad, cambia la velocidad a 0 y reporta un evento crítico. El modelo original V19 aplica penalizaciones didácticas de **8 puntos de batería** para `energy`, **5** para `obstacle` y **3** para `camera` o `cpu`. Si el peligro corresponde a cámara, se comunica una falla ADAS; si corresponde a CPU, se solicita una carga de procesamiento adicional. Esas penalizaciones no representan mediciones de un vehículo real.

Con menos de tres impactos, el usuario puede recuperar la conducción mediante un botón y reanudar a **30 km/h**, siempre que el sistema aún tenga batería y permisos. Tras alcanzar **tres impactos**, debe reiniciar la misión o consultar el informe; no se habilita recuperación normal.

## 5. Cruces sin clics V20 y calendario V21

### 5.1 Correspondencia de carriles y opciones

`routeIndexFromLane(lane, optionCount)` determina la opción sin abrir un cuadro que detenga el juego:

| Cantidad de opciones del escenario | Carril izquierdo (0) | Carril central (1) | Carril derecho (2) |
|---|---|---|---|
| 2 opciones | Opción 1 | Opción 1 | Opción 2 |
| 3 opciones | Opción 1 | Opción 2 | Opción 3 |

La pantalla muestra el nombre de cada opción, el carril que la elige y cuál está seleccionado en ese instante. **No es un control de carreteras físicas**: es una decisión de escenario representada por la posición del automóvil virtual.

### 5.2 Calendario final V21

En V21 se utiliza `JUNCTION_MINUTES_V21 = [8, 16]`:

| Minutos virtuales | Acción |
|---|---|
| 0–5 | Conducción normal, obstáculos y eventos. |
| 6–8 | Aviso anticipado del primer cruce; el conductor elige carril. |
| 8 | El sistema aplica automáticamente la primera decisión. |
| 9–13 | Continúa la conducción; no se generan nuevos cruces obligatorios. |
| 14–16 | Aviso anticipado del segundo cruce. |
| 16 | Aplica automáticamente la segunda decisión. |
| 17–20 | Trayecto final sin tercer cruce. |
| 20 | Se completa la misión si sigue en marcha y se cumplen las condiciones de cierre. |

`nextJunctionMinute` obtiene el siguiente cruce por índice y devuelve `null` cuando ya se realizaron los dos. `isRouteJunctionDue` determina si el tiempo alcanzó el cruce. `forkVisibleWhileDrivingV21` controla su aviso visual. Una referencia de control evita volver a ejecutar el mismo cruce a causa de renderizados repetidos.

**Decisión de diseño importante:** el contador de cruces `routeChoices` es **independiente** de la longitud del informe de decisiones. Por tanto, una intervención técnica registrada no adelanta otro cruce. La misión reinicia `routeChoices` al comenzar una partida nueva.

## 6. Persistencia del ahorro extremo V21

### 6.1 Caso que motivó el cambio

En el escenario de **batería crítica**, el usuario elegía `power_save` y la aplicación activaba el ahorro extremo. Al llegar al siguiente cruce, seleccionar `ignore` («Continuar sin cambios») podía causar una penalización y una parada propias de la lógica anterior, como si ninguna medida de protección hubiera sido aplicada.

La regla corregida es: **«Continuar sin cambios» conserva las políticas activas; no significa apagarlas.**

### 6.2 Comprobación de la política

`preserveEnergySavingOnIgnore(...)` solo permite la excepción si, a la vez:

1. El escenario es `battery`.
2. La acción es `ignore`.
3. El usuario ya había elegido explícitamente `power_save` en esta misión.
4. El modelo compartido de batería sigue indicando modo de ahorro.
5. El nivel de batería es válido y superior a cero.

Si todas son verdaderas, `SimulationCenter.choose` conserva la política, registra la decisión y emite un evento informativo **sin aplicar otra penalización de 6 puntos ni obligar a detener la conducción** por esa elección. El HUD muestra `AHORRO EXTREMO ACTIVO`.

Si alguna condición falla, no se aplica esa excepción: se mantiene la lógica normal del escenario correspondiente. En particular, **la regla no impide detenerse por batería agotada, colisiones u otras fallas críticas**.

`powerSaveActive` registra que el usuario activó la protección durante la misión actual y se reinicia al comenzar otra. La efectividad del ahorro no se supone por ese indicador por sí solo: también se comprueba `battery.isLowBatteryMode`.

### 6.3 Consumo y limitaciones

El modo de ahorro no recarga mágicamente la batería ni garantiza que alcance para todo el recorrido. Las métricas energéticas continúan calculándose en el modelo general (tracción, procesos, periféricos y servicios restantes). El nivel de batería puede seguir bajando; al llegar a cero corresponde una parada de seguridad.

## 7. Relación con conceptos de sistemas operativos

| Concepto | Evidencia visible y conexión al código |
|---|---|
| **Gestión de procesos** | Las acciones de escenario, como `power_save`, pueden suspender tareas multimedia o de confort mediante el motor compartido de AutoOS. |
| **Planificación de CPU** | Un incidente de CPU puede solicitar carga adicional; los cambios de procesos y las métricas se consultan en el panel del planificador. |
| **Gestión de memoria** | El HUD muestra RAM física estimada a partir de los procesos admitidos en el simulador; el minijuego no inventa RAM propia. |
| **Gestión energética** | El BMS virtual mantiene porcentaje de batería y modo de ahorro; colisiones o decisiones pueden modificar el nivel o la política. |
| **Administración de dispositivos** | Una interferencia de cámara puede generar la falla del dispositivo frontal ADAS. |
| **Seguridad / control de acceso** | La UI restringe el laboratorio técnico según el rol; en la escena se indica autorización de Mecánico/Administrador. Los permisos reales de backend se validan aparte. |
| **Auditoría** | `handleSimulatorGameEvent` añade eventos `[MINIJUEGO]` al estado de simulación React; Caja Negra puede sincronizarlos por el puente existente. |

**Cadena de una colisión:** `advanceDrivingGame` detecta coincidencia de carril → `SimulationCenter` activa parada, penalización y aviso → `App.tsx` modifica batería o procesos y agrega evento `[MINIJUEGO]` → los paneles muestran el estado actualizado → Caja Negra administra el envío y sus confirmaciones cuando hay servicio remoto.

**Cadena de una decisión de ahorro:** carril elegido → `routeIndexFromLane` → `SimulationCenter.choose('power_save')` → `App.handleSimulatorAction` y reglas del modelo → batería/estado de tareas compartidos → HUD e historial. En el segundo cruce, `preserveEnergySavingOnIgnore` conserva la política cuando se cumplen sus precondiciones.

## 8. Pruebas realizadas y pruebas todavía necesarias

### 8.1 Verificaciones automáticas confirmadas en el entorno local del proyecto

El comando ejecutado fue:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\validar_v21.ps1
```

La salida compartida de la validación confirmó:

- `npm run lint`: comprobación TypeScript aprobada.
- `npm run test:sim`: pruebas anteriores del simulador y pruebas V19, V20 y V21 aprobadas.
- V19: carriles, límites, perspectiva, aparición de peligros, esquiva, colisiones y eventos únicos.
- V20: opciones por carril, anticipación y ausencia de clics obligatorios.
- V21: cruces en minutos 8 y 16 y conservación de ahorro activo cuando corresponde.
- `vite build`: compilación de producción terminada.
- Regeneración de `Auto/autoos_unified.html` y `Auto/bridge_component/index.html` completada.

Los avisos de tamaño de bundle y de scripts de instalación de `esbuild` no bloquearon esa compilación. Estas pruebas **no prueban por sí solas** una escritura remota en Supabase ni garantizan ausencia de errores en todos los navegadores.

### 8.2 Pruebas manuales de aceptación antes de entrega

- [ ] Iniciar la misión en el rol permitido y controlar carril/velocidad con las flechas.
- [ ] Comprobar que los peligros se aproximan, se pueden esquivar y una colisión detiene el vehículo.
- [ ] Recuperar la conducción a 30 km/h tras un choque permitido.
- [ ] Comprobar que los avisos ocurren alrededor de los minutos 6 y 14 y las decisiones a los minutos 8 y 16, **sin clics de selección**.
- [ ] En batería crítica, elegir `power_save` en el primer cruce y `ignore` en el segundo; verificar que el ahorro permanece y no aparece una parada injustificada.
- [ ] Completar el minuto 20, revisar informe y eventos en Caja Negra.
- [ ] Verificar conexión y persistencia remota de eventos en Supabase, si se presentará esa función.
- [ ] Probar un rol sin permiso técnico y comprobar que el laboratorio no queda habilitado indebidamente.
- [ ] Abrir la **versión desplegada en Streamlit Cloud** y verificar que tiene el mismo comportamiento que la versión local.

El desarrollador informó haber probado el minijuego V21 en navegador y estar satisfecho con el resultado. No hay constancia en esta guía de verificación independiente completa del despliegue público ni de sincronización remota.

## 9. Compilación, publicación y archivos que no se deben incluir

**Estructura requerida:** situarse en la carpeta principal con `app.py`, `Auto/`, `web/`, `tools/` y `docs/`; no trabajar en el `AutoOS/` duplicado ni en `AutoOS_1/` por error.

Para volver a compilar y generar el contenido que consume Streamlit:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\validar_v21.ps1
```

Para ejecutar localmente, con las dependencias instaladas en el entorno correcto:

```powershell
.\.venv\Scripts\python.exe -m streamlit run .\app.py
```

Para publicar, se deben revisar los archivos con `git status`, incluir código, pruebas, documentación y **ambos** HTML generados. Si el código `.tsx` se actualiza pero los HTML del puente no se incorporan al commit, Streamlit Cloud puede mostrar la versión anterior.

**No agregar sin revisión:** `.autoos_vXX_backup/`, `.autoos_vXX_payload/`, `AutoOS/` anidado, `.venv/`, `node_modules/`, `dist/`, archivos de secretos, tokens, `.env` o credenciales de Supabase. Las carpetas `.autoos_vXX_payload/` son material de instalación, no código fuente necesario para ejecutar una V21 ya instalada.

Revisar el resultado en la rama de trabajo, abrir Pull Request contra la rama de despliegue y comprobar el merge. El repositorio remoto puede estar configurado para desplegar `main`; no debe asumirse que subir una rama de características actualiza inmediatamente la web pública.

## 10. Preguntas frecuentes para la sustentación

**¿Por qué no se detiene el juego en cada cruce?** Porque el propósito de la experiencia interactiva es conducir. El conductor decide por carril y el escenario se resuelve automáticamente cuando llega al minuto programado.

**¿Por qué solo hay dos cruces?** Para distribuir dos decisiones relevantes en una misión de 20 minutos sin interrumpir continuamente la conducción y sin que otras intervenciones técnicas generen cruces extra.

**¿Cómo se evita repetir una decisión?** El calendario V21 usa un contador de cruces dedicado y una referencia que marca el cruce procesado. Así la reejecución de efectos de React no debería duplicar la misma elección.

**¿Por qué el ahorro se mantiene aunque se elija «Continuar sin cambios»?** Porque esa acción no equivale a desactivar una política previamente autorizada. La excepción se aplica solo si fue elegida expresamente y continúa activa en el estado real de batería del simulador.

**¿Qué pasaría si la batería llega a 0 %?** El ahorro no evita la falta total de energía: la simulación se detiene y muestra el estado de agotamiento.

**¿Por qué existe `drivingGameV19.ts` por separado?** Para aislar reglas deterministas del navegador y de React, facilitando pruebas reproducibles y separación entre lógica del juego y presentación.

**¿Se está usando la CPU real del computador o la RAM real del automóvil?** No. Son métricas de un modelo didáctico, calculadas por los módulos del sistema. No constituyen telemetría física.

**¿Cada colisión queda automáticamente en Supabase?** Queda registrada como evento en el modelo React. La sincronización remota requiere que el puente, permisos, credenciales, conexión y confirmaciones funcionen; debe validarse por separado.

---

### Referencias internas del proyecto

- `docs/V19_MINIJUEGO_CONTROLES_Y_SISTEMA_OPERATIVO.md`
- `docs/V20_CONDUCCION_SIN_CLIC.md` (**histórico:** documenta el calendario de cruces anterior a V21)
- `docs/V21_POLITICAS_Y_CRUCES.md`
- `docs/MANUAL_AUTOOS_V18.pdf` (arquitectura general previa)
- Código fuente `web/src/`, pruebas `web/tests/` y compilador `tools/build_streamlit_bundle.py`

**Versión vigente de la conducción: V21.** Ante diferencias entre documentos históricos, tomar como referencia el código fuente V21 y sus pruebas.
