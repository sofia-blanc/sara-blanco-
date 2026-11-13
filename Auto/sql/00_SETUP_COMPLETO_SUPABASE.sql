-- ====================================================================
-- AUTOOS - INSTALACIÓN COMPLETA UNIFICADA PARA SUPABASE
-- ARCHIVO: 00_SETUP_COMPLETO_SUPABASE.sql
-- Ejecuta este script COMPLETO en el SQL Editor de tu proyecto Supabase.
-- ====================================================================

-- ====================================================================
-- PARTE 1: ESQUEMA Y TABLAS (DDL)
-- ====================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

DROP TABLE IF EXISTS reportes_simulacion CASCADE;
DROP TABLE IF EXISTS auditoria_accesos CASCADE;
DROP TABLE IF EXISTS eventos CASCADE;
DROP TABLE IF EXISTS dispositivos CASCADE;
DROP TABLE IF EXISTS roles_permisos CASCADE;
DROP TABLE IF EXISTS perfiles CASCADE;
DROP TABLE IF EXISTS permisos CASCADE;
DROP TABLE IF EXISTS roles CASCADE;
DROP TABLE IF EXISTS procesos_historial CASCADE;
DROP TABLE IF EXISTS procesos CASCADE;
DROP TABLE IF EXISTS memoria_bloques CASCADE;
DROP TABLE IF EXISTS memoria_config CASCADE;
DROP TABLE IF EXISTS almacenamiento_config CASCADE;
DROP TABLE IF EXISTS archivos CASCADE;
DROP TABLE IF EXISTS logs CASCADE;

-- 1. TABLA: roles
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    nivel_privilegio INTEGER NOT NULL CHECK (nivel_privilegio >= 1 AND nivel_privilegio <= 10),
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. TABLA: permisos
CREATE TABLE permisos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clave VARCHAR(100) UNIQUE NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    descripcion TEXT,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. TABLA: roles_permisos
CREATE TABLE roles_permisos (
    rol_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permiso_id UUID NOT NULL REFERENCES permisos(id) ON DELETE CASCADE,
    asignado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (rol_id, permiso_id)
);

-- 4. TABLA: perfiles (asociado a auth.users de Supabase)
CREATE TABLE perfiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    nombre_completo VARCHAR(150) NOT NULL,
    rol_id UUID NOT NULL REFERENCES roles(id),
    avatar_url TEXT,
    activo BOOLEAN DEFAULT TRUE,
    ultimo_acceso TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. TABLA: dispositivos (hardware vehicular)
CREATE TABLE dispositivos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('sensor', 'actuador', 'comunicacion', 'potencia', 'multimedia', 'seguridad')),
    sub_sistema VARCHAR(50) NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'operativo' CHECK (estado IN ('operativo', 'degradado', 'falla', 'desconectado')),
    salud_porcentaje INTEGER NOT NULL DEFAULT 100 CHECK (salud_porcentaje >= 0 AND salud_porcentaje <= 100),
    puerto_bus VARCHAR(50) NOT NULL CHECK (puerto_bus IN ('CAN-Bus Principal', 'CAN-Bus ADAS', 'Automotive Ethernet', 'LIN-Bus Confort')),
    nivel_critico VARCHAR(20) NOT NULL CHECK (nivel_critico IN ('critico', 'esencial', 'confort')),
    datos_telemetria JSONB DEFAULT '{}'::jsonb,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. TABLA: eventos
CREATE TABLE eventos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo_evento VARCHAR(50) NOT NULL CHECK (tipo_evento IN ('seguridad', 'dispositivo_fallo', 'bateria_critica', 'intento_no_autorizado', 'cambio_estado_so', 'simulacion', 'contingencia')),
    severidad VARCHAR(20) NOT NULL CHECK (severidad IN ('info', 'advertencia', 'critico', 'emergencia')),
    dispositivo_id UUID REFERENCES dispositivos(id) ON DELETE SET NULL,
    usuario_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    mensaje TEXT NOT NULL,
    detalles JSONB DEFAULT '{}'::jsonb,
    resuelto BOOLEAN DEFAULT FALSE,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. TABLA: auditoria_accesos
