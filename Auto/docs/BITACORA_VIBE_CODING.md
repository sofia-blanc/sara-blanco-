# AUTOOS: SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
## REGISTRO DE VIBE CODING — BITÁCORA DEL INTEGRANTE 3
### Módulo: Seguridad, Dispositivos, Roles, Permisos, Escenarios de Falla y Persistencia Cloud

---

## 1. INTRODUCCIÓN Y METODOLOGÍA
Siguiendo las pautas del **Proyecto Integrador de Sistemas Operativos**, esta bitácora documenta el proceso de desarrollo asistido por Inteligencia Artificial (**Vibe Coding** con Antigravity). Cada iteración detalla el prompt formulado, el código arquitectónico generado, las modificaciones realizadas, los errores técnicos encontrados durante las pruebas y las correcciones definitivas aplicadas.

---

## 2. ITERACIONES DE DESARROLLO

### ITERACIÓN 1: Diseño de la Base de Datos y Esquema Relacional en Supabase
- **Objetivo:** Definir el modelo de datos para el Integrante 3 (`roles`, `permisos`, `roles_permisos`, `perfiles`, `dispositivos`, `eventos`, `auditoria_accesos`) y asegurar compatibilidad con las tablas de los demás integrantes (`procesos`, `memoria_bloques`, `archivos`, `logs`).
- **Prompt Utilizado:**
  > *"Diseña el esquema DDL en PostgreSQL/Supabase para AutoOS (vehículo inteligente). Como Integrante 3, necesito las tablas para roles (admin/mecánico, user/conductor, guest/pasajero), catálogo de permisos por módulo, perfiles enlazados a auth.users, dispositivos vehiculares (sensores ADAS, actuadores By-Wire, BMS en buses CAN y Ethernet), tabla de eventos críticos y tabla de auditoría para demostrar Autenticación != Autorización."*
- **Código Generado:**
  Archivo [`sql/01_schema.sql`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/sql/01_schema.sql) y [`sql/03_seed_data.sql`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/sql/03_seed_data.sql).
- **Error Encontrado:**
  Al diseñar las claves foráneas, existía un riesgo de borrado en cascada sobre `eventos` y `auditoria_accesos` si un dispositivo o usuario era eliminado, perdiéndose la trazabilidad forense del vehículo.
- **Corrección Aplicada:**
  Se modificó la restricción referencial a `ON DELETE SET NULL` en `dispositivo_id` y `usuario_id`, preservando el registro inmutable del evento e incluyendo campos de respaldo como `usuario_email` y `rol_nombre`.

---

### ITERACIÓN 2: Implementación de Row Level Security (RLS) en Supabase
- **Objetivo:** Configurar las políticas de acceso a nivel de fila para garantizar que las restricciones se cumplan en el motor de base de datos.
- **Prompt Utilizado:**
  > *"Escribe el script SQL de políticas Row Level Security (RLS) para Supabase en AutoOS. El rol Admin (Mecánico) debe tener control total de calibración y usuarios. El Conductor (User) puede consultar y operar procesos normales pero no calibrar sensores críticos. El Pasajero (Guest) solo puede ver datos no críticos y confort. Evita problemas de recursión infinita al consultar perfiles."*
- **Código Generado:**
  Archivo [`sql/02_rls_policies.sql`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/sql/02_rls_policies.sql).
- **Error Encontrado:**
  En PostgreSQL, consultar directamente la tabla `perfiles` dentro de la política de `perfiles` genera una recursión infinita (`infinite recursion detected in policy for relation "perfiles"`).
- **Corrección Aplicada:**
  Se implementaron funciones auxiliares con modificador `SECURITY DEFINER` y `STABLE` (`fn_obtener_rol_actual()` y `fn_tiene_permiso(clave)`), permitiendo resolver el rol del usuario autenticado sin detonar la política recursiva.

---

### ITERACIÓN 3: Módulo de Abstracción de Hardware y Redes Vehiculares
- **Objetivo:** Crear el módulo de software que representa los sensores, actuadores y unidades electrónicas del vehículo en buses CAN y Automotive Ethernet.
- **Prompt Utilizado:**
  > *"Construye el módulo Python `devices.py` para AutoOS. Debe listar dispositivos automotrices con su salud, bus CAN/Ethernet y estado. Debe permitir inyectar fallos, desconectar dispositivos y calibrarlos, validando estrictamente que el usuario tenga los permisos adecuados."*
