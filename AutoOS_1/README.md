# AutoOS — Módulo de Procesos y CPU (Copia Compartible)

> **Simulación Académica de un Sistema Operativo para Vehículo Autónomo Inteligente**  
> **Responsable (Integrante 1):** Módulo del Núcleo — PCB, CPU Uniprocesador, Planificador por Prioridad y Motor de Simulación por Ciclos Discretos.

---

## 1. Descripción del Proyecto y Alcance

**AutoOS** es un simulador académico diseñado para modelar los mecanismos fundamentales de un sistema operativo en tiempo real embebido en un vehículo inteligente. 

El presente repositorio contiene la entrega completa e independiente del **Módulo de Procesos y CPU**, desarrollado por el **Integrante 1**. Este módulo implementa la lógica central del sistema operativo con las siguientes capacidades:

1. **Modelado riguroso del Bloque de Control de Procesos (PCB):** Gestión de identificadores PID únicos, nombres descriptivos de tareas vehiculares, prioridades y tiempos de ráfaga (*burst time*).
2. **Máquina de estados finitos estricta:** Validación de transiciones formales entre los estados `NEW`, `READY`, `RUNNING`, `WAITING` y `TERMINATED`.
3. **CPU uniprocesador con exclusión mutua:** Ejecución de a lo sumo un proceso por ciclo de CPU, garantizando que ninguna tarea interfiera indebidamente con otra.
4. **Planificador por prioridad con desempate FIFO:** Selección determinista basada en prioridad numérica (1 = prioridad crítica de seguridad, 5 = prioridad baja de confort) y orden de llegada para empates.
5. **Motor de simulación coordinado (`SimulationEngine`):** Control del reloj lógico (*ticks*), admisión automática o manual, pausas, reanudaciones, bloqueos de E/S vehicular, desbloqueos y cancelación forzada (*abort*).
6. **Bitácora de auditoría histórica (`EventLogger`):** Registro cronológico inmutable de todos los eventos relevantes del sistema.
7. **Capa de integración desacoplada (DTOs y `AutoOSService`):** Fachada de alto nivel que entrega datos 100% serializables a JSON, lista para conectarse directamente con el Dashboard web (Integrante 2), APIs REST (FastAPI) y bases de datos en la nube (Supabase).

---

## 2. Estructura del Proyecto

El código está organizado siguiendo principios de arquitectura limpia y separación de responsabilidades:

```text
AutoOS_COMPARTIR/
├── .gitignore                      # Configuración de exclusión para Git y Python
├── README.md                       # Documentación técnica integral del módulo
├── src/                            # Código fuente del núcleo y servicios
│   ├── __init__.py                 # Exportación de la API pública del paquete
│   ├── core/                       # Núcleo del sistema operativo
│   │   ├── __init__.py
│   │   ├── process_state.py        # Enum ProcessState y matriz VALID_TRANSITIONS
│   │   ├── exceptions.py           # Jerarquía de excepciones de dominio (AutoOSError)
│   │   ├── process.py              # Entidad Process (PCB y máquina de estados)
│   │   ├── cpu.py                  # Entidad CPU (uniprocesador y consumo de ticks)
│   │   ├── scheduler.py            # Planificador por prioridad y cola FIFO
│   │   ├── event_logger.py         # Registro cronológico de eventos del sistema
│   │   └── simulation.py           # Motor de simulación y orquestación
│   ├── dto/                        # Objetos de Transferencia de Datos
│   │   ├── __init__.py
│   │   └── dtos.py                 # ProcessDTO, CPUDTO, SchedulerDTO, EventDTO, SystemStatusDTO
│   └── services/                   # Capa de servicio de aplicación
│       ├── __init__.py
│       └── auto_os_service.py      # Fachada AutoOSService (consumo para frontend/API)
└── tests/                          # Suite completa de pruebas automatizadas
    ├── __init__.py
    ├── test_process.py             # Pruebas unitarias de Process y estados
    ├── test_cpu.py                 # Pruebas unitarias de CPU y exclusión mutua
    ├── test_scheduler.py           # Pruebas unitarias del Scheduler y ordenamiento
    ├── test_simulation.py          # Pruebas unitarias del SimulationEngine
    ├── test_service.py             # Pruebas de integración de AutoOSService y DTOs
    └── test_audit_edge_cases.py    # Pruebas de estrés y casos de borde de auditoría
```

---

## 3. Requisitos del Sistema

