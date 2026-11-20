# AUTOOS: SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
# BITÁCORA CONSOLIDADA DE VIBE CODING — EQUIPO DE 4 INTEGRANTES
> **Responsable de Ensamble y Bitácora General:** Integrante 4 (Interfaz e Integración)  
> **Materia:** Sistemas Operativos | **Semestre:** 2026-2  
> **Metodología:** Desarrollo asistido por IA (Vibe Coding con Antigravity)  

---

## 1. INTRODUCCIÓN Y METODOLOGÍA DEL EQUIPO
Para el desarrollo de **AutoOS**, el equipo de 4 integrantes adoptó la metodología de **Vibe Coding**, empleando modelos de lenguaje de última generación para diseño arquitectónico, prototipado rápido de esquemas de bases de datos, generación de código modular y resolución colaborativa de errores técnicos.

Cada integrante documentó sus iteraciones siguiendo la estructura estándar:
- **Prompt:** Instrucción técnica formulada al asistente.
- **Código:** Archivos generados y componentes construidos.
- **Cambios y Errores:** Fallos identificados en compilación, pruebas unitarias o integración.
- **Correcciones:** Soluciones aplicadas para garantizar la estabilidad y seguridad funcional del sistema.

---

## 2. BITÁCORA — INTEGRANTE 1: PROCESOS Y CPU
**Responsabilidad:** Scheduler preventivo, estados de procesos, diagrama Gantt, cálculo de métricas de procesador y puente IPC de kernel.

### Iteración 1.1: Definición del Bloque de Control de Proceso (PCB)
- **Prompt:**
  > *"Diseña la estructura del Bloque de Control de Procesos (PCB) para AutoOS. Debe incluir PID único, nombre del proceso automotriz, estados formales (Nuevo, Listo, Ejecutando, Bloqueado, Terminado), prioridad numérica (0 para Tiempo Real Crítico ASIL-D, hasta 10 para Confort/Ocioso), consumo estimado de CPU y memoria requerida."*
- **Código Generado:**
  Módulo de procesos en `Auto/modules/processes.py`, `AutoOS_1/src/core/process.py` y tabla `procesos` en Supabase.
- **Cambio Realizado:**
  Se agregó la bandera booleana `es_critico` para identificar procesos esenciales para la seguridad del vehículo (ej. `bms_thermal_monitor`, `adas_collision_avoidance`), restringiendo su modificación únicamente al rol Mecánico (Admin).

### Iteración 1.2: Lógica de Planificación y Transición de Estados
- **Prompt:**
  > *"Crea las funciones de transición de estados `cambiar_estado_proceso()` y `finalizar_proceso()`. Si un proceso está en ejecución y se pausa, debe pasar a Bloqueado. Si se reanuda, pasa a Ejecutando. Al finalizar, libera los recursos de CPU asignados."*
- **Error Encontrado:**
  Al calcular el consumo total de CPU en `calcular_uso_cpu_total()`, se estaban sumando procesos en estado "bloqueado" o "listo", distorsionando la carga real del procesador.
- **Corrección Aplicada:**
  Se filtró la agregación de CPU exclusivamente a procesos con `estado == 'ejecutando'`:
  ```python
  return round(sum(p["cpu"] for p in procesos if p["estado"] == "ejecutando"), 1)
  ```

### Iteración 1.3: Planificador Multialgoritmo (FCFS, Round Robin y Prioridad Preemptiva)
- **Prompt:**
  > *"Implementa en `schedulerEngine.ts` y `AutoOS_1/src/core/scheduler.py` tres algoritmos de planificación de CPU: First-Come First-Served (FCFS), Round Robin (con quantum configurable de 1 a 5 segundos) y Prioridad Preemptiva. En Prioridad Preemptiva, si llega un proceso ASIL-D (P1), debe desalojar inmediatamente al proceso en CPU."*
- **Código Generado:**
  `web/src/utils/schedulerEngine.ts` y componentes de cola de listos (`QueueVisualizer.tsx`).
- **Verificación:**
  Simulación paso a paso verificada con ráfagas concurrentes; cuando se inyecta la falla de frenado By-Wire (P1), desaloja al proceso de infoentretenimiento (P5), registrando el evento de preemption en el log.

### Iteración 1.4: Desalojo en Caliente y Serialización hacia el Kernel Bridge
- **Prompt:**
  > *"Conecta el despachador con `kernel_bridge.py`. Serializa cada tick de reloj, contexto de CPU, tiempos de espera (waiting time), retorno (turnaround time) y ráfaga restante para que el frontend React pueda reflejar fielmente las métricas del SO."*
