-- ====================================================================
-- AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
-- ARCHIVO: 03_seed_data.sql
-- RESPONSABLE: Integrante 3 (Datos de prueba: Roles, Permisos, Dispositivos)
-- ====================================================================

-- --------------------------------------------------------------------
-- 1. CARGA DE ROLES
-- --------------------------------------------------------------------
INSERT INTO roles (id, nombre, descripcion, nivel_privilegio) VALUES
('11111111-1111-1111-1111-111111111111', 'admin', 'Mecánico / Ingeniero de Servicio (Acceso Total a Telemetría, Calibración y Kernel)', 10),
('22222222-2222-2222-2222-222222222222', 'user', 'Conductor Autorizado (Control de Navegación, Conducción, Procesos de Usuario)', 5),
('33333333-3333-3333-3333-333333333333', 'guest', 'Pasajero / Invitado en Cabina (Acceso Restringido a Entretenimiento y Confort)', 1)
ON CONFLICT (id) DO UPDATE SET 
    nombre = EXCLUDED.nombre,
    descripcion = EXCLUDED.descripcion,
    nivel_privilegio = EXCLUDED.nivel_privilegio;

-- --------------------------------------------------------------------
-- 2. CARGA DE PERMISOS
-- --------------------------------------------------------------------
INSERT INTO permisos (id, clave, modulo, descripcion) VALUES
-- Módulo de Procesos (controlado por Int. 3)
('aa010000-0000-0000-0000-000000000001', 'proceso.crear', 'procesos', 'Capacidad de iniciar un nuevo proceso en el SO vehicular'),
('aa010000-0000-0000-0000-000000000002', 'proceso.listar', 'procesos', 'Capacidad de consultar la lista de procesos activos'),
('aa010000-0000-0000-0000-000000000003', 'proceso.cambiar_estado', 'procesos', 'Capacidad de pausar o reanudar procesos en ejecución'),
('aa010000-0000-0000-0000-000000000004', 'proceso.finalizar', 'procesos', 'Capacidad de terminar o abortar procesos (SIGKILL)'),
('aa010000-0000-0000-0000-000000000005', 'proceso.priorizar_tiempo_real', 'procesos', 'Capacidad de asignar prioridad 0 (Tiempo Real Crítico)'),

-- Módulo de Dispositivos y Hardware
('bb020000-0000-0000-0000-000000000001', 'dispositivo.consultar', 'dispositivos', 'Consultar estado, salud y telemetría de sensores y actuadores'),
('bb020000-0000-0000-0000-000000000002', 'dispositivo.calibrar', 'dispositivos', 'Ejecutar calibración de sensores ADAS y LiDAR'),
('bb020000-0000-0000-0000-000000000003', 'dispositivo.desconectar', 'dispositivos', 'Desconectar físicamente/lógicamente un dispositivo del bus'),
('bb020000-0000-0000-0000-000000000004', 'dispositivo.inyectar_fallo', 'dispositivos', 'Modo diagnóstico para inyectar fallos simulados en bus'),

-- Módulo de Seguridad y Auditoría
('cc030000-0000-0000-0000-000000000001', 'seguridad.admin_usuarios', 'seguridad', 'Crear y modificar roles de usuarios vehiculares'),
('cc030000-0000-0000-0000-000000000002', 'seguridad.ver_auditoria', 'seguridad', 'Inspeccionar registros de intentos autorizados y denegados'),

-- Módulo de Batería y Energía
('dd040000-0000-0000-0000-000000000001', 'telemetria.ver_bateria', 'energia', 'Consultar estado de carga (SoC), temperatura y voltaje BMS'),
('dd040000-0000-0000-0000-000000000002', 'telemetria.modo_eco', 'energia', 'Activar perfiles de bajo consumo y reducción de potencia'),

