# AUTOOS: SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
# DOCUMENTO DE ARQUITECTURA Y ESPECIFICACIÓN TÉCNICA MAESTRA
> **Responsable de Ensamble e Integración:** Integrante 4 (Interfaz e Integración)  
> **Equipo de Desarrollo:** 4 Integrantes  
> **Versión:** 2.4-RT | **Materia:** Sistemas Operativos  
> **Stack:** Python, Streamlit, Supabase (PostgreSQL + RLS), Plotly  

---

## 1. INTRODUCCIÓN Y DEFINICIÓN DEL PROBLEMA

### 1.1 Contexto Automotriz y Problemática
Los vehículos modernos integran simultáneamente sistemas críticos de conducción autónoma (*ADAS*), control por cable (*By-Wire*), gestión de baterías de alto voltaje (*BMS*), conectividad en la nube (*V2X*) e infoentretenimiento para los ocupantes.

El problema central que aborda **AutoOS** es la **coexistencia segura de tareas de tiempo real crítico con funciones de confort y conectividad abierta**. Un fallo o consumo desmedido de recursos por parte de un proceso de entretenimiento (ej. streaming de música) no debe, bajo ninguna circunstancia, degradar el tiempo de respuesta del sistema de frenos antibloqueo (ABS) ni del actuador de dirección asistida (ASIL-D / ISO 26262).

### 1.2 Objetivos de AutoOS
1. **Garantizar la Seguridad Funcional:** Planificador preventivo con prioridades de tiempo real (0 = Tiempo Real Crítico, 10 = Ocioso/Confort).
2. **Control de Acceso Riguroso (Autenticación ≠ Autorización):** Modelo RBAC respaldado por políticas Row Level Security (RLS) en Supabase para evitar operaciones no autorizadas.
3. **Supervisión Continua de Recursos y Hardware:** Monitoreo en tiempo real de CPU, memoria RAM (16 GB simulados), almacenamiento SSD (512 GB) y estado del paquete LiFePO4 de 400V.
4. **Respuesta Automática a Incidentes (5 Fases):** Capacidad de degradación controlada (*Fail-Safe*) ante sensores defectuosos, sobrecalentamiento o agotamiento de batería.

---

## 2. USUARIOS, PERFILES Y MODELO DE SEGURIDAD (RBAC)

AutoOS implementa el principio de **Privilegio Mínimo** dividiendo el acceso en tres identidades funcionales:

```mermaid
graph TD
    Kernel[Kernel AutoOS v2.4] --> R_Admin[Rol ADMIN: Mecánico / Ing. Servicio]
    Kernel --> R_User[Rol USER: Conductor Autorizado]
    Kernel --> R_Guest[Rol GUEST: Pasajero / Invitado]

    R_Admin -->|Nivel 10| P_Admin[Acceso Kernel Total: Calibrar Sensores, Gestión RLS, Inyección de Fallas, SIGKILL Procesos]
    R_User -->|Nivel 5| P_User[Acceso Operativo: Conducción, Procesos Estándar, Modos ECO/Sport, Telemetría BMS]
    R_Guest -->|Nivel 1| P_Guest[Acceso Restringido: Confort Cabina, Infoentretenimiento, Solo Lectura de Telemetría]
```

### 2.1 Matriz de Permisos por Rol