- **Código Generado:**
  `Auto/kernel_bridge.py` y suite de pruebas `AutoOS_1/tests/test_react_kernel_bridge.py`.
- **Corrección Aplicada:**
  Manejo defensivo de valores `None` en tiempos de inicio para procesos que aún se encuentran en la cola de listos.

---

## 3. BITÁCORA — INTEGRANTE 2: MEMORIA, ARCHIVOS Y LOGS
**Responsabilidad:** Gestión de RAM física y virtual, bloques dinámicos, sistema de archivos vehicular y trazabilidad de logs.

### Iteración 2.1: Partición de Memoria Física y Reserva de Kernel
- **Prompt:**
  > *"Modela el subsistema de memoria RAM para AutoOS considerando un hardware automotriz con 16 GB totales (16384 MB). El Kernel RTOS y los drivers críticos deben tener una reserva inmutable de 2048 MB. El resto se asigna dinámicamente según la memoria de los procesos activos."*
- **Código Generado:**
  Módulo `memory_storage.py` con la función `obtener_uso_memoria()`.
- **Verificación:**
  Se confirmó que la suma `kernel_mb + procesos_mb + libre_mb` se mantenga constante e igual a 16384 MB, calculando el porcentaje dinámico de ocupación para alertar si supera el umbral del 85%.

### Iteración 2.2: Jerarquía del Sistema de Archivos Vehicular
- **Prompt:**
  > *"Diseña la estructura de carpetas de almacenamiento para un vehículo inteligente (/config, /logs, /media, /maps, /telemetry) con tamaños típicos, tipos de datos y permisos octales según la sensibilidad."*
- **Código Generado:**
  Colección `obtener_sistema_archivos()` y tabla `archivos` en Supabase.
- **Ajuste Realizado:**
  Se asignaron permisos estrictos `0600` para configuraciones críticas del vehículo (`vehicle_params.json`), accesibles solo por el rol mecánico, y permisos de solo lectura `0444` para pesos de redes neuronales de visión artificial (`adas_network_weights.bin`).

### Iteración 2.3: Paginación Virtual y Algoritmo LRU de Reemplazo
- **Prompt:**
  > *"Implementa en `virtual_memory.py` un modelo de memoria virtual paginada con marcos de página fijos (4 KB), tabla de páginas por proceso, detección de fallos de página (page faults) y política de reemplazo LRU (Least Recently Used)."*
- **Código Generado:**
  `AutoOS_1/src/memory/virtual_memory.py` y `AutoOS_1/tests/test_virtual_memory_paging.py`.
- **Error Encontrado:**
  `AttributeError: 'VirtualMemory' object has no attribute 'swap_free'` al invocar el reporte consolidado de memoria.
- **Corrección Aplicada:**
  Se agregaron propiedades de consulta rápida `swap_free`, `swap_used` y `page_faults_total` garantizando interfaz completa para el monitor del sistema.

### Iteración 2.4: Documentación Técnica de Memoria y Swap NVRAM
- **Prompt:**
  > *"Redacta el documento exhaustivo de arquitectura de memoria y almacenamiento automotriz en `AutoOS_1/docs/MEMORIA_Y_ALMACENAMIENTO.md`. Incluye esquemas de memoria contigua vs paginada, gestión de memoria flash NVRAM para la Caja Negra y mecanismos de protección contra corrupción de datos en caso de corte súbito de alimentación."*
- **Código Generado:**
  Documento técnico de 500+ líneas [`AutoOS_1/docs/MEMORIA_Y_ALMACENAMIENTO.md`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/AutoOS_1/docs/MEMORIA_Y_ALMACENAMIENTO.md).

---

## 4. BITÁCORA — INTEGRANTE 3: SEGURIDAD, DISPOSITIVOS Y RLS
**Responsabilidad:** Modelo RBAC multinivel, políticas Row Level Security (RLS) en Supabase, HAL de 11 dispositivos CAN/Ethernet, telemetría BMS, escenarios de falla ISO 26262 y Caja Negra.

### Iteración 3.1: Esquema Relacional y Protección Referencial
- **Prompt:**
  > *"Diseña el esquema DDL en PostgreSQL/Supabase para AutoOS. Roles (admin, user, guest), catálogo de permisos por módulo, perfiles enlazados a auth.users, dispositivos en buses CAN y Ethernet, tabla de eventos críticos y auditoría para demostrar Autenticación != Autorización."*
- **Error Encontrado:**
  El borrado en cascada (`ON DELETE CASCADE`) eliminaba eventos de auditoría históricos si un perfil era modificado o borrado, destruyendo la evidencia forense requerida por normas automotrices.