CREATE TABLE auditoria_accesos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    usuario_email VARCHAR(255),
    rol_nombre VARCHAR(50),
    recurso VARCHAR(100) NOT NULL,
    accion VARCHAR(100) NOT NULL,
    autorizado BOOLEAN NOT NULL,
    motivo_rechazo TEXT,
    ip_o_modulo VARCHAR(50) DEFAULT 'dashboard_autoos',
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. TABLA: procesos (Integrante 1)
CREATE TABLE procesos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pid INTEGER UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'listo' CHECK (estado IN ('nuevo', 'listo', 'ejecutando', 'bloqueado', 'terminado')),
    prioridad INTEGER NOT NULL DEFAULT 5 CHECK (prioridad >= 0 AND prioridad <= 10),
    cpu_estimada NUMERIC(5,2) DEFAULT 0.0,
    memoria_mb INTEGER DEFAULT 64,
    es_critico BOOLEAN DEFAULT FALSE,
    usuario_creador UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE procesos_historial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proceso_id UUID REFERENCES procesos(id) ON DELETE CASCADE,
    estado_anterior VARCHAR(30),
    estado_nuevo VARCHAR(30) NOT NULL,
    cambiado_por UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    detalles TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. TABLAS DE MEMORIA Y ALMACENAMIENTO (Integrante 2)
CREATE TABLE memoria_bloques (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bloque_num INTEGER NOT NULL UNIQUE,
    tamano_mb INTEGER NOT NULL DEFAULT 256,
    ocupado BOOLEAN DEFAULT FALSE,
    proceso_id UUID REFERENCES procesos(id) ON DELETE SET NULL,
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE memoria_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ram_total_mb INTEGER NOT NULL DEFAULT 16384,
    kernel_reservado_mb INTEGER NOT NULL DEFAULT 2048,
    algoritmo_asignacion VARCHAR(50) DEFAULT 'First-Fit Dinámico',
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE almacenamiento_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    capacidad_total_gb INTEGER NOT NULL DEFAULT 512,
    tipo VARCHAR(50) DEFAULT 'NVMe SSD Automotriz ASIL',
    sistema_archivos VARCHAR(50) DEFAULT 'ext4-automotive',
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE archivos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ruta VARCHAR(255) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    tipo VARCHAR(30) NOT NULL,
    tamano_kb INTEGER DEFAULT 1,
    permisos_octal VARCHAR(4) DEFAULT '0644',
    propietario_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nivel VARCHAR(20) NOT NULL CHECK (nivel IN ('DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL')),
    modulo VARCHAR(50) NOT NULL,
    mensaje TEXT NOT NULL,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 10. TABLA: reportes_simulacion (Persistencia de Centro de Simulación Web)
CREATE TABLE reportes_simulacion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id VARCHAR(100) NOT NULL,
    escenario VARCHAR(50) NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    diagnostico TEXT,
    evaluacion VARCHAR(100),
    usuario_email VARCHAR(255) DEFAULT 'conductor@autoos.tech',
    iniciado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    finalizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    bateria_inicial NUMERIC(5,2),
    bateria_final NUMERIC(5,2),
    velocidad_final NUMERIC(5,2),
    cpu_load_final NUMERIC(5,2),
    acciones_json JSONB DEFAULT '[]'::jsonb,
    recomendaciones JSONB DEFAULT '[]'::jsonb,
    datos_completos JSONB DEFAULT '{}'::jsonb,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices de consulta rápida
CREATE INDEX idx_dispositivos_estado ON dispositivos(estado);
CREATE INDEX idx_eventos_severidad ON eventos(severidad);
CREATE INDEX idx_eventos_resuelto ON eventos(resuelto);
CREATE INDEX idx_procesos_estado ON procesos(estado);
CREATE INDEX idx_perfiles_rol ON perfiles(rol_id);
CREATE INDEX idx_auditoria_usuario ON auditoria_accesos(usuario_id);
CREATE INDEX idx_auditoria_autorizado ON auditoria_accesos(autorizado);
CREATE INDEX idx_reportes_escenario ON reportes_simulacion(escenario);
CREATE INDEX idx_reportes_creado_en ON reportes_simulacion(creado_en DESC);

-- ====================================================================
-- PARTE 2: POLÍTICAS DE SEGURIDAD (RLS)
-- ====================================================================

ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE permisos ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles_permisos ENABLE ROW LEVEL SECURITY;
ALTER TABLE perfiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE dispositivos ENABLE ROW LEVEL SECURITY;
ALTER TABLE eventos ENABLE ROW LEVEL SECURITY;
ALTER TABLE auditoria_accesos ENABLE ROW LEVEL SECURITY;
ALTER TABLE procesos ENABLE ROW LEVEL SECURITY;
ALTER TABLE procesos_historial ENABLE ROW LEVEL SECURITY;
ALTER TABLE memoria_bloques ENABLE ROW LEVEL SECURITY;
ALTER TABLE memoria_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE almacenamiento_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE archivos ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE reportes_simulacion ENABLE ROW LEVEL SECURITY;

-- Funciones auxiliares de seguridad
CREATE OR REPLACE FUNCTION fn_obtener_rol_actual()
RETURNS TEXT
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT r.nombre
    FROM perfiles p
    JOIN roles r ON p.rol_id = r.id
    WHERE p.id = auth.uid();
$$;

CREATE OR REPLACE FUNCTION fn_tiene_permiso(clave_permiso TEXT)
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM perfiles p
        JOIN roles_permisos rp ON p.rol_id = rp.rol_id
        JOIN permisos perm ON rp.permiso_id = perm.id
        WHERE p.id = auth.uid()
          AND perm.clave = clave_permiso
    );
