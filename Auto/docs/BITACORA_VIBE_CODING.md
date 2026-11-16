# AUTOOS: SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
## REGISTRO DE VIBE CODING — BITÁCORA DEL INTEGRANTE 3
### Módulo: Seguridad, Dispositivos, Roles, Permisos y Escenarios de Falla

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
  Archivo [`sql/01_schema.sql`](file:///C:/Users/nicol/.gemini/antigravity/scratch/auto_os/sql/01_schema.sql) y [`sql/03_seed_data.sql`](file:///C:/Users/nicol/.gemini/antigravity/scratch/auto_os/sql/03_seed_data.sql).
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
  Archivo [`sql/02_rls_policies.sql`](file:///C:/Users/nicol/.gemini/antigravity/scratch/auto_os/sql/02_rls_policies.sql).
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
  Archivo [`modules/devices.py`](file:///C:/Users/nicol/.gemini/antigravity/scratch/auto_os/modules/devices.py).
- **Cambios Realizados:**
  Se añadieron métricas de resumen (`obtener_resumen_dispositivos()`) para calcular el porcentaje de salud promedio del hardware y detectar de forma reactiva si algún dispositivo de seguridad crítica (ASIL-D) ha fallado.

---

### ITERACIÓN 4: Sistema BMS de Batería y Aporte al Semáforo General
- **Objetivo:** Cumplir el requisito de la fila 10 de la matriz: *'Dashboard: estado general -> Aporta batería y eventos críticos'*.
- **Prompt Utilizado:**
  > *"Crea `telemetry_battery.py` para modelar el sistema de batería de alta tensión (BMS) del vehículo eléctrico (SoC %, voltaje, temperatura) y programar la función que calcula el semáforo vehicular (Verde, Amarillo, Rojo) combinando el nivel de batería, los fallos de hardware y los eventos críticos activos."*
- **Código Generado:**
  Archivo [`modules/telemetry_battery.py`](file:///C:/Users/nicol/.gemini/antigravity/scratch/auto_os/modules/telemetry_battery.py).
- **Verificación:**
  Si el SoC cae por debajo del 10% o hay eventos críticos no resueltos, el semáforo conmuta inmediatamente a **ROJO** activando el modo Fail-Safe. Si el SoC está entre 11% y 25% o hay dispositivos degradados, conmuta a **AMARILLO**. En condiciones normales, opera en **VERDE**.

---

### ITERACIÓN 5: Los 3 Escenarios de Falla Críticos (Fase 10 del PDF)
- **Objetivo:** Programar los 3 escenarios obligatorios para AutoOS (Sensor defectuoso, Batería baja, Proceso crítico) siguiendo estrictamente el ciclo de 5 fases.
- **Prompt Utilizado:**
  > *"Implementa en `incidents.py` los 3 escenarios de falla para AutoOS según el PDF: 1) Sensor defectuoso (LiDAR frontal), 2) Batería baja crítica (SoC 6% y recalentamiento), 3) Proceso crítico (fallo en dirección By-Wire). Cada uno debe ejecutar de forma visible: 1. Detectar, 2. Registrar, 3. Generar alerta, 4. Priorizar procesos, 5. Ejecutar una respuesta."*
- **Código Generado:**
  Archivo [`modules/incidents.py`](file:///C:/Users/nicol/.gemini/antigravity/scratch/auto_os/modules/incidents.py).
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
- **Objetivo:** Garantizar que las operaciones de procesos (crear, cambiar estado, finalizar) validen los permisos del rol activo (filas 11, 13 y 14 de la matriz).
- **Prompt Utilizado:**
  > *"Conecta `processes.py` con `auth_security.py` para que cuando un usuario intente crear un proceso verifique `proceso.crear`, al pausar/reanudar valide `proceso.cambiar_estado`, y al terminar valide `proceso.finalizar`. Si el usuario no tiene permiso (ej. Pasajero), debe denegarse con 403 Forbidden y guardarse en `auditoria_accesos`."*
- **Código Generado:**
  Archivos [`modules/processes.py`](file:///C:/Users/nicol/.gemini/antigravity/scratch/auto_os/modules/processes.py) y [`modules/auth_security.py`](file:///C:/Users/nicol/.gemini/antigravity/scratch/auto_os/modules/auth_security.py).
- **Cambios Realizados:**
  Se agregó una protección adicional: los procesos con bandera `critico = True` (como el control de colisión ADAS o el monitor térmico BMS) solo pueden ser finalizados por el Mecánico (Admin), protegiendo la integridad del vehículo incluso si un usuario común intenta finalizar tareas vitales.

---

### ITERACIÓN 7: Construcción del Dashboard y Experiencia de Usuario (Streamlit)
- **Objetivo:** Ensamblar una interfaz de usuario automotriz moderna, con tacómetros interactivos Plotly, conmutador rápido de usuarios para la defensa ante el profesor y soporte tanto para conexión Supabase Cloud como para motor simulado local.
- **Prompt Utilizado:**
  > *"Diseña la aplicación Streamlit `app.py` para AutoOS con diseño Cockpit oscuro de vehículo inteligente. Incluye barra lateral con conmutador de usuario activo (Mecánico, Conductor, Pasajero) para pruebas en vivo, banner superior con semáforo dinámico, pestañas para Cockpit, Seguridad y Roles (con matriz RBAC y visor de auditoría), Dispositivos (con inyector de fallas), Batería BMS, Escenarios de Falla (con stepper de las 5 fases), Procesos y Guía de Sustentación."*
- **Código Generado:**
  Archivos [`app.py`](file:///C:/Users/nicol/.gemini/antigravity/scratch/auto_os/app.py) y [`modules/ui_components.py`](file:///C:/Users/nicol/.gemini/antigravity/scratch/auto_os/modules/ui_components.py).

---

## 3. RESUMEN DE APRENDIZAJES Y BUENAS PRÁCTICAS DE VIBE CODING
1. **La IA propone, el estudiante valida y comprende:** Cada componente generado fue revisado contra los principios teóricos de sistemas operativos (modelado de procesos, exclusión mutua, jerarquía de buses, RBAC y control de fallos).
2. **Pruebas tempranas y automatizadas:** El testeo automatizado de scripts y tipos de datos permitió capturar errores de importación antes de llegar a la fase de despliegue.
3. **Resiliencia de despliegue:** El sistema fue diseñado con una arquitectura de desacople desacoplada: funciona inmediatamente con Supabase Cloud y cuenta con un motor en memoria que previene caídas si la red no está disponible durante la sustentación.