- **Código Generado:**
  Archivo [`modules/devices.py`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/modules/devices.py).
- **Cambios Realizados:**
  Se añadieron métricas de resumen (`obtener_resumen_dispositivos()`) para calcular el porcentaje de salud promedio del hardware y detectar de forma reactiva si algún dispositivo de seguridad crítica (ASIL-D) ha fallado.

---

### ITERACIÓN 4: Gestión Energética BMS y Semáforo Vehicular
- **Objetivo:** Desarrollar el subsistema de telemetría de batería de alta tensión (SoC, voltaje, temperatura, degradación) y el algoritmo de cálculo del estado global del sistema (Semáforo vehicular).
- **Prompt Utilizado:**
  > *"Implementa en `telemetry_battery.py` la telemetría del sistema BMS (Battery Management System). Debe modelar porcentaje de carga (SoC), temperatura, voltaje y salud de celdas. Debe incluir la función `evaluar_semaforo_sistema()` que compute el estado global (Verde: Nominal, Amarillo: Advertencia, Rojo: Crítico) basándose en la salud del hardware, anomalías térmicas y alertas activas."*
- **Código Generado:**
  Archivo [`modules/telemetry_battery.py`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/modules/telemetry_battery.py).
- **Cambios Realizados:**
  Se incorporó lógica de degradación acelerada si la temperatura supera los 45 °C o el SoC desciende del 10 %, simulando las condiciones térmicas reales de celdas de iones de litio.

---

### ITERACIÓN 5: Los 3 Escenarios de Falla Críticos (Fase 10 del Proyecto)
- **Objetivo:** Programar los 3 escenarios obligatorios para AutoOS (Sensor defectuoso, Batería baja, Proceso crítico) siguiendo estrictamente el ciclo de 5 fases.
- **Prompt Utilizado:**
  > *"Implementa en `incidents.py` los 3 escenarios de falla para AutoOS según el PDF: 1) Sensor defectuoso (LiDAR frontal), 2) Batería baja crítica (SoC 6% y recalentamiento), 3) Proceso crítico (fallo en dirección By-Wire). Cada uno debe ejecutar de forma visible: 1. Detectar, 2. Registrar, 3. Generar alerta, 4. Priorizar procesos, 5. Ejecutar una respuesta."*
- **Código Generado:**
  Archivo [`modules/incidents.py`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/modules/incidents.py).
- **Error Encontrado Durante Pruebas de Ejecución:**
  Al ejecutar la prueba de importación en Python:
  ```text
  NameError: name 'Tuple' is not defined. Did you mean: 'tuple'?
  File ".../modules/incidents.py", line 262, in restablecer_sistema_a_normal
  ```
- **Corrección Aplicada:**
  Se actualizó la sentencia de importación en la cabecera de `incidents.py` agregando `Tuple` a `from typing import Dict, Any, List, Tuple`. Tras el ajuste, la prueba unitaria arrojó código de salida 0 (*Success*).

---

### ITERACIÓN 6: Validación de Permisos en Procesos y Simulación Local
- **Objetivo:** Garantizar que las operaciones de procesos (crear, cambiar estado, finalizar) validen los permisos del rol activo (filas 11, 13 y 14 de la matriz RBAC).
- **Prompt Utilizado:**
  > *"Conecta `processes.py` con `auth_security.py` para que cuando un usuario intente crear un proceso verifique `proceso.crear`, al pausar/reanudar valide `proceso.cambiar_estado`, y al terminar valide `proceso.finalizar`. Si el usuario no tiene permiso (ej. Pasajero), debe denegarse con 403 Forbidden y guardarse en `auditoria_accesos`."*
- **Código Generado:**
  Archivos [`modules/processes.py`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/modules/processes.py) y [`modules/auth_security.py`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/modules/auth_security.py).
- **Cambios Realizados:**
  Se agregó una protección adicional: los procesos con bandera `critico = True` (como el control de colisión ADAS o el monitor térmico BMS) solo pueden ser finalizados por el Mecánico (Admin), protegiendo la integridad del vehículo incluso si un usuario común intenta finalizar tareas vitales.

---