| Permiso | Módulo | Descripción | Admin | User | Guest |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `proceso.crear` | Procesos | Iniciar nuevo proceso en el SO | ✅ | ✅ | ❌ |
| `proceso.listar` | Procesos | Consultar procesos en ejecución | ✅ | ✅ | ✅ |
| `proceso.cambiar_estado` | Procesos | Pausar/reanudar tareas del vehículo | ✅ | ✅ | ❌ |
| `proceso.finalizar` | Procesos | Abortar procesos (SIGKILL) | ✅ | ✅* | ❌ |
| `proceso.priorizar_tiempo_real` | Procesos | Asignar prioridad de nivel 0 (RT) | ✅ | ❌ | ❌ |
| `dispositivo.consultar` | Hardware | Inspeccionar estado de sensores/buses | ✅ | ✅ | ✅ |
| `dispositivo.calibrar` | Hardware | Calibrar LiDAR, Radar y Cámaras ADAS | ✅ | ❌ | ❌ |
| `dispositivo.desconectar` | Hardware | Interrupción física de bus CAN/Ethernet | ✅ | ❌ | ❌ |
| `dispositivo.inyectar_fallo` | Hardware | Simulación de avería de periférico | ✅ | ❌ | ❌ |
| `seguridad.admin_usuarios` | Seguridad | Administrar usuarios y roles | ✅ | ❌ | ❌ |
| `seguridad.ver_auditoria` | Seguridad | Consultar registros de acceso denegado | ✅ | ❌ | ❌ |
| `telemetria.ver_bateria` | Energía | Inspeccionar SoC, voltaje y celdas BMS | ✅ | ✅ | ✅ |
| `telemetria.modo_eco` | Energía | Forzar modo de ahorro energético | ✅ | ✅ | ❌ |
| `cabina.control_clima` | Confort | Ajuste de climatización y ventilación | ✅ | ✅ | ✅ |
| `cabina.control_multimedia` | Confort | Reproducción de audio y navegación | ✅ | ✅ | ✅ |

*\*Nota: El usuario Conductor (`user`) no puede abortar procesos con bandera `critico = True` (ASIL-D).*

---

## 3. ARQUITECTURA GENERAL DEL SISTEMA Y COMPONENTES

La arquitectura de AutoOS se organiza en cuatro capas modulares coordinadas por los cuatro integrantes del equipo:

```mermaid
graph TB
    subgraph CAPA_PRESENTACION["Capa 1: Presentación e Interfaz (Int. 4)"]
        UI_Cockpit[Dashboard Cockpit General]
        UI_Gantt[Visualizador Gantt CPU]
        UI_Memoria[Barras Apiladas RAM]
        UI_Dispositivos[Matriz de Hardware]
        UI_Semaforo[Semáforo Estado General]
        UI_Incidentes[Panel de 5 Fases de Falla]
    end

    subgraph CAPA_LOGICA["Capa 2: Lógica de Sistema Operativo"]
        subgraph MOD_INT1["Int. 1: Procesos y CPU"]
            Proc_Scheduler[Scheduler con Prioridades 0-10]
            Proc_Lifecycle[Ciclo de Vida: Listo/Ejecutando/Bloqueado]
            Proc_Metrics[Cálculo de Carga Total CPU]
        end

        subgraph MOD_INT2["Int. 2: Memoria y Almacenamiento"]
            Mem_RAM[Gestor RAM 16GB: Kernel vs Procesos]
            FS_Vehicle[Sistema de Archivos: /config, /logs, /maps]
            Log_Manager[Registrador de Logs: DEBUG a FATAL]
        end

        subgraph MOD_INT3["Int. 3: Seguridad, Hardware y Energía"]
            Sec_RBAC[Motor de Autorización RBAC]
            Dev_HAL[Abstracción de Buses: CAN, LIN, Ethernet]
            BMS_Engine[Telemetría Batería 400V y Térmica]
            Incident_5Phase[Protocolo de Contingencia 5 Fases]
        end
    end

    subgraph CAPA_PERSISTENCIA["Capa 3: Persistencia y Seguridad Backend (Supabase)"]
        DB_Postgres[(PostgreSQL 15)]
        DB_RLS[Políticas Row Level Security]
        DB_Auth[Supabase Auth / JWT]
    end

    CAPA_PRESENTACION --> MOD_INT1
    CAPA_PRESENTACION --> MOD_INT2
    CAPA_PRESENTACION --> MOD_INT3

    MOD_INT1 --> CAPA_PERSISTENCIA
    MOD_INT2 --> CAPA_PERSISTENCIA
    MOD_INT3 --> CAPA_PERSISTENCIA
```

### 3.1 Detalle de Módulos por Integrante

#### Integrante 1: Procesos, Scheduler y Estados
AutoOS implementa un modelo de 5 estados para los procesos del vehículo:

```mermaid
stateDiagram-v2
    [*] --> Nuevo : Solicitud creación proceso (proceso.crear)
    Nuevo --> Listo : Admisión y asignación de PID/Memoria
    Listo --> Ejecutando : Despacho Scheduler (Mayor Prioridad 0-10)
    Ejecutando --> Listo : Quantum expirado / Preemption
    Ejecutando --> Bloqueado : Espera de sensor o evento de bus CAN
    Bloqueado --> Listo : Telemetría recibida / Desbloqueo
    Ejecutando --> Terminado : Finalización / SIGKILL (proceso.finalizar)
    Terminado --> [*] : Recursos de CPU y RAM liberados
```

- **Scheduler por Prioridad Preventivo:** Las tareas de seguridad dinámica (ABS, Dirección EPS, BMS) operan con prioridad 0-1 (Tiempo Real Estricto), mientras que las tareas de usuario y confort operan con prioridades 3-10.
- **Modelo de Datos:** Tablas `procesos` (PID, nombre, prioridad, CPU %, RAM MB, crítico) y `procesos_historial` (trazabilidad de transiciones de estado con usuario y timestamp).

#### Integrante 2: Memoria, Archivos y Logs
- **Gestión de Memoria RAM:** Simulación de 16 GB totales (16384 MB). El Kernel RTOS reserva de manera estática e inviolable 2048 MB. El remanente se asigna mediante bloques dinámicos (`memoria_bloques`).
- **Sistema de Archivos Virtual:** Estructura jerárquica con carpetas raíz `/config`, `/logs`, `/media`, `/maps` y `/telemetry`, con permisos octales específicos según el rol.
- **Trazabilidad y Logs:** Registro centralizado en tabla `logs` categorizado en 5 niveles: `DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL`.
- **Modelo de Datos:** Tablas `memoria_bloques`, `memoria_config`, `archivos`, `almacenamiento_config`, `logs`.

#### Integrante 3: Seguridad, Dispositivos y Redes Vehiculares
- **Abstracción de Hardware (HAL):** Gestión de 10 dispositivos mapeados en buses CAN 2.0B, LIN y Automotive Ethernet, con estados: `operativo`, `degradado`, `falla` y `desconectado`.
- **Control de Acceso (RBAC + RLS):** 13 permisos en 5 módulos, validación obligatoria con `validar_accion()` y políticas a nivel de fila en Supabase.
- **Telemetría BMS y 5 Fases de Incidentes:** Supervisión térmica del paquete LiFePO4 de 400V y ejecución del protocolo de 5 fases ante averías críticas.
- **Modelo de Datos:** Tablas `roles`, `permisos`, `roles_permisos`, `perfiles`, `dispositivos`, `eventos`, `auditoria_accesos`.

#### Integrante 4: Interfaz, Integración y Visualizaciones
- **Cockpit Unificado:** Dashboard reactivo en Streamlit con diseño dark automotriz.
- **Visualizaciones Técnicas:** Tacómetros circulares Plotly, Diagrama de Gantt para CPU, gráfico Donut de procesos por estado, barra apilada horizontal de memoria RAM y Semáforo vehicular integral.
- **Despliegue y Validación:** Orquestación en Streamlit Cloud con sincronización en Supabase Cloud.

---

## 4. DIAGRAMA ENTIDAD-RELACIÓN (SUPABASE / POSTGRESQL)

El modelo de datos relacional consta de 14 tablas normalizadas sin colisiones de nombres, con llaves foráneas protegidas mediante `ON DELETE SET NULL` o `ON DELETE CASCADE`:

