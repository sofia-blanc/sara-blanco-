# AutoOS V9 — Simulación integrada de recursos

## Qué demuestra

El objetivo es que un escenario afecte **la misma instancia del motor React**
que usan los módulos Simulación, Planificador y la banda de telemetría de Conducción.
No son tres paneles con números independientes.

| Entrada | Respuesta del motor | Evidencia en la interfaz |
|---|---|---|
| Escenario CPU | Crea un proceso pesado con PID y demanda de RAM | Aparece PID, RAM reservada, CPU solicitada y consumo en W |
| Suspender multimedia | Cambia estado a SUSPENDIDO y sale de la cola | Disminuye RAM ocupada, demanda y potencia del SO |
| Proceso extra | La demanda de RAM puede superar 2048 MB | RAM llena y SWAP estimada (no SWAP Python real) |
| Arrancar viaje | Cada segundo de demostración equivale a **1 minuto virtual** | Batería disminuye, aumentan Wh de la sesión y km recorridos |
| Reducir velocidad | Reduce energía calculada de tracción | Baja la potencia instantánea y la tasa de descarga |
| Falla de sensor | Cambia estado del dispositivo y agrega diagnóstico al scheduler | Fallas, eventos y procesos muestran el efecto |
| Fin de procesos | CPU continúa en espera mientras el vehículo circula | Tick, Gantt ocioso, consumo de batería sin trabajo CPU |

## Arquitectura: cuál es la fuente de los datos

```
SimulationCenter (acciones del usuario)
        |
        v
App.tsx (SimulationState + BatteryState + VehicleDevice[])
        |          |                |
        |          |                +--> estados de dispositivos
        |          +-------------------> descarga calculada por tick
        +------------------------------> cola, Gantt y procesos
        |
        v
simulation/resources.ts (cálculos puros)
        |
        +--> OSResourceMonitor en Simulación
        +--> OSResourceMonitor compacto en Planificador
        +--> OSResourceMonitor compacto en Conducción
        +--> Informe final y bitácora
```

`OSResourceMonitor.tsx` es solo presentación. No contiene contadores ni genera datos.

## Cálculos para explicar al profesor

- **RAM:** suma de `memoryMb` de procesos admitidos (LISTO, EJECUTANDO y BLOQUEADO).
  NUEVO no reserva; TERMINADO y SUSPENDIDO liberan la reserva **en el modelo didáctico**.
  RAM física = `min(RAM demandada, 2048 MB)`; SWAP solicitada = `max(0, demanda - 2048)`.
- **CPU solicitada:** suma de `cpuUsagePct` de los procesos admitidos; puede superar
  100 %, expresando saturación. **CPU utilizada:** tiempo ocupado del Gantt / ticks
  ejecutados; es una métrica distinta.
- **Energía:** potencia estimada = tracción + procesos + dispositivos + auxiliares.
  Para cada minuto virtual, Wh = W / 60. Nivel de batería = nivel anterior -
  `Wh * 100 / 32000` (pack supuesto de **32 kWh**).
- **Historia:** una muestra por tick y una gráfica corta de 60 muestras máximo;
  los cambios en la misma unidad de tiempo actualizan su muestra.
- **Registros:** el informe final compara CPU, RAM, SWAP, batería y energía consumida.

Los coeficientes de W son **supuestos educativos**, no mediciones del hardware físico.

## Límite de integración que debe explicarse con honestidad

**El kernel Python de `AutoOS_1` y el motor TypeScript de `web` todavía son dos
motores separados.** La V9 **integra de verdad** Simulación, Planificador y
Conducción **dentro del frontend React**, pero no envía comandos al kernel Python.

Streamlit carga React con `components.html(...)` dentro de un iframe; `postMessage`
actualiza información entre iframes del frontend, pero no modifica `st.session_state`
ni ejecuta por sí solo los servicios de `AutoOS_1`.

Para una integración real extremo a extremo, habría que implementar un componente
bidireccional de Streamlit o una API Python con autenticación, autorización,
serialización de eventos y pruebas de concurrencia. **No se ha implementado aquí.**

## Demostración en clase

1. Abrir Simulación > Conducción normal. Observar batería, potencia, CPU y RAM.
2. Iniciar Sobrecarga CPU. Mostrar el nuevo proceso y la subida de demanda.
3. Pasar a Planificador: comprobar que el proceso aparece en la misma cola.
4. Regresar a Simulación, suspender multimedia y explicar qué recursos se liberan.
5. Aumentar carga varias veces en Laboratorio libre hasta mostrar SWAP solicitada.
6. Avanzar el viaje, reducir velocidad y observar que baja la descarga por minuto.
7. Generar informe de antes/después, revisar advertencias y su origen.
8. Explicar qué motor es React y cuál es Python: no confundir la representación.

## Pruebas incluidas

- `npm run lint`, `npm run test:sim` (incluye `resources.test.ts`), `npm run build`.
- Reconstrucción HTML con `python tools/build_streamlit_bundle.py`.
- 130 pruebas Python con unittest (no se modifica el kernel).

**Por qué no sobrescribimos `Auto/app.py`:** respeta el trabajo de Supabase y
los componentes Python existentes, y evita falsificar un puente no implementado.