$$;

-- Políticas RLS
CREATE POLICY "Lectura catalogo roles" ON roles FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Lectura catalogo permisos" ON permisos FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Lectura catalogo roles_permisos" ON roles_permisos FOR SELECT TO anon, authenticated USING (true);

CREATE POLICY "Lectura de perfiles" ON perfiles FOR SELECT TO authenticated USING (id = auth.uid() OR fn_obtener_rol_actual() = 'admin');
CREATE POLICY "Admin gestiona perfiles" ON perfiles FOR ALL TO authenticated USING (fn_obtener_rol_actual() = 'admin');

CREATE POLICY "Lectura publica dispositivos" ON dispositivos FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Admin o calibracion modifica dispositivos" ON dispositivos FOR UPDATE TO anon, authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Lectura eventos vehiculares" ON eventos FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Insercion eventos vehiculares" ON eventos FOR INSERT TO anon, authenticated WITH CHECK (true);

CREATE POLICY "Lectura auditoria" ON auditoria_accesos FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Insercion auditoria" ON auditoria_accesos FOR INSERT TO anon, authenticated WITH CHECK (true);

CREATE POLICY "Lectura procesos" ON procesos FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Modificacion procesos" ON procesos FOR ALL TO anon, authenticated USING (true);

CREATE POLICY "Lectura memoria" ON memoria_bloques FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Lectura memoria_config" ON memoria_config FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Lectura almacenamiento" ON almacenamiento_config FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Lectura archivos" ON archivos FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Lectura logs" ON logs FOR SELECT TO anon, authenticated USING (true);

CREATE POLICY "Lectura reportes simulacion" ON reportes_simulacion FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Insercion reportes simulacion" ON reportes_simulacion FOR INSERT TO anon, authenticated WITH CHECK (true);

-- ====================================================================
-- PARTE 3: DATOS SEMILLA (SEED DATA)
-- ====================================================================

-- 1. Roles
INSERT INTO roles (id, nombre, descripcion, nivel_privilegio) VALUES
('11111111-1111-1111-1111-111111111111', 'admin', 'Mecánico / Ingeniero de Servicio (Acceso Total a Telemetría, Calibración y Kernel)', 10),
('22222222-2222-2222-2222-222222222222', 'user', 'Conductor Autorizado (Control de Navegación, Conducción, Procesos de Usuario)', 5),
('33333333-3333-3333-3333-333333333333', 'guest', 'Pasajero / Invitado en Cabina (Acceso Restringido a Entretenimiento y Confort)', 1)
ON CONFLICT (id) DO UPDATE SET 
    nombre = EXCLUDED.nombre,
    descripcion = EXCLUDED.descripcion,
    nivel_privilegio = EXCLUDED.nivel_privilegio;

