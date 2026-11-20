/**
 * AutoOS V14 — Sincronización persistente y no bloqueante de Caja Negra.
 * La Caja Negra sigue siendo local; aquí se envían eventos representativos al
 * servidor Streamlit por LOTES y solo se retiran de la cola con acuse válido.
 * No se colocan claves Supabase en React. Sin Streamlit, se retienen pendientes.
 */
import { useEffect, useMemo, useRef, useState, useCallback } from 'react';
import { sendCloudRequest } from '../kernelBridge';

export type BlackboxEventInput = {
  id: string;
  kind: string;
  severity: 'info' | 'warning' | 'critical' | 'success';
  message: string;
  tick: number;
};
export type BlackboxCloudEvent = {
  id: string; kind: string; severity: BlackboxEventInput['severity'];
  message: string; tick: number; batteryPct: number; cpuPct: number; ramMb: number;
};
export type BlackboxCloudStatus = {
  pending: number; confirmed: number; message: string; online: boolean;
};

const PENDING_KEY = 'autoos_v14_blackbox_pending';
const CONFIRMED_KEY = 'autoos_v14_blackbox_confirmed';
const SESSION_KEY = 'autoos_v14_blackbox_session';
const QUEUE_LIMIT = 240;
const BATCH_LIMIT = 6;
const SENDING_INTERVAL_MS = 3500;
const RETRY_INTERVAL_MS = 12500;

function safeRead<T>(key: string, fallback: T): T {
  try { const raw = localStorage.getItem(key); return raw ? JSON.parse(raw) as T : fallback; }
  catch { return fallback; }
}
function safeWrite(key: string, value: unknown): void {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* el laboratorio continúa en memoria */ }
}
function sessionKey(): string {
  try {
    const old = sessionStorage.getItem(SESSION_KEY);
    if (old && /^[a-z0-9]{8,30}$/.test(old)) return old;
    const generated = `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 9)}`;
    sessionStorage.setItem(SESSION_KEY, generated);
    return generated;
  } catch { return `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 9)}`; }
}

export function shouldSyncBlackboxEvent(event: BlackboxEventInput): boolean {
  if (event.kind === 'GPS' && event.severity === 'info' && event.message.startsWith('Ruta virtual:')) {
    return event.tick % 5 === 0; // no registrar cada tick de navegación
  }
  return true; // transiciones del planificador, alarmas, cambios de ruta
}

export function useBlackboxCloudSync(
  incoming: BlackboxEventInput[], metrics: {batteryPct:number;cpuPct:number;ramMb:number}
): {status: BlackboxCloudStatus; retry: () => void} {
  const session = useRef(sessionKey());
  const queue = useRef<BlackboxCloudEvent[]>(safeRead(PENDING_KEY, []));
  const confirmed = useRef<string[]>(safeRead(CONFIRMED_KEY, []));
  const inFlight = useRef<{id:string;ids:string[]}|null>(null);
  const retryAt = useRef(0);
  const [status, setStatus] = useState<BlackboxCloudStatus>({
    pending: queue.current.length, confirmed: confirmed.current.length,
    message: 'Esperando eventos para sincronizar.', online: false,
  });
  const metricsRef = useRef(metrics);
  metricsRef.current = metrics;

  const refresh = useCallback((message: string, online: boolean) => {
    setStatus({pending: queue.current.length, confirmed: confirmed.current.length, message, online});
  }, []);

  // Entrada: se observan eventos del estado compartido; no se genera ningún tick.
  useEffect(() => {
    const known = new Set([...confirmed.current, ...queue.current.map(e => e.id)]);
    let added = 0;
    for (const event of incoming.slice(-150)) {
      if (!shouldSyncBlackboxEvent(event)) continue;
      const key = `${session.current}_${event.id.replace(/[^A-Za-z0-9_-]/g, '_')}`.slice(0, 90);
      if (known.has(key) || !key.match(/^[A-Za-z0-9_-]{5,90}$/)) continue;
      known.add(key);
      queue.current.push({
        id:key, kind: event.kind.toUpperCase().replace(/[^A-Z0-9_]/g,'_').slice(0,32),
        severity: event.severity,
        message:event.message.slice(0,220), tick:Math.max(0,Math.floor(event.tick)),
        batteryPct:metricsRef.current.batteryPct, cpuPct:metricsRef.current.cpuPct,
        ramMb:metricsRef.current.ramMb,
      });
      added++;
    }
    if (added) {
      // Si no hay red, limitar memoria; no borrar un lote en tránsito.
      queue.current = queue.current.slice(-QUEUE_LIMIT);
      safeWrite(PENDING_KEY, queue.current);
      refresh(`${added} acontecimiento(s) pendientes de sincronización.`, false);
    }
  }, [incoming, refresh]);

  useEffect(() => {
    const receive = (raw: Event) => {
      const result = (raw as CustomEvent).detail?.blackbox as
        {ack?:string;ok?:boolean;ackedIds?:string[];message?:string}|undefined;
      if (!result || !inFlight.current || result.ack !== inFlight.current.id) return;
      const ids = new Set(inFlight.current.ids);
      const accepted = new Set((Array.isArray(result.ackedIds) ? result.ackedIds : []).filter(id => ids.has(id)));
      if (accepted.size) {
        queue.current = queue.current.filter(event => !accepted.has(event.id));
        confirmed.current = [...new Set([...confirmed.current, ...accepted])].slice(-600);
        safeWrite(PENDING_KEY, queue.current);
        safeWrite(CONFIRMED_KEY, confirmed.current);
      }
      inFlight.current = null;
      retryAt.current = Date.now() + (result.ok ? 0 : RETRY_INTERVAL_MS);
      refresh(result.message || 'Respuesta del servidor recibida.', Boolean(result.ok));
    };
    window.addEventListener('autoos:kernel-update', receive);
    const timer = window.setInterval(() => {
      if (inFlight.current || queue.current.length === 0 || Date.now() < retryAt.current) return;
      const batch = queue.current.slice(0, BATCH_LIMIT);
      const id = `bb_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
      const sent = sendCloudRequest({type:'autoos:blackbox-batch',requestId:id,events:batch});
      if (!sent) {
        refresh('Sin puente Streamlit: los eventos siguen pendientes en este navegador.', false);
        retryAt.current = Date.now() + RETRY_INTERVAL_MS;
        return;
      }
      inFlight.current = {id, ids:batch.map(e => e.id)};
      retryAt.current = Date.now() + RETRY_INTERVAL_MS;
      refresh(`Enviando lote de ${batch.length} evento(s)…`, false);
    }, SENDING_INTERVAL_MS);
    const watchdog = window.setInterval(() => {
      if (inFlight.current && Date.now() > retryAt.current) {
        inFlight.current = null; // falta acuse: conservar eventos para reintento
        retryAt.current = Date.now() + RETRY_INTERVAL_MS;
        refresh('No llegó confirmación de Streamlit. Se reintentará sin borrar eventos.', false);
      }
    }, 2000);
    return () => {
      window.removeEventListener('autoos:kernel-update', receive);
      window.clearInterval(timer);
      window.clearInterval(watchdog);
    };
  }, [refresh]);

  const retry = useCallback(() => { retryAt.current=0; inFlight.current=null;
    refresh('Reintento solicitado. Se enviará el siguiente lote.', false); }, [refresh]);
  return useMemo(() => ({status,retry}), [status,retry]);
}
