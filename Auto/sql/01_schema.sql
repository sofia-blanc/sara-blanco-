-- ====================================================================
-- AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
-- ARCHIVO: 01_schema.sql
-- RESPONSABLE: Integrante 3 (Seguridad, Dispositivos y Control de Acceso)
-- ====================================================================

-- Extensiones requeridas
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Limpieza preventiva de tablas previas si existen (respetando orden de dependencias)
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
DROP TABLE IF EXISTS archivos CASCADE;
DROP TABLE IF EXISTS logs CASCADE;

-- --------------------------------------------------------------------
-- 1. TABLA: roles
-- Define los niveles de acceso del vehículo: admin (mecánico), user (conductor), guest (pasajero)
-- --------------------------------------------------------------------
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    nivel_privilegio INTEGER NOT NULL CHECK (nivel_privilegio >= 1 AND nivel_privilegio <= 10),
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- --------------------------------------------------------------------
-- 2. TABLA: permisos
-- Catálogo atómico de capacidades sobre procesos, dispositivos y configuración
-- --------------------------------------------------------------------
CREATE TABLE permisos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clave VARCHAR(100) UNIQUE NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    descripcion TEXT,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- --------------------------------------------------------------------
-- 3. TABLA: roles_permisos (Tabla intermedia muchos-a-muchos)
-- --------------------------------------------------------------------
CREATE TABLE roles_permisos (
    rol_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permiso_id UUID NOT NULL REFERENCES permisos(id) ON DELETE CASCADE,
    asignado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (rol_id, permiso_id)
);

-- --------------------------------------------------------------------
-- 4. TABLA: perfiles (Extensión de auth.users de Supabase)
-- Almacena la identidad vehicular, rol asignado y estado del usuario
-- --------------------------------------------------------------------
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

-- --------------------------------------------------------------------
-- 5. TABLA: dispositivos
-- Hardware y periféricos del vehículo (sensores ADAS, actuadores by-wire, BMS, etc.)
-- --------------------------------------------------------------------
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

-- --------------------------------------------------------------------
-- 6. TABLA: eventos
-- Registro de sucesos críticos del vehículo, fallos de hardware y alarmas
-- --------------------------------------------------------------------
CREATE TABLE eventos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo_evento VARCHAR(50) NOT NULL CHECK (tipo_evento IN ('seguridad', 'dispositivo_fallo', 'bateria_critica', 'intento_no_autorizado', 'cambio_estado_so')),
    severidad VARCHAR(20) NOT NULL CHECK (severidad IN ('info', 'advertencia', 'critico', 'emergencia')),
    dispositivo_id UUID REFERENCES dispositivos(id) ON DELETE SET NULL,
    usuario_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    mensaje TEXT NOT NULL,
    detalles JSONB DEFAULT '{}'::jsonb,
    resuelto BOOLEAN DEFAULT FALSE,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- --------------------------------------------------------------------
-- 7. TABLA: auditoria_accesos
-- Demuestra Autenticación != Autorización (logs de rechazo y aprobación)
-- --------------------------------------------------------------------
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

-- --------------------------------------------------------------------
-- 8. TABLAS DE INTEGRACIÓN CON OTROS INTEGRANTES
-- (Procesos, Memoria, Archivos y Logs de Sistema)
-- --------------------------------------------------------------------

-- Tabla de Procesos (Integrante 1)
CREATE TABLE procesos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pid INTEGER UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'listo' CHECK (estado IN ('nuevo', 'listo', 'ejecutando', 'bloqueado', 'terminado')),
    prioridad INTEGER NOT NULL DEFAULT 5 CHECK (prioridad >= 0 AND prioridad <= 10), -- 0 = Tiempo Real Crítico, 10 = Idle
    cpu_estimada NUMERIC(5,2) DEFAULT 0.0,
    memoria_mb INTEGER DEFAULT 64,
    es_critico BOOLEAN DEFAULT FALSE,
    usuario_creador UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Historial de transiciones de estados de procesos (Integrante 1)
CREATE TABLE procesos_historial (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proceso_id UUID REFERENCES procesos(id) ON DELETE CASCADE,
    estado_anterior VARCHAR(30),
    estado_nuevo VARCHAR(30) NOT NULL,
    cambiado_por UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    detalles TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Memoria y Bloques (Integrante 2)
CREATE TABLE memoria_bloques (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bloque_num INTEGER NOT NULL UNIQUE,
    tamano_mb INTEGER NOT NULL DEFAULT 256,
    ocupado BOOLEAN DEFAULT FALSE,
    proceso_id UUID REFERENCES procesos(id) ON DELETE SET NULL,
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Configuración de Memoria RAM (Integrante 2)
CREATE TABLE memoria_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ram_total_mb INTEGER NOT NULL DEFAULT 16384,
    kernel_reservado_mb INTEGER NOT NULL DEFAULT 2048,
    algoritmo_asignacion VARCHAR(50) DEFAULT 'First-Fit Dinámico',
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Configuración de Almacenamiento (Integrante 2)
CREATE TABLE almacenamiento_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    capacidad_total_gb INTEGER NOT NULL DEFAULT 512,
    tipo VARCHAR(50) DEFAULT 'NVMe SSD Automotriz ASIL',
    sistema_archivos VARCHAR(50) DEFAULT 'ext4-automotive',
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sistema de Archivos Virtual (Integrante 2)
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

-- Logs Generales del Sistema Operativo (Integrante 2)
CREATE TABLE logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nivel VARCHAR(20) NOT NULL CHECK (nivel IN ('DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL')),
    modulo VARCHAR(50) NOT NULL,
    mensaje TEXT NOT NULL,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para optimización de consultas en tiempo real
CREATE INDEX idx_dispositivos_estado ON dispositivos(estado);
CREATE INDEX idx_eventos_severidad ON eventos(severidad);
CREATE INDEX idx_eventos_resuelto ON eventos(resuelto);
CREATE INDEX idx_procesos_estado ON procesos(estado);
CREATE INDEX idx_perfiles_rol ON perfiles(rol_id);
CREATE INDEX idx_auditoria_usuario ON auditoria_accesos(usuario_id);
CREATE INDEX idx_auditoria_autorizado ON auditoria_accesos(autorizado);