- **Python:** Versión **3.10** o superior (probado y verificado en Python 3.10, 3.11, 3.12, 3.13 y 3.14).
- **Dependencias externas:** **Cero (0) dependencias de terceros.** El módulo utiliza exclusivamente la biblioteca estándar de Python (`dataclasses`, `enum`, `typing`, `json`, `unittest`).
- **Sistema operativo:** Compatible con Windows, macOS y Linux.

---

## 4. Instrucciones para Abrir y Ejecutar

### Opción A: Visual Studio Code

1. Descomprime la carpeta `AutoOS_COMPARTIR.zip` en tu equipo.
2. Abre Visual Studio Code.
3. Ve al menú superior: **Archivo (File) > Abrir carpeta... (Open Folder...)**.
4. Selecciona la carpeta raíz `AutoOS_COMPARTIR`.
5. Abre una terminal integrada con ``Ctrl + ` `` o desde el menú **Terminal > Nueva terminal**.

### Opción B: Terminal o Consola del Sistema

Abre tu terminal favorita (PowerShell, Command Prompt o Bash) y navega a la raíz del proyecto:

```bash
cd ruta/hacia/AutoOS_COMPARTIR
```

---

## 5. Comprobación y Pruebas Automatizadas

El proyecto cuenta con una cobertura completa de pruebas automatizadas utilizando `unittest`.

### A. Ejecución de la Suite Completa de Pruebas

Ejecuta el siguiente comando desde la raíz del proyecto:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

*Resultado esperado:* **61 pruebas aprobadas con estatus `OK`**, sin fallos ni errores.

### B. Verificación de Compilación y Sintaxis

Para verificar que todos los archivos compilan limpiamente sin errores de sintaxis ni de tipos en tiempo de compilación:

```bash
python -m compileall -q src tests
```

*Resultado esperado:* Código de salida `0` sin advertencias ni errores.

### C. Verificación Rápida de Importación

Para comprobar que el paquete se importa y se inicializa correctamente:

```bash
python -c "from src import AutoOSService; s = AutoOSService(); print('AutoOS listo. Estado inicial:', s.get_system_status()['is_paused'])"
```

---

## 6. Componentes Principales de la Arquitectura

### 1. `Process` (Bloque de Control de Procesos - PCB)
Modela una tarea vehicular individual (`src/core/process.py`).
- **Atributos:** `pid` (único, auto-incremental o asignado), `name`, `priority` (1 a 5), `state` (`ProcessState`), `burst_time` (ciclos requeridos) y `remaining_time` (ciclos pendientes).
- **Control de estados:** Solo permite transiciones explícitas válidas según `VALID_TRANSITIONS` (`admit()`, `dispatch()`, `preempt()`, `block()`, `unblock()`, `terminate()`).
- **Métricas:** Calcula automáticamente `is_finished`, `executed_time` y porcentaje de avance.

### 2. `CPU` (Uniprocesador con Exclusión Mutua)
Modela el núcleo de procesamiento físico (`src/core/cpu.py`).
- **Exclusión mutua:** Rechaza con `CPUBusyError` cualquier intento de cargar un proceso si la CPU ya se encuentra ocupada.
- **Validación de estado:** Solo acepta procesos en estado `READY`. Al cargarlo (`load_process`), efectúa la transición legal a `RUNNING`.
- **Ciclos de ejecución:** El método `tick()` ejecuta un ciclo del proceso activo, reduce su tiempo restante y, si finaliza, lo libera automáticamente dejándolo en `TERMINATED`.
- **Métricas:** Registra `total_ticks`, `busy_ticks`, `idle_ticks` y el porcentaje de uso de CPU.

### 3. `Scheduler` (Planificador por Prioridad)
Administra la cola de procesos listos (`src/core/scheduler.py`).
- **Criterio de ordenamiento:** Prioridad estricta (prioridad numérica menor = mayor urgencia).
  - *Prioridad 1:* Frenado de emergencia / Airbag (Crítica).
  - *Prioridad 2:* Control de aceleración y dirección.
  - *Prioridad 3:* Monitoreo de sensores de proximidad (Por defecto).
  - *Prioridad 4:* Telemetría y diagnóstico de batería.
  - *Prioridad 5:* Sistema de infoentretenimiento / Climatización (Baja).
- **Desempate:** FIFO estricto mediante contador de admisión determinista.
- **Integridad:** Rechaza duplicados en cola y valida que solo ingresen procesos en estado `READY`.

### 4. `SimulationEngine` (Motor de Simulación)
Orquesta el ciclo de vida global del sistema (`src/core/simulation.py`).
- Mantiene el reloj lógico global (`current_tick`).
- Coordina la CPU, el Scheduler y el registro central de todos los procesos.
- Controla el despacho no apropiativo (si la CPU está libre, extrae el siguiente proceso del Scheduler y lo despacha).
- Gestiona bloqueos por eventos de E/S (`block_current_process`), desbloqueos (`unblock_process`) y abortos forzados de procesos (`abort_process`, admitiendo cancelar procesos incluso en estado `NEW`).

### 5. `EventLogger` (Bitácora de Auditoría)
Registra eventos inmutables estructurados (`src/core/event_logger.py`).
- Cada evento almacena: `event_id`, `tick`, `timestamp`, `event_type`, `pid`, `process_name` y `description`.
- Permite filtrado por PID y por tipo de evento.

### 6. DTOs (Data Transfer Objects)
Modelos inmutables y desacoplados (`src/dto/dtos.py`).
- `ProcessDTO`, `CPUDTO`, `SchedulerDTO`, `EventDTO` y `SystemStatusDTO`.
- Convierten las entidades del dominio en estructuras puras de datos con métodos `.to_dict()` para serialización JSON inmediata.

### 7. `AutoOSService` (Fachada de Aplicación)
Punto de entrada principal para consumidores externos (`src/services/auto_os_service.py`).
- Encapsula toda la complejidad del motor de simulación.
- Expone únicamente estructuras de datos serializables (diccionarios y cadenas JSON), protegiendo los objetos internos de mutaciones accidentales desde el exterior.

---

## 7. Ejemplo Práctico de Uso (`AutoOSService`)

El siguiente script en Python demuestra cómo inicializar el simulador, crear procesos de distinta prioridad, avanzar ciclos de reloj, consultar el estado del sistema e inspeccionar la bitácora:

```python
from src import AutoOSService