-- Módulo de Control de Cabina / Multimedia
('ee050000-0000-0000-0000-000000000001', 'cabina.control_clima', 'confort', 'Ajustar climatización HVAC y calefacción de asientos'),
('ee050000-0000-0000-0000-000000000002', 'cabina.control_multimedia', 'confort', 'Reproducir música, navegación y contenido en pantalla')
ON CONFLICT (id) DO UPDATE SET
    clave = EXCLUDED.clave,
    modulo = EXCLUDED.modulo,
    descripcion = EXCLUDED.descripcion;

-- --------------------------------------------------------------------
-- 3. ASIGNACIÓN MATRIZ ROLES <-> PERMISOS
-- --------------------------------------------------------------------

-- Rol: ADMIN (Mecánico / Ingeniero) -> TIENE TODOS LOS PERMISOS
INSERT INTO roles_permisos (rol_id, permiso_id)
SELECT '11111111-1111-1111-1111-111111111111', id FROM permisos
ON CONFLICT DO NOTHING;

-- Rol: USER (Conductor)
INSERT INTO roles_permisos (rol_id, permiso_id) VALUES
('22222222-2222-2222-2222-222222222222', 'aa010000-0000-0000-0000-000000000001'), -- proceso.crear
('22222222-2222-2222-2222-222222222222', 'aa010000-0000-0000-0000-000000000002'), -- proceso.listar
('22222222-2222-2222-2222-222222222222', 'aa010000-0000-0000-0000-000000000003'), -- proceso.cambiar_estado
('22222222-2222-2222-2222-222222222222', 'aa010000-0000-0000-0000-000000000004'), -- proceso.finalizar
('22222222-2222-2222-2222-222222222222', 'bb020000-0000-0000-0000-000000000001'), -- dispositivo.consultar
('22222222-2222-2222-2222-222222222222', 'dd040000-0000-0000-0000-000000000001'), -- telemetria.ver_bateria
('22222222-2222-2222-2222-222222222222', 'dd040000-0000-0000-0000-000000000002'), -- telemetria.modo_eco
('22222222-2222-2222-2222-222222222222', 'ee050000-0000-0000-0000-000000000001'), -- cabina.control_clima
('22222222-2222-2222-2222-222222222222', 'ee050000-0000-0000-0000-000000000002')  -- cabina.control_multimedia
ON CONFLICT DO NOTHING;

-- Rol: GUEST (Pasajero) -> Solo lectura y confort
INSERT INTO roles_permisos (rol_id, permiso_id) VALUES
('33333333-3333-3333-3333-333333333333', 'aa010000-0000-0000-0000-000000000002'), -- proceso.listar (solo ver)
('33333333-3333-3333-3333-333333333333', 'bb020000-0000-0000-0000-000000000001'), -- dispositivo.consultar
('33333333-3333-3333-3333-333333333333', 'dd040000-0000-0000-0000-000000000001'), -- telemetria.ver_bateria (solo ver)
('33333333-3333-3333-3333-333333333333', 'ee050000-0000-0000-0000-000000000001'), -- cabina.control_clima (temperatura pasajero)
('33333333-3333-3333-3333-333333333333', 'ee050000-0000-0000-0000-000000000002')  -- cabina.control_multimedia
ON CONFLICT DO NOTHING;