```mermaid
erDiagram
    roles ||--o{ perfiles : "asigna rol a"
    roles ||--o{ roles_permisos : "contiene"
    permisos ||--o{ roles_permisos : "pertenece a"
    
    perfiles ||--o{ auditoria_accesos : "genera intento"
    perfiles ||--o{ procesos : "crea"
    perfiles ||--o{ archivos : "es propietario"
    perfiles ||--o{ eventos : "asociado a"
    
    dispositivos ||--o{ eventos : "origina alerta"
    
    procesos ||--o{ procesos_historial : "registra cambio"
    procesos ||--o{ memoria_bloques : "reserva"

    roles {
        uuid id PK
        varchar nombre UK
        integer nivel_privilegio
        text descripcion
        timestamp creado_en
    }

    permisos {
        uuid id PK
        varchar clave UK
        varchar modulo
        text descripcion
    }

    roles_permisos {
        uuid rol_id PK,FK
        uuid permiso_id PK,FK
        timestamp asignado_en
    }

    perfiles {
        uuid id PK,FK
        varchar email UK
        varchar nombre_completo
        uuid rol_id FK
        boolean activo
    }

    dispositivos {
        uuid id PK
        varchar codigo UK
        varchar nombre
        varchar tipo
        varchar sub_sistema
        varchar estado
        integer salud_porcentaje
        varchar puerto_bus
        varchar nivel_critico
    }

    procesos {
        uuid id PK
        integer pid UK
        varchar nombre
        varchar estado
        integer prioridad
        numeric cpu_estimada
        integer memoria_mb
        boolean es_critico
        uuid usuario_creador FK
    }

    procesos_historial {
        uuid id PK
        uuid proceso_id FK
        varchar estado_anterior
        varchar estado_nuevo
        uuid cambiado_por FK
        timestamp timestamp
    }

    memoria_bloques {
        uuid id PK
        integer bloque_num UK
        integer tamano_mb
        boolean ocupado
        uuid proceso_id FK
    }

    archivos {
        uuid id PK
        varchar ruta UK
        varchar nombre
        varchar tipo
        integer tamano_kb
        varchar permisos_octal
        uuid propietario_id FK
    }

    eventos {
        uuid id PK
        varchar tipo_evento
        varchar severidad
        uuid dispositivo_id FK
        uuid usuario_id FK
        text mensaje
        boolean resuelto
    }

    auditoria_accesos {
        uuid id PK
        uuid usuario_id FK
        varchar usuario_email
        varchar rol_nombre
        varchar recurso
        varchar accion
        boolean autorizado
        text motivo_rechazo
        timestamp creado_en
    }

    logs {
        uuid id PK
        varchar nivel
        varchar modulo
        text mensaje
        timestamp creado_en
    }

    memoria_config {
        uuid id PK
        integer ram_total_mb
        integer kernel_reservado_mb
        varchar algoritmo_asignacion
        timestamp actualizado_en
    }

    almacenamiento_config {
        uuid id PK
        integer capacidad_total_gb
        varchar tipo
        varchar sistema_archivos
        timestamp actualizado_en
    }
```

### 4.1 Verificación de No Colisión y Políticas RLS
1. **Evitación de Recursión Infinita en RLS:** La función de base de datos `fn_obtener_rol_actual()` fue declarada como `SECURITY DEFINER` y `STABLE`, permitiendo consultar el rol del usuario autenticado sin provocar llamadas circulares en las políticas de la tabla `perfiles`.
2. **Preservación de Trazabilidad Forense:** Todas las referencias a usuarios en `auditoria_accesos`, `eventos` y `procesos_historial` usan `ON DELETE SET NULL`, garantizando que si una cuenta es removida, el historial de seguridad no desaparezca.
3. **Aislamiento por Severidad:** La política RLS sobre la tabla `eventos` restringe la lectura a usuarios invitados (`guest`), quienes únicamente pueden ver eventos de nivel `info` y `advertencia`, ocultando alertas críticas internas del tren motriz.

---

## 5. PROTOCOLO DE INCIDENTES EN 5 FASES (FASE 10)

Ante cualquier situación anómala en la telemetría, AutoOS ejecuta de forma determinística la secuencia de 5 fases exigida por la especificación:

1. **Detección:** El controlador de bus (CAN/Ethernet) identifica lecturas erráticas o fuera de rango (ej. Código DTC U0129-87 por error de redundancia cíclica en LiDAR).
2. **Registro:** El incidente se inserta de forma inmutable en `eventos` con severidad `critico` o `emergencia`.
3. **Alerta:** El semáforo general conmuta a **ROJO**, emitiendo señal acústica y visual en el HUD del Cockpit.
4. **Priorización:** El scheduler promueve tareas de frenado (`adas_collision_avoidance`) a prioridad de tiempo real 0 y suspende tareas de confort (`infotainment_media_player`).
5. **Respuesta Fail-Safe:** Se conmuta a la capa de respaldo secundario (ej. control por radar/cámaras con velocidad restringida a 60 km/h o parada segura en el arcén).
