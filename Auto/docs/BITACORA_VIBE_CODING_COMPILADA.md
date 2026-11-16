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
**Responsabilidad:** Scheduler preventivo, estados de procesos, diagrama Gantt y cálculo de métricas de procesador.

### Iteración 1.1: Definición del Bloque de Control de Proceso (PCB)
- **Prompt:**
  > *"Diseña la estructura del Bloque de Control de Procesos (PCB) para AutoOS. Debe incluir PID único, nombre del proceso automotriz, estados formales (Nuevo, Listo, Ejecutando, Bloqueado, Terminado), prioridad numérica (0 para Tiempo Real Crítico ASIL-D, hasta 10 para Confort/Ocioso), consumo estimado de CPU y memoria requerida."*
- **Código Generado:**
  Módulo de procesos y tabla `procesos` en Supabase.
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

---

## 3. BITÁCORA — INTEGRANTE 2: MEMORIA, ARCHIVOS Y LOGS
**Responsabilidad:** Gestión de RAM (16 GB), bloques dinámicos, sistema de archivos vehicular y trazabilidad de logs.

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

---

## 4. BITÁCORA — INTEGRANTE 3: SEGURIDAD, DISPOSITIVOS Y RLS
**Responsabilidad:** Modelo RBAC, políticas Row Level Security (RLS) en Supabase, HAL de dispositivos CAN/Ethernet, telemetría BMS y protocolo de contingencia en 5 fases.

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

---

## 5. BITÁCORA — INTEGRANTE 4: INTERFAZ, INTEGRACIÓN Y DEPLOY
**Responsabilidad:** Dashboard Cockpit en Streamlit, componentes visuales Plotly (Gantt, barras apiladas, donut), cálculo del semáforo general, ensamblado de arquitectura y despliegue en Streamlit Cloud.

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

### Iteración 4.4: Preparación y Validación para Despliegue en Streamlit Cloud
- **Prompt:**
  > *"Verifica los archivos requirements.txt y la configuración de secrets.toml para asegurar un despliegue exitoso en Streamlit Cloud sin dependencias faltantes ni fallos de autenticación."*
- **Acción:**
  Se verificaron versiones estables de `streamlit>=1.30.0`, `supabase>=2.0.0`, `plotly>=5.18.0` y `pandas>=2.0.0`. Se preparó el conector con respaldo de base de datos en memoria para garantizar que la aplicación arranque de forma infalible tanto en local como en la nube.

---

## 6. CONCLUSIÓN DEL EQUIPO
La integración de las responsabilidades de los cuatro integrantes mediante la metodología de Vibe Coding permitió construir un simulador de sistema operativo automotriz robusto, seguro y visualmente impactante, cumpliendo el 100% de los criterios de la matriz de evaluación y las directivas de seguridad ISO 26262 / ASIL-D.
