import React from 'react';
import { Process, AlgorithmType } from '../types/scheduler';
import { Cpu, Zap, Activity, AlertTriangle, ShieldCheck, Flame } from 'lucide-react';

interface CPUCoreCardProps {
  runningProcess: Process | null;
  algorithm: AlgorithmType;
  quantum: number;
  quantumRemaining: number;
  preemptedProcessId: number | null;
  contextSwitches: number;
  currentTime: number;
  isLowBatteryActive: boolean;
}

export const CPUCoreCard: React.FC<CPUCoreCardProps> = ({
  runningProcess,
  algorithm,
  quantum,
  quantumRemaining,
  preemptedProcessId,
  contextSwitches,
  isLowBatteryActive,
}) => {
  const isIdle = !runningProcess;
  const progressPercent = runningProcess
    ? ((runningProcess.burstTime - runningProcess.remainingTime) / runningProcess.burstTime) * 100
    : 0;

  return (
    <div className={`relative autoos-card rounded-2xl p-5 transition-all duration-300 shadow-xl ${
      runningProcess?.critical
        ? 'border-red-500/80 ring-2 ring-red-500/20'
        : isIdle
        ? ''
        : 'border-[var(--accent-primary)]/50 shadow-md'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between pb-3.5 border-b border-[var(--border-color)] mb-4">
        <div className="flex items-center gap-2.5">
          <div className={`p-2 rounded-xl ${
            runningProcess?.critical
              ? 'bg-red-500/20 text-red-400 border border-red-500/40 animate-pulse'
              : isIdle
              ? 'bg-[var(--bg-surface)] text-[var(--text-muted)] border border-[var(--border-color)]'
              : 'bg-[var(--accent-primary)]/15 text-[var(--accent-primary)] border border-[var(--accent-primary)]/30'
          }`}>
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-serif font-bold text-[var(--text-primary)]">
                Núcleo ASIL-D — Core 0 (AutoOS)
              </h3>
              <span className={`text-[10px] px-2 py-0.5 rounded-full font-mono font-bold ${
                isIdle
                  ? 'bg-[var(--bg-surface)] text-[var(--text-muted)] border border-[var(--border-color)]'
                  : 'bg-emerald-500/15 text-emerald-500 border border-emerald-500/30'
              }`}>
                {isIdle ? 'IDLE' : 'EJECUTANDO'}
              </span>
            </div>
            <p className="text-[11px] text-[var(--text-muted)]">
              Procesador RTOS de Tracción, Dirección y Seguridad
            </p>
          </div>
        </div>

        {/* Algorithm info badge */}
        <div className="text-right">
          <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[var(--accent-primary)] bg-[var(--accent-primary)]/10 px-2.5 py-1 rounded-xl border border-[var(--accent-primary)]/30">
            {algorithm}
          </span>
          {algorithm === 'RR' && (
            <div className="text-[10px] text-[var(--text-muted)] font-mono mt-1">
              Quantum: <strong className="text-amber-500">{quantumRemaining}s</strong> / {quantum}s
            </div>
          )}
        </div>
      </div>

      {/* Preemption Flash Banner */}
      {preemptedProcessId && (
        <div className="mb-3.5 px-3.5 py-2 bg-amber-500/15 border border-amber-500/30 rounded-xl flex items-center gap-2 text-xs text-amber-500 animate-bounce font-medium">
          <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0" />
          <span>¡Desalojo Preemptivo! Se ejecutó conmutación forzosa de CPU.</span>
        </div>
      )}

      {/* Main Body */}
      {runningProcess ? (
        <div className="space-y-3.5">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: runningProcess.color }}
                />
                <h4 className="text-base font-bold text-[var(--text-primary)] flex items-center gap-1.5">
                  {runningProcess.name}
                  {runningProcess.critical && (
                    <span className="px-2 py-0.5 rounded-full text-[10px] bg-red-500/20 text-red-500 border border-red-500/40 font-mono font-bold flex items-center gap-1">
                      <Flame className="w-3 h-3" /> ASIL-D
                    </span>
                  )}
                </h4>
              </div>
              <div className="flex items-center gap-2 text-xs text-[var(--text-muted)] mt-1 font-mono">
                <span>PID: <strong className="text-[var(--text-primary)]">{runningProcess.pid}</strong></span>
                <span>•</span>
                <span>Prioridad: <strong className={runningProcess.priority === 1 ? 'text-red-500' : 'text-[var(--accent-primary)]'}>{runningProcess.priority}</strong></span>
                <span>•</span>
                <span className="capitalize">{runningProcess.category}</span>
              </div>
            </div>

            {/* Power usage */}
            <div className="text-right text-xs font-mono">
              <div className="flex items-center justify-end gap-1 text-amber-500 font-bold">
                <Zap className="w-3.5 h-3.5" />
                <span>{runningProcess.powerConsumptionWatts}W</span>
              </div>
              <span className="text-[10px] text-[var(--text-muted)]">
                {isLowBatteryActive ? '⚡ Modo Eco' : 'Potencia Nominal'}
              </span>
            </div>
          </div>

          {/* Burst progress */}
          <div>
            <div className="flex justify-between text-xs font-mono text-[var(--text-muted)] mb-1.5">
              <span>Progreso de Ráfaga:</span>
              <span>
                <strong className="text-[var(--text-primary)]">
                  {runningProcess.burstTime - runningProcess.remainingTime}s
                </strong>{' '}
                / {runningProcess.burstTime}s ({Math.round(progressPercent)}%)
              </span>
            </div>
            <div className="w-full bg-[var(--bg-surface)] rounded-full h-2.5 overflow-hidden border border-[var(--border-color)]">
              <div
                className="h-full rounded-full transition-all duration-300 relative"
                style={{
                  width: `${progressPercent}%`,
                  backgroundColor: runningProcess.color,
                }}
              >
                <div className="absolute inset-0 bg-white/20 animate-pulse" />
              </div>
            </div>
          </div>

          {/* Quick specs */}
          <div className="grid grid-cols-3 gap-2.5 pt-1 text-[11px] font-mono">
            <div className="autoos-surface p-2.5 rounded-xl">
              <span className="text-[var(--text-muted)] block text-[9px] uppercase">Llegada (AT)</span>
              <strong className="text-[var(--text-primary)]">{runningProcess.arrivalTime}s</strong>
            </div>
            <div className="autoos-surface p-2.5 rounded-xl">
              <span className="text-[var(--text-muted)] block text-[9px] uppercase">Restante (RT)</span>
              <strong className="text-amber-500">{runningProcess.remainingTime}s</strong>
            </div>
            <div className="autoos-surface p-2.5 rounded-xl">
              <span className="text-[var(--text-muted)] block text-[9px] uppercase">T. Respuesta</span>
              <strong className="text-emerald-500">
                {runningProcess.responseTime !== undefined ? `${runningProcess.responseTime}s` : '-'}
              </strong>
            </div>
          </div>
        </div>
      ) : (
        <div className="py-7 flex flex-col items-center justify-center text-center">
          <Activity className="w-8 h-8 mb-2 opacity-40 animate-pulse text-[var(--accent-primary)]" />
          <p className="text-xs font-semibold text-[var(--text-primary)]">Núcleo en Reposo (CPU IDLE)</p>
          <p className="text-[11px] text-[var(--text-muted)] max-w-xs mt-0.5">
            Esperando nuevos procesos listos en la cola de despacho...
          </p>
        </div>
      )}

      {/* Footer Stats */}
      <div className="flex items-center justify-between pt-3.5 mt-3.5 border-t border-[var(--border-color)] text-[10px] font-mono text-[var(--text-muted)]">
        <span className="flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-[var(--accent-primary)]" />
          Conmutaciones de Contexto: <strong className="text-[var(--text-primary)]">{contextSwitches}</strong>
        </span>
        <span>
          RTOS Kernel v2.4.1
        </span>
      </div>
    </div>
  );
};