### ITERACIÓN 7: Construcción del Dashboard y Experiencia de Usuario (Streamlit)
- **Objetivo:** Ensamblar una interfaz de usuario automotriz moderna, con tacómetros interactivos Plotly, conmutador rápido de usuarios para la defensa ante el profesor y soporte tanto para conexión Supabase Cloud como para motor simulado local.
- **Prompt Utilizado:**
  > *"Diseña la aplicación Streamlit `app.py` para AutoOS con diseño Cockpit oscuro de vehículo inteligente. Incluye barra lateral con conmutador de usuario activo (Mecánico, Conductor, Pasajero) para pruebas en vivo, banner superior con semáforo dinámico, pestañas para Cockpit, Seguridad y Roles (con matriz RBAC y visor de auditoría), Dispositivos (con inyector de fallas), Batería BMS, Escenarios de Falla (con stepper de las 5 fases), Procesos y Guía de Sustentación."*
- **Código Generado:**
  Archivos [`app.py`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/app.py) y [`modules/ui_components.py`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/modules/ui_components.py).

---

### ITERACIÓN 8: Estética Blue Shift y Unificación RBAC React <-> Streamlit
- **Objetivo:** Integrar la nueva paleta automotriz "Blue Shift" de alto contraste y unificar el control de roles entre el componente React de frontend y el backend de Streamlit.
- **Prompt Utilizado:**
  > *"Adapta `Auto/app.py` y los componentes CSS para que soporten la paleta Blue Shift (#030712, cian eléctrico, cobalto) en modo claro y oscuro. Unifica el selector de rol en la barra superior para que envíe eventos postMessage `AUTOOS_SET_ROLE` y `AUTOOS_SET_THEME` al iframe embebido, sincronizando instantáneamente los permisos RBAC sin recargar la página."*
- **Código Generado:**
  Archivos [`Auto/styles/blue_shift_streamlit.css`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/styles/blue_shift_streamlit.css), [`Auto/styles/blue_shift_cockpit.css`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/styles/blue_shift_cockpit.css) y actualización del puente de comunicación en `Auto/app.py`.
- **Error Encontrado:**
  Al cambiar de rol en Streamlit a "Pasajero", el iframe de cabina permanecía con privilegios de Mecánico si no se capturaba el evento en los primeros ciclos de renderizado.
- **Corrección Aplicada:**
  Se implementó un protocolo de saludo bidireccional: el iframe emite `AUTOOS_REQUEST_SYNC` al cargarse y el contenedor padre responde con reintentos programados a los 60 ms, 200 ms y 500 ms.

---

### ITERACIÓN 9: Puente de Kernel Python (`kernel_bridge.py`) y Despacho ASIL-D
- **Objetivo:** Establecer un puente de comunicación IPC determinístico entre el núcleo del sistema operativo en Python (`AutoOS_1/src/core/kernel.py`) y el despachador de procesos en el frontend.
- **Prompt Utilizado:**
  > *"Construye `kernel_bridge.py` y `bridge_react_kernel.py` para serializar en tiempo real los estados de la PCB, cambios de contexto, tiempos de espera y ráfagas restantes entre el kernel Python y los componentes de visualización en React. Si el kernel Python no está disponible en la sesión, provee fallback elegante a la simulación web."*
- **Código Generado:**
  Archivos [`Auto/kernel_bridge.py`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/kernel_bridge.py) y [`Auto/bridge_react_kernel.py`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/bridge_react_kernel.py).
- **Verificación:**
  Pruebas unitarias de serialización superadas con `python AutoOS_1/tests/test_react_kernel_bridge.py`.

---

### ITERACIÓN 10: Protocolo de Confirmación Asíncrona Robusta en Supabase Cloud (Etapa 13)
- **Objetivo:** Resolver el problema de falsos timeouts en la inserción de eventos desde React hacia la tabla `public.eventos` de Supabase Cloud.
- **Prompt Utilizado:**
  > *"Corrige el flujo de confirmación de eventos en Supabase. Cuando el frontend solicite guardar un evento de auditoría o falla, genera un `requestId` único. El cliente solo debe marcar el evento como CONFIRMADO si recibe `cloud.ack === requestId` desde Python. Evita confundir lentitud de red con fallos de la base de datos."*
- **Código Generado:**
  Documentado en [`docs/ETAPA_13_CONFIRMACION_EVENTOS_SUPABASE.md`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/docs/ETAPA_13_CONFIRMACION_EVENTOS_SUPABASE.md) y actualizado en `Auto/bridge_component/index.html`.
- **Error Encontrado:**
  Los usuarios observaban mensajes persistentes de «En espera...» a pesar de que el registro ya había sido insertado exitosamente en PostgreSQL.
