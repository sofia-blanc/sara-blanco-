# AUTOOS V18 — GUÍA RÁPIDA PARA QUIEN EXPONE

## Qué decir al empezar (35 segundos)

«AutoOS es un **simulador didáctico de sistema operativo vehicular**. Tiene una interfaz React donde elegimos escenarios, rutas y decisiones; un modelo React que calcula procesos, consumo y periféricos; un kernel Python que implementa algoritmos clásicos de SO; y Streamlit como puente hacia ese kernel y Supabase. Una decisión puede modificar prioridades, estado de procesos, batería y velocidad. Los eventos se registran en Caja Negra y se pueden consultar en Supabase».

## El recorrido de demostración

1. **Inicio:** mostrar menú y los siete módulos.
2. **Simulación:** perfil Mecánico → Batería crítica → Iniciar.
3. **Checkpoint:** esperar minuto 5 virtual. Elegir «Continuar sin cambios» → velocidad 0 → advertencia → penalización de 6 puntos de batería (convención didáctica).
4. **Contraste:** reiniciar y seleccionar «Activar ahorro extremo» → se suspenden multimedia/confort en el modelo.
5. **Planificador:** demostrar proceso crítico, ráfagas, prioridad y Gantt.
6. **Panel RTOS:** boot de siete etapas; First-Fit, memoria virtual, terminal.
7. **Caja Negra:** mostrar evento `DISPATCH`/`COMPLETION`, pendientes y confirmados.
8. **Supabase:** mostrar la consulta real a `public.eventos` (sin contraseñas).
9. **Roles:** cambiar a Pasajero y mostrar limitación de acciones técnicas; explicar la segunda verificación en servidor.

## Diagrama que debes repetir de memoria

```text
Jugador → React (SimulationCenter) → App (motor de procesos/energía)
                                       |
                      CPU/RAM/BMS/GPS  +→ Eventos del scheduler/GPS
                                       |
                                Caja Negra (cola)
                                       |
                              Streamlit / Python
                                RBAC y validación
                                       |
                                   Supabase

Kernel Python: subsistema aparte de CPU, memoria, VFS y terminal.
Se comunica por un puente explícito con procesos espejo, no es el mismo scheduler React.
```

## Diez archivos que debes abrir sin perderte

| Código | Respuesta que permite demostrar |
|---|---|
| `web/src/App.tsx` | Quién posee el estado compartido. |
| `web/src/components/SimulationCenter.tsx` | Cómo se inicia una misión y se procesa una decisión. |
| `web/src/components/MissionStageV17.tsx` | Cómo se dibujan los caminos y el auto vectorial V18. |
| `web/src/simulation/engine.ts` | Qué hace cada opción al motor. |
| `web/src/simulation/resources.ts` | Fórmulas y RAM/CPU/batería. |
| `web/src/utils/schedulerEngine.ts` | Cómo avanza un proceso en React. |
| `AutoOS_1/src/core/kernel.py` | El kernel Python y sus siete fases de boot. |
| `AutoOS_1/src/memory/memory.py` | First-Fit y fusión de particiones. |
| `Auto/bridge_react_kernel.py` | Cómo se sincronizan procesos espejo. |
| `Auto/blackbox_cloud_sync.py` | Cómo se validan y confirman los eventos de Supabase. |

## Fórmulas que sí debes saber

- **Potencia virtual:** tracción + procesos + periféricos + auxiliares.
- **Tracción:** `550 + 1,25×velocidad²` (W), multiplicada por factor de clima, si velocidad > 0.
- **Energía por minuto virtual:** `W / 60` Wh.
- **Batería:** `bateríaNueva = max(0, bateríaAnterior – Wh/32000×100)`.
- **RAM React:** `min(2048, suma memoria de procesos admitidos)`.
- **SWAP estimada React:** `max(0, memoria solicitada – 2048)`.
- **Demanda CPU:** suma de demandas de procesos; puede ser >100 %.
- **Ocupación CPU:** `(ticks – ociosos) / ticks × 100`.
- **Checkpoint:** `elapsed >= 5×(decisiones+1)`.
- **Fragmentación:** `(libre – mayor hueco libre) / libre × 100`.

## Respuestas breves que salvan una pregunta difícil

**¿Es un SO real?** Kernel *simulado* escrito en Python, con estructuras reales de SO; no reemplaza al sistema operativo anfitrión ni maneja un automóvil físico.

**¿Por qué dos motores?** React permite interacción ágil; Python demuestra memoria/planificación con objetos independientes. El puente crea procesos espejo por solicitud.

**¿Por qué la RAM no coincide?** React modela 2048 MB; Python usa su propia configuración y reservas First-Fit. Sus PIDs y relojes no son idénticos.

**¿Qué pasa al ignorar?** V18 ejecuta `setSpeed(0)`, `setRunning(false)` y descuenta 6 puntos de batería virtual. Es una penalización de seguridad pedagógica.

**¿Dónde se guarda en nube?** `public.eventos`, mediante cola React, puente Streamlit y `persist_blackbox_batch`.

**¿Por qué RLS?** Una clave configurada no implica permiso de lectura/escritura; Supabase puede bloquear filas o acciones.

**¿Qué ocurre sin internet?** Simulación local sigue funcionando, pero la nube queda pendiente hasta recibir acuse.

**¿Qué protege un botón deshabilitado?** Solo UX. Operaciones de backend requieren comprobación adicional Python y políticas de datos.

**¿Con qué probaron?** En la copia inspeccionada, 151 pruebas Python aprobaron con `PYTHONPATH` ajustado. Las pruebas de navegador y despliegue son adicionales.

**¿Qué mejorarían?** Unificar motores, autenticación real, idempotencia transaccional de eventos, E2E y consolidación de CSS.

## Preguntas al compañero (ensayo oral)

1. Abre el método que cambia una decisión a un efecto de estado.
2. Explica de dónde sale el valor de RAM que ve el jugador.
3. ¿Por qué `MissionStageV17` no usa `setBattery` directamente?
4. ¿Qué ocurre si la conexión de Supabase falla cuando hay seis eventos pendientes?
5. ¿Cómo se impide que un Pasajero llame una operación remota de kernel?
6. ¿Por qué First-Fit puede fragmentar la memoria?
7. ¿Cuál es la diferencia entre FIFO, LRU, FCFS y Round Robin?
8. Si el profesor pide un evento de esta sesión, ¿cómo demuestras que se insertó realmente?
9. Si una página no cambia tras modificar TSX, ¿qué archivo debes recompilar?
10. ¿Por qué no se puede prometer cumplimiento ISO 26262 o funcionamiento en un carro real?

**Regla para contestar:** di **archivo → función → entrada → cambio de estado → efecto observable → límite**. No memorices solo frases; practica encontrando el método exacto.