-- --------------------------------------------------------------------
-- 4. CARGA DE DISPOSITIVOS VEHICULARES DE AUTOOS
-- Representa sensores, actuadores, ECUs y periféricos del vehículo
-- --------------------------------------------------------------------
INSERT INTO dispositivos (id, codigo, nombre, tipo, sub_sistema, estado, salud_porcentaje, puerto_bus, nivel_critico, datos_telemetria) VALUES
('d0000001-0000-0000-0000-000000000001', 'DEV_GPS_01', 'Receptor GNSS / GPS Diferencial', 'sensor', 'Navegación', 'operativo', 98, 'CAN-Bus Principal', 'esencial', '{"satelites_visibles": 14, "hdop": 0.8, "lat": 4.60971, "lon": -74.08175, "frecuencia_hz": 10}'::jsonb),
('d0000002-0000-0000-0000-000000000002', 'DEV_CAM_FRONT', 'Cámara Estereoscópica ADAS Frontal', 'sensor', 'Visión Artificial', 'operativo', 95, 'Automotive Ethernet', 'critico', '{"fps": 60, "resolucion": "1080p", "temperatura_c": 42.5, "oclusion_lente": false}'::jsonb),
('d0000003-0000-0000-0000-000000000003', 'DEV_LIDAR_01', 'Sensor LiDAR 360° Solid-State', 'sensor', 'Detección Obstáculos', 'operativo', 99, 'Automotive Ethernet', 'critico', '{"puntos_segundo": 1200000, "rango_max_m": 200, "rpm": 600, "ruido_retorno_pct": 1.2}'::jsonb),
('d0000004-0000-0000-0000-000000000004', 'DEV_RADAR_01', 'Radar de Onda Milimétrica 77GHz', 'sensor', 'Control Crucero ACC', 'operativo', 94, 'CAN-Bus ADAS', 'critico', '{"objetos_trackeados": 8, "distancia_vehiculo_delantero_m": 35.4, "velocidad_relativa_kmh": -2.1}'::jsonb),
('d0000005-0000-0000-0000-000000000005', 'DEV_BATTERY_BMS', 'BMS - Batería de Alta Tensión LiFePO4', 'potencia', 'Tren Motriz', 'operativo', 92, 'CAN-Bus Principal', 'critico', '{"soc_porcentaje": 84, "voltaje_total_v": 398.4, "corriente_descarga_a": 42.1, "temp_max_celda_c": 31.8, "salud_soh": 96}'::jsonb),
('d0000006-0000-0000-0000-000000000006', 'DEV_ACT_BRAKE', 'Actuador Electromecánico By-Wire Frenado', 'actuador', 'Seguridad Dinámica', 'operativo', 100, 'CAN-Bus ADAS', 'critico', '{"presion_hidraulica_bar": 0, "tiempo_respuesta_ms": 12, "redundancia_activa": true}'::jsonb),
('d0000007-0000-0000-0000-000000000007', 'DEV_ACT_STEER', 'Actuador de Dirección Asistida (EPS)', 'actuador', 'Seguridad Dinámica', 'operativo', 97, 'CAN-Bus ADAS', 'critico', '{"angulo_volante_deg": 0.5, "torque_nm": 1.2, "modo": "asistido_autonomo"}'::jsonb),
('d0000008-0000-0000-0000-000000000008', 'DEV_COM_V2X', 'Módulo de Telemetría 5G / V2X', 'comunicacion', 'Conectividad Cloud', 'operativo', 91, 'Automotive Ethernet', 'esencial', '{"latencia_ms": 18, "calidad_senal_dbm": -68, "servidor_telemetria": "supabase_gateway"}'::jsonb),
('d0000009-0000-0000-0000-000000000009', 'DEV_HVAC_CLIMA', 'Climatización Bizona y Gestión Térmica', 'actuador', 'Confort de Cabina', 'operativo', 88, 'LIN-Bus Confort', 'confort', '{"temp_cabina_c": 21.5, "temp_deseada_c": 21.0, "potencia_compresor_pct": 35}'::jsonb),
('d000000a-0000-0000-0000-000000000010', 'DEV_INFOTAINMENT', 'Pantalla Central Digital & Audio Cockpit', 'multimedia', 'Infoentretenimiento', 'operativo', 96, 'LIN-Bus Confort', 'confort', '{"brillo_pantalla_pct": 75, "audio_volumen_pct": 40, "app_activa": "spotify_car"}'::jsonb)
ON CONFLICT (id) DO UPDATE SET
    nombre = EXCLUDED.nombre,
    estado = EXCLUDED.estado,
    salud_porcentaje = EXCLUDED.salud_porcentaje,
    datos_telemetria = EXCLUDED.datos_telemetria;

-- --------------------------------------------------------------------
-- 5. CARGA INICIAL DE PROCESOS AUTOMOTRICES (Para integración con Int. 1)
-- --------------------------------------------------------------------
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

