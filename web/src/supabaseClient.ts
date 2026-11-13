/**
 * ====================================================================
 * AUTOOS - CLIENTE DE CONEXIÓN A SUPABASE (FRONTEND WEB RESILIENTE)
 * ====================================================================
 * Implementación de alta compatibilidad que utiliza el API REST PostgREST
 * de Supabase de manera nativa (mediante fetch del navegador).
 *
 * Ventajas:
 * 1. Cero dependencias rotas si no se ha ejecutado 'npm install'.
 * 2. Funciona inmediatamente tanto en modo desarrollo (Vite) como en
 *    bundles HTML estáticos compilados.
 * 3. Total compatibilidad con Row-Level Security (RLS) y autenticación anon.
 * 4. Resiliente: si no hay credenciales, conmuta silenciosamente a modo local.
 * ====================================================================
 */

import type { AutoOSReport } from './simulation/report';

// Leer variables de entorno de Vite
const supabaseUrl = (import.meta.env.VITE_SUPABASE_URL || '').trim().replace(/\/$/, '');
const supabaseAnonKey = (import.meta.env.VITE_SUPABASE_ANON_KEY || '').trim();

/**
 * Valida si las credenciales están presentes y no son placeholders de ejemplo.
 */
export const isSupabaseConfigured = (): boolean => {
  return (
    Boolean(supabaseUrl) &&
    Boolean(supabaseAnonKey) &&
    !supabaseUrl.includes('tu-proyecto-aqui') &&
    !supabaseUrl.includes('your-project-id') &&
    !supabaseAnonKey.includes('tu-anon-key') &&
    !supabaseAnonKey.includes('your-anon-key')
  );
};

/**
 * Encabezados estándar para llamadas PostgREST de Supabase
 */
const getHeaders = (preferReturn = false): HeadersInit => ({
  apikey: supabaseAnonKey,
  Authorization: `Bearer ${supabaseAnonKey}`,
  'Content-Type': 'application/json',
  ...(preferReturn ? { Prefer: 'return=representation' } : {}),
});

/**
 * Prueba la conectividad real con Supabase consultando la tabla de dispositivos.
 */
export async function testSupabaseConnection(): Promise<{ ok: boolean; message: string; latencyMs?: number }> {
  if (!isSupabaseConfigured()) {
    return {
      ok: false,
      message: 'Credenciales no configuradas. Agrega VITE_SUPABASE_URL y VITE_SUPABASE_ANON_KEY en web/.env.',
    };
  }

  const start = performance.now();
  try {
    const res = await fetch(`${supabaseUrl}/rest/v1/dispositivos?select=codigo,estado&limit=1`, {
      method: 'GET',
      headers: getHeaders(),
    });
    const latency = Math.round(performance.now() - start);

    if (!res.ok) {
      const errText = await res.text();
      return {
        ok: false,
        message: `Error HTTP ${res.status} desde Supabase: ${errText}`,
        latencyMs: latency,
      };
    }

    const data = await res.json();
    return {
      ok: true,
      message: `Conectado exitosamente a Supabase Cloud (${latency} ms). Registros leídos: ${data.length}`,
      latencyMs: latency,
    };
  } catch (err: any) {
    return {
      ok: false,
      message: `Fallo de red o URL inalcanzable: ${err?.message || err}`,
    };
  }
}

/**
 * Guarda un informe generado en el Centro de Simulación en Supabase.
 * Intenta escribir en 'reportes_simulacion', y si la tabla no existe aún,
 * guarda un registro en 'eventos' como respaldo.
 */
export async function saveSimulationReportToSupabase(report: AutoOSReport): Promise<boolean> {
  if (!isSupabaseConfigured()) return false;

  const payload = {
    report_id: report.id,
    escenario: report.scenario,
    titulo: report.title,
    diagnostico: report.diagnosis,
    evaluacion: report.status,
    usuario_email: 'conductor@autoos.tech',
    iniciado_en: report.startedAt,
    finalizado_en: report.completedAt,
    bateria_inicial: report.initial.battery,
    bateria_final: report.final.battery,
    velocidad_final: report.final.speed,
    cpu_load_final: report.final.cpuLoad,
    acciones_json: report.actions,
    recomendaciones: report.recommendations,
    datos_completos: report,
  };

  try {
    // 1. Intentar insertar en la tabla dedicada 'reportes_simulacion'
    const res = await fetch(`${supabaseUrl}/rest/v1/reportes_simulacion`, {
      method: 'POST',
      headers: getHeaders(true),
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      console.log('[AutoOS Supabase] Informe guardado en reportes_simulacion:', report.id);
      return true;
    }

    // 2. Si falla (por ejemplo tabla no creada aún), insertar en tabla 'eventos'
    console.warn('[AutoOS Supabase] Fallback de reporte a tabla eventos (HTTP ' + res.status + ')');
    const fallbackRes = await fetch(`${supabaseUrl}/rest/v1/eventos`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        tipo_evento: 'simulacion',
        severidad: report.status.includes('RIESGO') ? 'advertencia' : 'info',
        mensaje: `Informe de Simulación: ${report.title} [${report.status}]`,
        detalles: {
          report_id: report.id,
          scenario: report.scenario,
          evaluation: report.status,
          recommendations: report.recommendations,
        },
        resuelto: true,
      }),
    });

    return fallbackRes.ok;
  } catch (err) {
    console.warn('[AutoOS Supabase] Error al sincronizar informe con la nube:', err);
    return false;
  }
}

/**
 * Registra un evento de seguridad o contingencia en Supabase.
 */
export async function logSimulatorEvent(
  tipo: string,
  severidad: 'info' | 'advertencia' | 'critico' | 'emergencia',
  mensaje: string,
  detalles: Record<string, any> = {}
): Promise<boolean> {
  if (!isSupabaseConfigured()) return false;

  try {
    const res = await fetch(`${supabaseUrl}/rest/v1/eventos`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        tipo_evento: tipo,
        severidad,
        mensaje,
        detalles,
        resuelto: severidad === 'info',
      }),
    });
    return res.ok;
  } catch (err) {
    console.warn('[AutoOS Supabase] Error al registrar evento:', err);
    return false;
  }
}

/**
 * Actualiza el estado operativo y salud de un dispositivo vehicular en Supabase.
 */
export async function updateDeviceInSupabase(
  codigo: string,
  estado: string,
  saludPorcentaje: number
): Promise<boolean> {
  if (!isSupabaseConfigured()) return false;

  try {
    const res = await fetch(`${supabaseUrl}/rest/v1/dispositivos?codigo=eq.${encodeURIComponent(codigo)}`, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify({
        estado,
        salud_porcentaje: saludPorcentaje,
        actualizado_en: new Date().toISOString(),
      }),
    });
    return res.ok;
  } catch (err) {
    console.warn('[AutoOS Supabase] Error al actualizar dispositivo:', err);
    return false;
  }
}

/**
 * Consulta la lista remota de dispositivos en Supabase Cloud.
 */
export async function fetchRemoteDevices(): Promise<any[] | null> {
  if (!isSupabaseConfigured()) return null;

  try {
    const res = await fetch(`${supabaseUrl}/rest/v1/dispositivos?select=*&order=codigo.asc`, {
      method: 'GET',
      headers: getHeaders(),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('[AutoOS Supabase] Error en fetchRemoteDevices:', err);
    return null;
  }
}