# 1. Instanciar el servicio
service = AutoOSService()

# 2. Registrar procesos vehiculares simulados
# Proceso 1: Telemetría general (prioridad baja = 4, duración = 3 ticks)
p_telemetry = service.create_process(name="Telemetria_Bateria", priority=4, burst_time=3)

# Proceso 2: Freno de emergencia (prioridad crítica = 1, duración = 2 ticks)
p_brake = service.create_process(name="Freno_Emergencia_ABS", priority=1, burst_time=2)

# Proceso 3: Infoentretenimiento (prioridad baja = 5, duración = 1 tick)
p_radio = service.create_process(name="Radio_Multimedia", priority=5, burst_time=1)

print(f"Proceso creado: PID={p_brake['pid']}, Nombre={p_brake['name']}, Prioridad={p_brake['priority']}")

# 3. Avanzar un ciclo de simulación (Tick 1)
# El Scheduler despachará primero a Freno_Emergencia_ABS por tener prioridad 1
step_1 = service.step()
print(f"Tick actual: {step_1['current_tick']}")
print(f"Proceso en CPU: {step_1['cpu']['current_process']['name']}")

# 4. Avanzar otro ciclo (Tick 2) - El freno completa sus 2 ticks y finaliza
step_2 = service.step()
print(f"Tick actual: {step_2['current_tick']}")

# 5. Ejecutar una ráfaga de 3 ciclos continuos
run_res = service.run_cycles(cycles=3)
print(f"Ciclos ejecutados: {run_res['executed_cycles']}, Tick acumulado: {run_res['current_tick']}")

# 6. Consultar la instantánea completa del sistema (formato diccionario o JSON)
status = service.get_system_status()
print(f"Total de procesos en el sistema: {status['total_processes']}")
print(f"Uso de CPU: {status['cpu']['usage_percentage']}%")
print(f"Procesos listos en cola: {len(status['scheduler']['ready_queue'])}")

# 7. Consultar eventos de auditoría registrados
eventos = service.get_events(limit=5)
print("\nÚltimos 5 eventos registrados:")
for ev in eventos:
    print(f" - [Tick {ev['tick']}] {ev['event_type']}: {ev['description']}")