- **Corrección Aplicada:**
  Se reemplazó por `ON DELETE SET NULL` en claves foráneas de auditoría y se mantuvieron campos redundantes (`usuario_email`, `rol_nombre`).

### Iteración 3.2: Políticas RLS sin Recursión Infinita
- **Prompt:**
  > *"Configura las políticas RLS en Supabase. Admin tiene control total; Conductor opera funciones normales; Pasajero solo confort. Evita la recursión infinita al leer perfiles."*
- **Error Encontrado:**
  PostgreSQL arrojó: `infinite recursion detected in policy for relation "perfiles"`.
- **Corrección Aplicada:**
  Se definieron funciones `SECURITY DEFINER` y `STABLE` (`fn_obtener_rol_actual()` y `fn_tiene_permiso()`), resolviendo el rol del usuario con privilegios de sistema sin volver a evaluar la política RLS.

### Iteración 3.3: Protocolo de Contingencia en 5 Fases
- **Prompt:**
  > *"Programa en incidents.py los 3 escenarios obligatorios: 1) Sensor LiDAR defectuoso, 2) Batería baja crítica con sobrecalentamiento, 3) Fallo en dirección By-Wire. Cada uno debe ejecutar: 1. Detectar, 2. Registrar, 3. Alertar, 4. Priorizar procesos, 5. Responder."*
- **Error Encontrado:**
  `NameError: name 'Tuple' is not defined` en las anotaciones de retorno.
- **Corrección Aplicada:**
  Se importaron `Tuple`, `Optional` y `Dict` desde la librería estándar `typing`.

### Iteración 3.4: Confirmación Asíncrona Robusta de Eventos en Supabase Cloud (Etapa 13)
- **Prompt:**
  > *"Resuelve el problema de falsos timeouts en la inserción de eventos desde React hacia la tabla `public.eventos` de Supabase Cloud. Utiliza `requestId` único y acuse de recibo explícito `cloud.ack === requestId`."*
- **Código Generado:**
  `docs/ETAPA_13_CONFIRMACION_EVENTOS_SUPABASE.md` e integración en `Auto/bridge_component/index.html`.
- **Verificación:**
  Prueba de escritura y lectura exitosa en `public.eventos` con estado visual CONFIRMADO en UI.

### Iteración 3.5: Caja Negra Automotriz con Persistencia por Lotes (Etapa 14)
- **Prompt:**
  > *"Implementa en `blackbox_cloud_sync.py` y `web/src/cloud/blackboxSync.ts` la sincronización de Caja Negra con Supabase. Almacena eventos en una cola local en el navegador y despacha en lotes de hasta 6 eventos cada 3.5 segundos con desduplicación por `detalles.autoos_id`."*
- **Código Generado:**
  `Auto/blackbox_cloud_sync.py` y `web/src/cloud/blackboxSync.ts`.
- **Verificación:**
  `python AutoOS_1/tests/test_v14_blackbox_cloud_sync.py` confirmó 24 eventos insertados sin duplicidad.

---

## 5. BITÁCORA — INTEGRANTE 4: INTERFAZ, INTEGRACIÓN Y DEPLOY
**Responsabilidad:** Menú cinematográfico, tema Blue Shift, integración Streamlit/React, componentes visuales Plotly, Centro de Simulación y verificación final.

### Iteración 4.1: Diseño del Cockpit y Tema Automotriz
- **Prompt:**
  > *"Diseña una interfaz moderna tipo cabina de control inteligente (Cockpit) en Streamlit con paleta oscura (#0d1117, #1e293b), tacómetros circulares Plotly para CPU, RAM y Batería, banner con semáforo vehicular y conmutador rápido de usuarios en el sidebar para demostración en vivo."*
- **Código Generado:**
  `app.py` y `modules/ui_components.py` con estilos CSS inyectados.

### Iteración 4.2: Integración de Módulos y Detección de Error de Importación
- **Error Encontrado:**
  Al integrar el código entregado por los integrantes, en la línea 309 de `app.py` se invocaba `obtener_dispositivo(x)` para renderizar el selector de dispositivos, pero la función no había sido incluida en la cláusula de importación de `modules.devices`, provocando un fallo en tiempo de ejecución:
  ```text
  NameError: name 'obtener_dispositivo' is not defined
  ```
- **Corrección Aplicada:**
  Se actualizó la importación en `app.py`:
  ```python
  from modules.devices import (
      obtener_dispositivos, obtener_dispositivo, obtener_resumen_dispositivos,
      cambiar_estado_dispositivo, calibrar_dispositivo
  )
  ```