-- 2. Permisos
INSERT INTO permisos (id, clave, modulo, descripcion) VALUES
('aa010000-0000-0000-0000-000000000001', 'proceso.crear', 'procesos', 'Capacidad de iniciar un nuevo proceso en el SO vehicular'),
('aa010000-0000-0000-0000-000000000002', 'proceso.listar', 'procesos', 'Capacidad de consultar la lista de procesos activos'),
('aa010000-0000-0000-0000-000000000003', 'proceso.cambiar_estado', 'procesos', 'Capacidad de pausar o reanudar procesos en ejecución'),
('aa010000-0000-0000-0000-000000000004', 'proceso.finalizar', 'procesos', 'Capacidad de terminar o abortar procesos (SIGKILL)'),
('aa010000-0000-0000-0000-000000000005', 'proceso.priorizar_tiempo_real', 'procesos', 'Capacidad de asignar prioridad 0 (Tiempo Real Crítico)'),

('bb020000-0000-0000-0000-000000000001', 'dispositivo.consultar', 'dispositivos', 'Consultar estado, salud y telemetría de sensores y actuadores'),
('bb020000-0000-0000-0000-000000000002', 'dispositivo.calibrar', 'dispositivos', 'Ejecutar calibración de sensores ADAS y LiDAR'),
('bb020000-0000-0000-0000-000000000003', 'dispositivo.desconectar', 'dispositivos', 'Desconectar periférico del bus CAN'),
('bb020000-0000-0000-0000-000000000004', 'dispositivo.inyectar_fallo', 'dispositivos', 'Modo diagnóstico para inyectar fallos simulados en bus'),

('cc030000-0000-0000-0000-000000000001', 'seguridad.admin_usuarios', 'seguridad', 'Crear y modificar roles de usuarios vehiculares'),
('cc030000-0000-0000-0000-000000000002', 'seguridad.ver_auditoria', 'seguridad', 'Inspeccionar registros de auditoría'),

('dd040000-0000-0000-0000-000000000001', 'telemetria.ver_bateria', 'energia', 'Consultar estado de carga (SoC), temperatura y voltaje BMS'),
('dd040000-0000-0000-0000-000000000002', 'telemetria.modo_eco', 'energia', 'Activar perfiles de bajo consumo y reducción de potencia'),

('ee050000-0000-0000-0000-000000000001', 'cabina.control_clima', 'confort', 'Ajustar climatización HVAC y confort'),
('ee050000-0000-0000-0000-000000000002', 'cabina.control_multimedia', 'confort', 'Reproducir música, navegación y contenido en pantalla')
ON CONFLICT (id) DO UPDATE SET
    clave = EXCLUDED.clave,
    modulo = EXCLUDED.modulo,
    descripcion = EXCLUDED.descripcion;

-- 3. Matriz Roles <-> Permisos
-- Admin tiene todos
INSERT INTO roles_permisos (rol_id, permiso_id)
SELECT '11111111-1111-1111-1111-111111111111', id FROM permisos
ON CONFLICT DO NOTHING;

-- User (Conductor)
INSERT INTO roles_permisos (rol_id, permiso_id) VALUES
('22222222-2222-2222-2222-222222222222', 'aa010000-0000-0000-0000-000000000001'),
('22222222-2222-2222-2222-222222222222', 'aa010000-0000-0000-0000-000000000002'),
('22222222-2222-2222-2222-222222222222', 'aa010000-0000-0000-0000-000000000003'),
('22222222-2222-2222-2222-222222222222', 'aa010000-0000-0000-0000-000000000004'),
('22222222-2222-2222-2222-222222222222', 'bb020000-0000-0000-0000-000000000001'),
('22222222-2222-2222-2222-222222222222', 'dd040000-0000-0000-0000-000000000001'),
('22222222-2222-2222-2222-222222222222', 'dd040000-0000-0000-0000-000000000002'),
('22222222-2222-2222-2222-222222222222', 'ee050000-0000-0000-0000-000000000001'),
('22222222-2222-2222-2222-222222222222', 'ee050000-0000-0000-0000-000000000002')
ON CONFLICT DO NOTHING;