```

---

## 8. Decisiones de Diseño y Limitaciones Conocidas

Para garantizar la coherencia académica y técnica del módulo, se tomaron las siguientes decisiones:

1. **Planificación No Apropiativa (*Non-preemptive*):**  
   Una vez que un proceso ingresa a la CPU, conserva el procesador hasta completar su tiempo de ráfaga (*burst time*), pasar a espera de E/S (`WAITING`) o ser abortado explícitamente. No es desalojado automáticamente solo por la llegada de un proceso de mayor prioridad.
2. **Escala de Prioridades:**  
   Se utiliza el estándar clásico de sistemas operativos donde un valor numérico menor denota mayor prioridad:
   - **1:** Máxima prioridad (procesos críticos).
   - **5:** Mínima prioridad (procesos no críticos).
3. **Memoria Volátil en Ejecución:**  
   El estado del sistema se mantiene en memoria principal durante la vida de la instancia de `AutoOSService` o `SimulationEngine`. La persistencia física es responsabilidad de la capa adaptadora hacia Supabase.
4. **Reloj Lógico Discreto:**  
   El avance temporal ocurre en unidades discretas denominadas *ticks*. No depende del reloj en tiempo real del procesador anfitrión, lo que garantiza simulaciones 100% deterministas y reproducibles.

---

## 9. Guía de Integración para el Dashboard (Integrante 2)

El módulo está diseñado bajo el patrón **Fachada (Facade)** para integrarse de forma transparente con el dashboard web y la capa de servicios:

### Conexión con FastAPI
Para exponer el simulador a través de endpoints REST o WebSockets, basta con instanciar `AutoOSService` en el backend de FastAPI:

```python
# Ejemplo en backend/main.py de FastAPI
from fastapi import FastAPI
from src import AutoOSService

app = FastAPI(title="AutoOS Vehicle API")
service = AutoOSService()

@app.get("/api/system/status")
def get_status():
    return service.get_system_status()

@app.post("/api/simulation/tick")
def execute_tick():
    return service.step()

@app.post("/api/processes")
def create_process(name: str, priority: int = 3, burst_time: int = 1):
    return service.create_process(name=name, priority=priority, burst_time=burst_time)
```

### Persistencia en Supabase
Los diccionarios devueltos por `service.get_system_status()`, `service.get_all_processes()` y `service.get_events()` coinciden exactamente con esquemas tabulares relacionales:
- **Tabla `processes`:** Mapeable directamente desde los campos de `ProcessDTO` (`pid`, `name`, `priority`, `state`, `burst_time`, `remaining_time`).
- **Tabla `events`:** Mapeable directamente desde los campos de `EventDTO` (`id`, `tick`, `timestamp`, `event_type`, `pid`, `process_name`, `description`).
- **Tabla `cpu_metrics`:** Mapeable desde los campos de `CPUDTO` (`is_idle`, `total_ticks`, `busy_ticks`, `idle_ticks`, `usage_percentage`).

---

## 10. Resumen de Calidad y Verificación

| Métrica / Aspecto | Valor / Estado |
| :--- | :--- |
| **Archivos fuente (`src/`)** | 13 módulos Python |
| **Archivos de pruebas (`tests/`)** | 7 módulos de prueba |
| **Total de pruebas unitarias** | **61 pruebas aprobadas (100% OK)** |
| **Dependencias externas** | **0 (Solo biblioteca estándar)** |
| **Compatibilidad** | Python 3.10+ |
| **Estado para entrega** | **Listo para comprimir en `.zip` y compartir** |

---

## 3. Nuevas Implementaciones de Planificación y Simuladores

Se han incorporado los algoritmos formales de planificación de CPU requeridos para AutoOS:

### 3.1 Algoritmos de Planificación Implementados
1. **FCFS (First-Come, First-Served):**
   - Política no apropiativa estricta por tiempo de llegada.
   - Demuestra el fenómeno del *efecto convoy* en sistemas embebidos.
2. **Round Robin (RR):**
   - Planificación circular con Quantum de tiempo configurable ($q = 1, 2, 3, 4, 5$).
   - Desalojo periódico y reencolamiento al final de la cola para garantizar equidad.
3. **Priority Scheduling (No Apropiativo y Apropiativo / Preemptive):**
   - Selección por min-heap basada en prioridad numérica (1 = Crítica ASIL-D, 5 = Muy Baja).
   - En modo apropiativo (*preemptive*), cualquier proceso de mayor prioridad desaloja inmediatamente al proceso en CPU.

### 3.2 Simuladores de Contingencia Vehicular
- **Simulador de Batería Baja:**
  - Detecta niveles de reserva energética $< 20\%$.
  - Suspende dinámicamente procesos de confort e infoentretenimiento para ahorrar potencia.
  - Eleva la prioridad del sistema de frenado regenerativo y gestión térmica (BMS).
- **Simulador de Proceso Crítico (ASIL-D):**
  - Inyección en tiempo real de tareas de emergencia (ej. *Frenado Autónomo de Emergencia - AEB*, *Sensor de Colisión Airbag*).
  - Fuerza el desalojo inmediato (*preemption*) del proceso actual en CPU y registra el cambio de contexto (*context switch*).

### 3.3 Representación Visual
- Diagrama de Gantt interactivo con traza temporal continua.
- Métricas en tiempo real: Tiempo de Espera promedio ($WT$), Tiempo de Retorno promedio ($TAT$) y Porcentaje de Utilización de CPU.