-- --------------------------------------------------------------------
-- 6. EVENTOS INICIALES DE SISTEMA
-- --------------------------------------------------------------------
INSERT INTO eventos (tipo_evento, severidad, dispositivo_id, mensaje, detalles, resuelto) VALUES
('cambio_estado_so', 'info', NULL, 'Kernel AutoOS 2.4 arrancado exitosamente en ECU principal.', '{"boot_time_ms": 420, "kernel_version": "AutoOS-RT-2.4.1"}'::jsonb, true),
('seguridad', 'info', NULL, 'Políticas de seguridad RLS inicializadas y validadas.', '{"roles_cargados": 3, "permisos_activos": 13}'::jsonb, true),
('dispositivo_fallo', 'advertencia', 'd0000009-0000-0000-0000-000000000009', 'Filtro de polen en climatizador detecta saturación ligera.', '{"delta_presion_pa": 120}'::jsonb, false)
ON CONFLICT DO NOTHING;

-- --------------------------------------------------------------------
-- 7. AUDITORÍA INICIAL (Demostración Autenticación != Autorización)
-- --------------------------------------------------------------------
INSERT INTO auditoria_accesos (usuario_email, rol_nombre, recurso, accion, autorizado, motivo_rechazo) VALUES
('mecanico@autoos.tech', 'admin', 'dispositivos', 'dispositivo.calibrar', true, NULL),
('conductor@autoos.tech', 'user', 'procesos', 'proceso.crear', true, NULL),
('pasajero@autoos.tech', 'guest', 'procesos', 'proceso.finalizar', false, 'Violación de directiva de seguridad: Rol GUEST no posee la capacidad de terminar procesos del vehículo.')
ON CONFLICT DO NOTHING;

-- --------------------------------------------------------------------
-- 8. CONFIGURACIÓN DE MEMORIA Y ALMACENAMIENTO (Integrante 2)
-- --------------------------------------------------------------------
INSERT INTO memoria_config (ram_total_mb, kernel_reservado_mb, algoritmo_asignacion) VALUES
(16384, 2048, 'First-Fit Dinámico')
ON CONFLICT DO NOTHING;

INSERT INTO almacenamiento_config (capacidad_total_gb, tipo, sistema_archivos) VALUES
(512, 'NVMe SSD Automotriz ASIL', 'ext4-automotive')
ON CONFLICT DO NOTHING;

-- --------------------------------------------------------------------
-- 9. CARPETAS Y ARCHIVOS BASE DEL VEHÍCULO (/config, /logs, /media, /maps)
-- --------------------------------------------------------------------
INSERT INTO archivos (ruta, nombre, tipo, tamano_kb, permisos_octal) VALUES
('/config/vehicle_params.json', 'vehicle_params.json', 'Configuración', 12, '0600'),
('/config/adas_network_weights.bin', 'adas_network_weights.bin', 'Modelo IA', 184000, '0444'),
('/maps/offline_regional_hd.bin', 'offline_regional_hd.bin', 'Navegación', 850000, '0444'),
('/media/cockpit_soundtrack.flac', 'cockpit_soundtrack.flac', 'Audio', 42000, '0644'),
('/logs/blackbox_can_telemetry.log', 'blackbox_can_telemetry.log', 'Registro Forense', 3200, '0640')
ON CONFLICT DO NOTHING;

-- --------------------------------------------------------------------
-- 10. LOGS INICIALES DE SISTEMA OPERATIVO (Integrante 2)
-- --------------------------------------------------------------------
INSERT INTO logs (nivel, modulo, mensaje) VALUES
('INFO', 'KERNEL', 'Inicialización de subsistema de memoria RAM 16GB completa.'),
('INFO', 'SCHEDULER', 'Planificador de procesos por prioridad arrancado.'),
('WARN', 'STORAGE', 'Espacio en /logs alcanzando 65% de capacidad rotativa.')
ON CONFLICT DO NOTHING;