-- Guest (Pasajero)
INSERT INTO roles_permisos (rol_id, permiso_id) VALUES
('33333333-3333-3333-3333-333333333333', 'aa010000-0000-0000-0000-000000000002'),
('33333333-3333-3333-3333-333333333333', 'bb020000-0000-0000-0000-000000000001'),
('33333333-3333-3333-3333-333333333333', 'dd040000-0000-0000-0000-000000000001'),
('33333333-3333-3333-3333-333333333333', 'ee050000-0000-0000-0000-000000000001'),
('33333333-3333-3333-3333-333333333333', 'ee050000-0000-0000-0000-000000000002')
ON CONFLICT DO NOTHING;

-- 4. Dispositivos Vehiculares (10 dispositivos)
INSERT INTO dispositivos (id, codigo, nombre, tipo, sub_sistema, estado, salud_porcentaje, puerto_bus, nivel_critico, datos_telemetria) VALUES
('d0000001-0000-0000-0000-000000000001', 'DEV_GPS_01', 'Receptor GNSS / GPS Diferencial', 'sensor', 'Navegación', 'operativo', 98, 'CAN-Bus Principal', 'esencial', '{"satelites": 14, "hdop": 0.8, "lat": 4.6097, "lon": -74.0817, "frecuencia_hz": 10}'::jsonb),
('d0000002-0000-0000-0000-000000000002', 'DEV_CAM_FRONT', 'Cámara Estereoscópica ADAS Frontal', 'sensor', 'Visión Artificial', 'operativo', 95, 'Automotive Ethernet', 'critico', '{"fps": 60, "resolucion": "1080p", "temperatura_c": 42.5}'::jsonb),
('d0000003-0000-0000-0000-000000000003', 'DEV_LIDAR_01', 'Sensor LiDAR 360° Solid-State', 'sensor', 'Detección Obstáculos', 'operativo', 99, 'Automotive Ethernet', 'critico', '{"puntos_segundo": 1200000, "rango_max_m": 200, "rpm": 600}'::jsonb),
('d0000004-0000-0000-0000-000000000004', 'DEV_RADAR_01', 'Radar Milimétrico 77GHz (ACC)', 'sensor', 'Control Crucero ACC', 'operativo', 94, 'CAN-Bus ADAS', 'critico', '{"distancia_m": 35.4, "vel_relativa_kmh": -2.1}'::jsonb),
('d0000005-0000-0000-0000-000000000005', 'DEV_BATTERY_BMS', 'BMS - Batería LiFePO4 Alta Tensión', 'potencia', 'Tren Motriz', 'operativo', 92, 'CAN-Bus Principal', 'critico', '{"soc_pct": 84, "voltaje_v": 398.4, "corriente_a": 42.1, "temp_c": 31.8}'::jsonb),
('d0000006-0000-0000-0000-000000000006', 'DEV_ACT_BRAKE', 'Actuador Frenado By-Wire EBS', 'actuador', 'Seguridad Dinámica', 'operativo', 100, 'CAN-Bus ADAS', 'critico', '{"presion_bar": 0, "latencia_ms": 12, "redundancia": "dual_activa"}'::jsonb),
('d0000007-0000-0000-0000-000000000007', 'DEV_ACT_STEER', 'Actuador Dirección Eléctrica EPS', 'actuador', 'Seguridad Dinámica', 'operativo', 97, 'CAN-Bus ADAS', 'critico', '{"angulo_deg": 0.5, "torque_nm": 1.2}'::jsonb),
('d0000008-0000-0000-0000-000000000008', 'DEV_COM_V2X', 'Módulo Telemetría 5G / V2X Cloud', 'comunicacion', 'Conectividad Cloud', 'operativo', 91, 'Automotive Ethernet', 'esencial', '{"latencia_ms": 18, "calidad_dbm": -68}'::jsonb),
('d0000009-0000-0000-0000-000000000009', 'DEV_HVAC_CLIMA', 'Climatización y Gestión Térmica', 'actuador', 'Confort Cabina', 'operativo', 88, 'LIN-Bus Confort', 'confort', '{"temp_cabina_c": 21.5, "temp_deseada_c": 21.0}'::jsonb),
('d000000a-0000-0000-0000-000000000010', 'DEV_INFOTAINMENT', 'Pantalla Central Cockpit & Audio', 'multimedia', 'Infoentretenimiento', 'operativo', 96, 'LIN-Bus Confort', 'confort', '{"brillo_pct": 75, "volumen_pct": 40}'::jsonb)
ON CONFLICT (id) DO UPDATE SET
    nombre = EXCLUDED.nombre,
    estado = EXCLUDED.estado,
    salud_porcentaje = EXCLUDED.salud_porcentaje,
    datos_telemetria = EXCLUDED.datos_telemetria;