### Iteración 4.3: Implementación de Visualizaciones Avanzadas (Gantt y Barras Apiladas)
- **Prompt:**
  > *"Implementa en la pestaña de Procesos el Diagrama Gantt de planificación de CPU usando plotly.express.timeline con ventanas de tiempo simuladas según el estado de cada proceso. Implementa además el gráfico Donut de distribución por estado y, en la pestaña de Memoria, una gráfica de barras apiladas horizontales (Kernel vs Procesos vs Libre)."*
- **Código Generado:**
  Integración directa en `Auto/app.py` utilizando `plotly.express` y `plotly.graph_objects`.
- **Verificación:**
  Al cambiar el estado de un proceso (ej. pausar `adas_collision_avoidance`), el diagrama Gantt y el gráfico Donut se recalculan automáticamente reflejando la nueva distribución.

### Iteración 4.4: Menú Cinematográfico Inmersivo y Paleta Blue Shift
- **Prompt:**
  > *"Crea `CinematicMenu.tsx` y `blue-shift.css` para una pantalla de bienvenida inmersiva con animaciones de cámara y selección de módulos (Conducción, Simulación, Planificador). Soporta navegación por teclado y clics de ratón sin interferir con el motor de simulación."*
- **Código Generado:**
  `web/src/components/CinematicMenu.tsx`, `web/src/blue-shift.css` y `web/src/cinematic-menu.css`.

### Iteración 4.5: Centro de Simulación de Conducción 2D y Reportes Forenses
- **Prompt:**
  > *"Construye `SimulationCenter.tsx` con 8 modos de simulación interactiva, dinámica de conducción virtual 2D (velocidad, consumo de energía, distancia), telemetría sincronizada y botón para descargar reportes forenses en formato `.txt`."*
- **Código Generado:**
  `web/src/components/SimulationCenter.tsx`, `web/src/simulation/scenarios.ts` y `GUIA_CENTRO_SIMULACION.md`.

### Iteración 4.6: Telemetría Reactiva de RAM / CPU y Calibración OBD-II (Etapa 15)
- **Prompt:**
  > *"Sincroniza la telemetría de memoria RAM y CPU en el Cockpit interactivo y en el planificador RTOS para que reaccione al pausar/reanudar procesos, reproducir multimedia e inyectar fallas. Asegura que el botón de calibración OBD-II restablezca los sensores a estado 100% nominal."*
- **Código Generado:**
  Actualizaciones en `Auto/autoos_interactive.html`, `Auto/autoos_unified.html`, `web/public/autoos_interactive.html` y script `tools/update_memory_telemetry.py`.
- **Verificación:**
  Pruebas de sintaxis con `node --check` con código de salida 0 y validación visual interactiva en tiempo real.

---

## 6. MATRIZ DE TRAZABILIDAD Y ENTREGABLES POR INTEGRANTE

| Integrante | Rol y Especialidad | Módulos Principales | Scripts de Prueba | Documentación |
|---|---|---|---|---|
| **Integrante 1** | Procesos y CPU | `processes.py`, `scheduler.py`, `schedulerEngine.ts`, `kernel_bridge.py` | `test_cpu.py`, `test_scheduler.py`, `test_react_kernel_bridge.py` | `Auto/docs/BITACORA_VIBE_CODING_COMPILADA.md` |
| **Integrante 2** | Memoria y Almacenamiento | `memory_storage.py`, `memory.py`, `virtual_memory.py`, `file_system.py` | `test_memory.py`, `test_virtual_memory_paging.py` | `AutoOS_1/docs/MEMORIA_Y_ALMACENAMIENTO.md` |
| **Integrante 3** | Seguridad, Dispositivos y RLS | `devices.py`, `auth_security.py`, `telemetry_battery.py`, `incidents.py`, `blackbox_cloud_sync.py` | `test_full_integration.py`, `test_v14_blackbox_cloud_sync.py`, `test_supabase.py` | `Auto/docs/BITACORA_VIBE_CODING.md`, `DOCUMENTO_ARQUITECTURA_INT3.md` |
| **Integrante 4** | Interfaz, Integración y Deploy | `app.py`, `autoos_unified.html`, `CinematicMenu.tsx`, `SimulationCenter.tsx`, `App.tsx` | `tools/verificar_entrega_final.ps1`, `tools/validar_v12.ps1`, `test_bluetooth_v12.cjs` | `docs/blue-shift/BITACORA.md`, `GUIA_CENTRO_SIMULACION.md`, `README.md` |

---

## 7. CONCLUSIÓN DEL EQUIPO
La integración de las responsabilidades de los cuatro integrantes mediante la metodología de Vibe Coding permitió construir un simulador de sistema operativo automotriz robusto, seguro y visualmente impactante, cumpliendo el 100% de los criterios de la matriz de evaluación y las directivas de seguridad ISO 26262 / ASIL-D.
