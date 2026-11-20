/**
 * Protocolo de integración V10 (React <-> kernel Python de Streamlit).
 *
 * Una solicitud deliberada envía la lista de procesos de la sesión React.
 * No hay comunicación directa con Python en la vista Vite local; el puente
 * solo existe dentro del componente bidireccional de Streamlit.
 *
 * El servidor valida el mensaje y realiza reservas reales en First-Fit.
 * Los PIDs Python y React son DISTINTOS; la respuesta contiene su mapa.
 */
export interface PythonKernelStatus {
  connected: boolean;
  mode: string;
  booted: boolean;
  tick: number;
  ramMb: number;
  ramTotalMb: number;
  cpuPid: number | null;
  pythonProcesses: number;
  mappedPids: Record<string, number>;
  events: number;
  lastReactTick: number;
  lastBatteryPctReact: number | null;
  message: string;
  errors: string[];
  ack: string | null;
  /** V11: prueba real por Supabase desde servidor, nunca mera configuración. */
  cloud?: {ok:boolean;message:string;ack?:string};
  /** V14: los acuses de Caja Negra son independientes de la prueba manual. */
  blackbox?: {ok:boolean;message:string;ack?:string;ackedIds?:string[]};
}

export interface PythonKernelSyncRequest {
  type: 'autoos:kernel-sync';
  requestId: string;
  tick: number;
  batteryPct: number;
  processes: Array<{
    pid: number;
    name: string;
    memoryMb: number;
    priority: number;
    burstTime: number;
  }>;
}

export type CloudRequest = {type:'autoos:blackbox-batch';requestId:string;events:import('./cloud/blackboxSync').BlackboxCloudEvent[]} |
  {type:'autoos:cloud-test';requestId:string} |
  {type:'autoos:cloud-event';requestId:string;message:string;severity:'info'|'advertencia'|'critico'} |
  {type:'autoos:cloud-report';requestId:string;report:Record<string,unknown>};

interface ComponentBridge {
  latest: PythonKernelStatus | null;
  send: (message: PythonKernelSyncRequest | CloudRequest) => void;
}

declare global {
  interface Window {
    __AUTOOS_KERNEL_COMPONENT__?: ComponentBridge;
  }
}

export function getPythonKernelStatus(): PythonKernelStatus | null {
  return typeof window !== 'undefined' ? (window.__AUTOOS_KERNEL_COMPONENT__?.latest ?? null) : null;
}

export function sendKernelSyncRequest(message: PythonKernelSyncRequest): boolean {
  const bridge = typeof window !== 'undefined' ? window.__AUTOOS_KERNEL_COMPONENT__ : undefined;
  if (!bridge) return false;
  bridge.send(message);
  return true;
}

/**
 * Escucha eventos emitidos cuando Streamlit vuelve a renderizar el componente
 * con el resultado del kernel. El listener no crea ciclos ni envía nada.
 */
export function onPythonKernelStatus(callback: (value: PythonKernelStatus) => void): () => void {
  const listener = (event: Event) => {
    const status = (event as CustomEvent<PythonKernelStatus>).detail;
    if (status && typeof status.tick === 'number') callback(status);
  };
  window.addEventListener('autoos:kernel-update', listener);
  return () => window.removeEventListener('autoos:kernel-update', listener);
}

/** Solo se envía la operación. Las claves permanecen en Streamlit Secrets. */
export function sendCloudRequest(request:CloudRequest):boolean {
  const bridge = typeof window!=='undefined'?window.__AUTOOS_KERNEL_COMPONENT__:undefined;
  if(!bridge)return false;
  bridge.send(request);
  return true;
}

// AUTOOS_V14_BLACKBOX_CLOUD — el puente V10 transporta lotes de Caja Negra también.
