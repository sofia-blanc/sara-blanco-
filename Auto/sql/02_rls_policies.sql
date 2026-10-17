-- ====================================================================
-- AUTOOS - SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE
-- ARCHIVO: 02_rls_policies.sql
-- RESPONSABLE: Integrante 3 (Seguridad, Dispositivos y RLS)
-- ====================================================================

-- 1. Habilitar Row Level Security (RLS) en todas las tablas sensibles
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
ALTER TABLE archivos ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;

-- --------------------------------------------------------------------
-- FUNCIONES AUXILIARES DE SEGURIDAD (SECURITY DEFINER)
-- Permiten consultar el rol y permisos del usuario autenticado sin recursión
-- --------------------------------------------------------------------

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

-- --------------------------------------------------------------------
-- POLÍTICAS RLS: perfiles
-- --------------------------------------------------------------------
-- Cualquier usuario autenticado puede leer su propio perfil o el Admin puede leer todos
CREATE POLICY "Lectura de perfiles"
ON perfiles FOR SELECT
TO authenticated
USING (
    id = auth.uid() OR fn_obtener_rol_actual() = 'admin'
);

-- Solo el Admin puede insertar o actualizar roles de perfiles
CREATE POLICY "Admin gestiona perfiles"
ON perfiles FOR ALL
TO authenticated
USING (fn_obtener_rol_actual() = 'admin')
WITH CHECK (fn_obtener_rol_actual() = 'admin');

-- --------------------------------------------------------------------
-- POLÍTICAS RLS: roles, permisos, roles_permisos
-- --------------------------------------------------------------------
-- Usuarios anónimos y autenticados pueden ver el catálogo de roles y permisos
CREATE POLICY "Lectura de catalogo de seguridad"
ON roles FOR SELECT
TO anon, authenticated
USING (true);

CREATE POLICY "Lectura de catalogo de permisos"
ON permisos FOR SELECT
TO anon, authenticated
USING (true);

CREATE POLICY "Lectura de roles_permisos"
ON roles_permisos FOR SELECT
TO anon, authenticated
USING (true);

-- Solo el rol Admin puede modificar el esquema de roles y permisos
CREATE POLICY "Admin modifica catalogo de roles"
ON roles FOR ALL
TO authenticated
USING (fn_obtener_rol_actual() = 'admin')
WITH CHECK (fn_obtener_rol_actual() = 'admin');

-- --------------------------------------------------------------------
-- POLÍTICAS RLS: dispositivos
-- --------------------------------------------------------------------
-- Lectura pública para telemetría vehicular en cabina
CREATE POLICY "Lectura publica de dispositivos"
ON dispositivos FOR SELECT
TO anon, authenticated
USING (true);


-- Modificar estado de dispositivos (calibrar, desconectar, inyectar fallos):
-- Conductor puede ver o reportar, pero solo el Admin (Mecánico) puede alterar o calibrar
CREATE POLICY "Admin modifica dispositivos"
ON dispositivos FOR UPDATE
TO authenticated
USING (fn_tiene_permiso('dispositivo.calibrar') OR fn_obtener_rol_actual() = 'admin')
WITH CHECK (fn_tiene_permiso('dispositivo.calibrar') OR fn_obtener_rol_actual() = 'admin');

CREATE POLICY "Admin inserta o elimina dispositivos"
ON dispositivos FOR DELETE
TO authenticated
USING (fn_obtener_rol_actual() = 'admin');

-- --------------------------------------------------------------------
-- POLÍTICAS RLS: eventos
-- --------------------------------------------------------------------
-- Cualquier usuario puede consultar eventos de severidad 'info' o 'advertencia',
-- pero eventos de seguridad y críticos son visibles para Conductor y Mecánico.
CREATE POLICY "Lectura de eventos segun rol"
ON eventos FOR SELECT
TO authenticated
USING (
    fn_obtener_rol_actual() IN ('admin', 'user') 
    OR (fn_obtener_rol_actual() = 'guest' AND severidad IN ('info', 'advertencia'))
);

-- Cualquier subsistema o usuario autenticado puede disparar un registro de evento (ej. alerta)
CREATE POLICY "Insercion de eventos autenticados"
ON eventos FOR INSERT
TO authenticated
WITH CHECK (true);

-- --------------------------------------------------------------------
-- POLÍTICAS RLS: auditoria_accesos
-- Demuestra el cumplimiento de la separación Autenticación != Autorización
-- --------------------------------------------------------------------
-- Solo el Admin (Mecánico) puede auditar todos los accesos; el usuario puede ver los suyos
CREATE POLICY "Lectura de auditoria"
ON auditoria_accesos FOR SELECT
TO authenticated
USING (
    fn_obtener_rol_actual() = 'admin' OR usuario_id = auth.uid()
);

-- Inserción permitida por el backend del SO para registrar intentos válidos o bloqueados
CREATE POLICY "Registro de auditoria del sistema"
ON auditoria_accesos FOR INSERT
TO authenticated
WITH CHECK (true);

-- --------------------------------------------------------------------
-- POLÍTICAS RLS: procesos (Demostración de requerimiento Int. 3 en procesos)
-- --------------------------------------------------------------------
-- Todos los autenticados pueden ver la lista de procesos
CREATE POLICY "Lectura de procesos"
ON procesos FOR SELECT
TO authenticated
USING (true);

-- Solo usuarios con permiso 'proceso.crear' pueden registrar un nuevo proceso
CREATE POLICY "Creacion de procesos con permiso"
ON procesos FOR INSERT
TO authenticated
WITH CHECK (
    fn_tiene_permiso('proceso.crear') OR fn_obtener_rol_actual() = 'admin'
);

-- Solo usuarios con permiso 'proceso.cambiar_estado' o 'proceso.finalizar' pueden modificar
CREATE POLICY "Modificacion y finalizacion de procesos"
ON procesos FOR UPDATE
TO authenticated
USING (
    fn_tiene_permiso('proceso.cambiar_estado') OR fn_tiene_permiso('proceso.finalizar') OR fn_obtener_rol_actual() = 'admin'
)
WITH CHECK (
    fn_tiene_permiso('proceso.cambiar_estado') OR fn_tiene_permiso('proceso.finalizar') OR fn_obtener_rol_actual() = 'admin'
);

-- --------------------------------------------------------------------
-- POLÍTICAS RLS: logs
-- --------------------------------------------------------------------
-- Mecánico ve todos los logs; Conductor ve INFO y WARN; Pasajero no ve logs de sistema
CREATE POLICY "Lectura de logs segun nivel y rol"
ON logs FOR SELECT
TO authenticated
USING (
    fn_obtener_rol_actual() = 'admin'
    OR (fn_obtener_rol_actual() = 'user' AND nivel IN ('INFO', 'WARN'))
);