-- 5. Procesos Iniciales
INSERT INTO procesos (pid, nombre, estado, prioridad, cpu_estimada, memoria_mb, es_critico) VALUES
(101, 'bms_thermal_monitor', 'ejecutando', 0, 4.2, 128, true),
(102, 'adas_collision_avoidance', 'ejecutando', 0, 18.5, 512, true),
(103, 'can_bus_gateway_daemon', 'ejecutando', 1, 3.1, 96, true),
(104, 'gnss_navigation_engine', 'listo', 3, 5.0, 256, false),
(105, 'telemetry_cloud_sync', 'listo', 4, 2.8, 180, false),
(106, 'hvac_thermal_controller', 'ejecutando', 6, 1.5, 64, false),
(107, 'infotainment_media_player', 'ejecutando', 7, 8.4, 420, false),
(108, 'voice_assistant_agent', 'bloqueado', 8, 2.0, 310, false)
ON CONFLICT (pid) DO NOTHING;

-- 6. Eventos Iniciales
INSERT INTO eventos (tipo_evento, severidad, dispositivo_id, mensaje, detalles, resuelto) VALUES
('cambio_estado_so', 'info', NULL, 'Kernel AutoOS 2.4 arrancado exitosamente en ECU principal.', '{"boot_time_ms": 420, "kernel_version": "AutoOS-RT-2.4.1"}'::jsonb, true),
('seguridad', 'info', NULL, 'Políticas de seguridad RLS inicializadas y validadas con 3 roles.', '{"roles": 3, "permisos": 13}'::jsonb, true)
ON CONFLICT DO NOTHING;

-- 7. Auditoría Inicial
INSERT INTO auditoria_accesos (usuario_email, rol_nombre, recurso, accion, autorizado, motivo_rechazo) VALUES
('mecanico@autoos.tech', 'admin', 'dispositivos', 'dispositivo.calibrar', true, NULL),
('conductor@autoos.tech', 'user', 'procesos', 'proceso.crear', true, NULL),
('pasajero@autoos.tech', 'guest', 'procesos', 'proceso.finalizar', false, 'Violación de directiva de seguridad: Rol GUEST no posee capacidad de terminar procesos del vehículo.')
ON CONFLICT DO NOTHING;

-- 8. Memoria y Almacenamiento
INSERT INTO memoria_config (ram_total_mb, kernel_reservado_mb, algoritmo_asignacion) VALUES
(16384, 2048, 'First-Fit Dinámico')
ON CONFLICT DO NOTHING;

INSERT INTO almacenamiento_config (capacidad_total_gb, tipo, sistema_archivos) VALUES
(512, 'NVMe SSD Automotriz ASIL', 'ext4-automotive')
ON CONFLICT DO NOTHING;

-- 9. Logs Iniciales
INSERT INTO logs (nivel, modulo, mensaje) VALUES
('INFO', 'KERNEL', 'Inicialización de subsistema de memoria RAM 16GB completa.'),
('INFO', 'SCHEDULER', 'Planificador de procesos por prioridad arrancado.'),
('WARN', 'STORAGE', 'Espacio en /logs alcanzando 65% de capacidad rotativa.')
ON CONFLICT DO NOTHING;