- **Corrección Aplicada:**
  Se estableció una máquina de estados estricta de tres salidas (`CONFIRMADO`, `OPERACIÓN RECHAZADA` o `SIN CONFIRMACIÓN`) vinculada al identificador único de transacción.

---

### ITERACIÓN 11: Implementación de Caja Negra Vehicular con Sincronización en Batches (Etapa 14)
- **Objetivo:** Desarrollar la Caja Negra automotriz que almacena cronológicamente los eventos de despacho, cambios de estado y alertas críticas, sincronizándolos con Supabase sin exceder cuotas de API.
- **Prompt Utilizado:**
  > *"Implementa en `blackbox_cloud_sync.py` y `web/src/cloud/blackboxSync.ts` la sincronización de la Caja Negra con Supabase. Almacena eventos en una cola local en el navegador y despacha en lotes de hasta 6 eventos cada 3.5 segundos. En el backend, valida la estructura y desduplica los registros usando el campo `detalles.autoos_id` antes del INSERT."*
- **Código Generado:**
  Archivos [`Auto/blackbox_cloud_sync.py`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/blackbox_cloud_sync.py) y [`web/src/cloud/blackboxSync.ts`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/web/src/cloud/blackboxSync.ts).
- **Verificación:**
  `python AutoOS_1/tests/test_v14_blackbox_cloud_sync.py` validó la persistencia y desduplicación de 24 eventos confirmados en la tabla `public.eventos`.

---

### ITERACIÓN 12: Telemetría Reactiva de RAM / CPU y Calibración OBD-II (Etapa 15)
- **Objetivo:** Lograr que los indicadores de uso de memoria RAM y CPU en el Cockpit y en el planificador RTOS reflejen en tiempo real la ejecución de procesos, reproducción multimedia, inyección de fallas y calibración.
- **Prompt Utilizado:**
  > *"Haz que la telemetría vehicular de RAM y CPU sea 100% reactiva ante cambios en los procesos. Al pausar un proceso debe liberar memoria a swap, al matarlo con SIGKILL debe liberar su cuota completa, al reproducir música debe aumentar la carga del DSP de audio, y al inyectar ataques CAN o fallas de hardware debe reflejar sobrecarga de buffers. Incluye botón y función de calibración OBD-II para restablecer sensores a 100% nominal."*
- **Código Generado:**
  Actualizaciones en [`Auto/autoos_interactive.html`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/autoos_interactive.html), [`Auto/autoos_unified.html`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/Auto/autoos_unified.html) y script de sincronización base64 [`tools/update_memory_telemetry.py`](file:///C:/Users/Usuario/Desktop/mio/universidad/autoos/tools/update_memory_telemetry.py).
- **Error Encontrado:**
  Valores estáticos de `baseRam = 48.5` en el listener de multimedia sobreescribían los incrementos de memoria provocados por escenarios de incidentes.
- **Corrección Aplicada:**
  Se reemplazó la asignación fija por un efecto reactivo unificado `useEffect([f, ie, u])` que recalcula de forma determinística la memoria sobre una base ASIL-D de 4096 MB.

---

## 3. RESUMEN DE APRENDIZAJES Y BUENAS PRÁCTICAS DE VIBE CODING
1. **La IA propone, el estudiante valida y comprende:** Cada componente generado fue contrastado rigurosamente con los fundamentos teóricos de sistemas operativos: modelado formal de PCBs, exclusión mutua, jerarquía de buses vehiculares, políticas RBAC multinivel y directivas de seguridad funcional ISO 26262.
2. **Pruebas tempranas, estáticas y automatizadas:** El testeo automatizado de scripts con `node --check`, suites de pruebas unitarias (`test_full_integration.py`, `test_v14_blackbox_cloud_sync.py`) y comprobación de esquemas SQL permitió erradicar fallos de importación y tipos antes del despliegue en producción.
3. **Resiliencia de despliegue y desacoplamiento:** El sistema fue diseñado con una arquitectura de fallback inmutable: opera inmediatamente contra Supabase Cloud pero cuenta con un motor en memoria local que asegura el 100% de operatividad ante caídas de red durante la sustentación ante el jurado evaluador.
4. **Trazabilidad forense inmutable:** En sistemas automotrices críticos, los eventos de auditoría jamás deben eliminarse en cascada; el uso de `ON DELETE SET NULL` y la desduplicación de la Caja Negra aseguran que la bitácora del vehículo sea legal y técnicamente infalsificable.
