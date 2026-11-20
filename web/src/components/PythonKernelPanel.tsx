/**
 * Panel de comparación: React simula recursos y Python los ejecuta en su kernel.
 * Muestra ambas cifras por separado para que el estudiante NO confunda
 * una estimación didáctica con la reserva real del gestor First-Fit.
 */
import React from 'react';
import { ArrowLeftRight, Cpu, Database, LockKeyhole, RefreshCw } from 'lucide-react';
import type { OSResourceSnapshot } from '../simulation/resources';
import type { PythonKernelStatus } from '../kernelBridge';

interface Props {
  snapshot: OSResourceSnapshot;
  status: PythonKernelStatus | null;
  onSync: () => void;
  syncing: boolean;
}

export function PythonKernelPanel({ snapshot, status, onSync, syncing }: Props) {
  const isConnected = Boolean(status?.connected);
  const mapped = Object.entries(status?.mappedPids ?? {});
  return <section className="autoos-kernel-bridge" aria-label="Integración del simulador con el kernel Python">
    <div className="autoos-kernel-bridge__header">
      <div>
        <small>INTEGRACIÓN DEL SISTEMA OPERATIVO / ETAPA 10</small>
        <h3><ArrowLeftRight size={20} /> REACT ↔ KERNEL PYTHON</h3>
        <p>La simulación estima recursos. Al sincronizar, el kernel Python crea procesos espejo,
          asigna RAM con First-Fit y ejecuta ciclos reales de su motor.</p>
      </div>
      <button type="button" onClick={onSync} disabled={!isConnected || syncing}
        title={isConnected ? 'Aplicar la carga actual al kernel Python' : 'Disponible en Streamlit, no en Vite local'}>
        <RefreshCw size={15} className={syncing ? 'autoos-kernel-bridge__spin' : ''} />
        {syncing ? 'SINCRONIZANDO…' : 'SINCRONIZAR KERNEL'}
      </button>
    </div>
    <div className="autoos-kernel-bridge__metrics">
      <div><span><Cpu size={15}/> TICK</span><strong>{snapshot.tick} <small>React</small></strong>
        <strong>{status?.tick ?? '—'} <small>Python</small></strong></div>
      <div><span><Database size={15}/> RAM USADA</span><strong>{snapshot.ramPhysicalMb} MB <small>Estimación React</small></strong>
        <strong>{status?.ramMb ?? '—'} MB <small>Reserva First-Fit Python</small></strong></div>
      <div><span>PROCESOS</span><strong>{snapshot.admittedCount} <small>React</small></strong>
        <strong>{mapped.length} <small>Espejo en Python</small></strong></div>
      <div><span>BATERÍA</span><strong>{snapshot.batteryPct.toFixed(1)} % <small>Modelo del vehículo</small></strong>
        <strong>{status?.lastBatteryPctReact != null ? status.lastBatteryPctReact.toFixed(1) + ' %' : '—'} <small>Última muestra recibida</small></strong></div>
    </div>
    <div className="autoos-kernel-bridge__notice" role="status">
      <LockKeyhole size={15}/>
      <span>{!isConnected ? 'Abre esta vista desde Streamlit para conectar con Python.' :
        status?.message ?? 'Conectado; presiona Sincronizar para aplicar los cambios.'}</span>
    </div>
    {status?.errors?.length ? <div className="autoos-kernel-bridge__errors" role="alert">{status.errors.join(' · ')}</div> : null}
    <p className="autoos-kernel-bridge__note">Los PID de React y Python son diferentes. Los procesos BMS/ADAS de arranque
      y la planificación Python siguen existiendo; por eso los totales pueden diferir. RBAC se valida en Python.</p>
  </section>;
}
