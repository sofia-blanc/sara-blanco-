import React from 'react';
import { Process, AlgorithmType } from '../types/scheduler';
import { ListOrdered, ShieldAlert, ArrowRight, PauseCircle } from 'lucide-react';

interface QueueVisualizerProps {
  readyQueue: Process[];
  algorithm: AlgorithmType;
  suspendedProcesses: Process[];
}

export const QueueVisualizer: React.FC<QueueVisualizerProps> = ({
  readyQueue,
  algorithm,
  suspendedProcesses,
}) => {
  const getPolicyExplanation = () => {
    switch (algorithm) {
      case 'FCFS':
        return 'Política FIFO: Los procesos se despachan estrictamente en orden de llegada (Tiempo de Llegada).';
      case 'RR':
        return 'Política Circular: Cada proceso recibe una cuota de tiempo (Quantum). Si no termina, se reencola al final.';
      case 'PRIORITY':
        return 'Política por Prioridad No Apropiativa: Prioridad 1 (Crítica) tiene preferencia sobre 5. Desempate FIFO.';
      case 'PRIORITY_PREEMPTIVE':
        return 'Política por Prioridad Apropiativa: Un proceso con mayor prioridad desaloja de inmediato al que está en CPU.';
    }
  };

  return (
    <div className="autoos-card rounded-2xl p-5 shadow-xl">
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3.5 border-b border-[var(--border-color)] mb-3.5">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-[var(--accent-primary)]/15 text-[var(--accent-primary)] border border-[var(--accent-primary)]/30">
            <ListOrdered className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-serif font-bold text-[var(--text-primary)]">
              Cola de Listos (Ready Queue)
            </h3>
            <p className="text-[11px] text-[var(--text-muted)]">
              {readyQueue.length} proceso{readyQueue.length === 1 ? '' : 's'} en espera de despacho
            </p>
          </div>
        </div>

        <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-[var(--bg-surface)] text-[var(--accent-primary)] border border-[var(--border-color)]">
          {algorithm}
        </span>
      </div>

      {/* Policy explanation notice */}
      <div className="mb-3.5 px-3.5 py-2 autoos-surface rounded-xl text-[11px] text-[var(--text-muted)] flex items-center gap-2 font-mono">
        <ArrowRight className="w-3.5 h-3.5 text-[var(--accent-primary)] shrink-0" />
        <span>{getPolicyExplanation()}</span>
      </div>

      {/* Queue items */}
      {readyQueue.length === 0 ? (
        <div className="py-7 text-center text-xs text-[var(--text-muted)] italic autoos-surface rounded-xl border border-dashed border-[var(--border-color)]">
          La cola de listos está vacía en este instante.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5">
          {readyQueue.map((proc, index) => {
            const isNext = index === 0;
            return (
              <div
                key={proc.pid}
                className={`relative p-3 rounded-xl border transition-all ${
                  isNext
                    ? 'autoos-card border-[var(--accent-primary)] ring-1 ring-[var(--accent-primary)]/50 shadow-md'
                    : 'autoos-surface hover:border-[var(--accent-primary)]/40'
                }`}
              >
                {isNext && (
                  <span className="absolute -top-2.5 right-2 text-[9px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-[var(--accent-primary)] text-white font-mono shadow-sm">
                    Próximo a CPU
                  </span>
                )}
                <div className="flex items-start justify-between gap-1 mb-2">
                  <div className="flex items-center gap-2">
                    <span
                      className="w-2.5 h-2.5 rounded-full shrink-0"
                      style={{ backgroundColor: proc.color }}
                    />
                    <h5 className="text-xs font-bold text-[var(--text-primary)] truncate max-w-[130px]">
                      {proc.name}
                    </h5>
                  </div>
                  <span className="text-[10px] font-mono text-[var(--text-muted)]">
                    P{proc.pid}
                  </span>
                </div>

                <div className="flex items-center justify-between text-[10px] font-mono text-[var(--text-muted)] pt-1.5 border-t border-[var(--border-color)]">
                  <span className="flex items-center gap-1">
                    Prioridad:{' '}
                    <strong className={proc.priority === 1 ? 'text-red-500 font-bold' : 'text-[var(--text-primary)]'}>
                      {proc.priority}
                    </strong>
                    {proc.critical && <ShieldAlert className="w-3 h-3 text-red-500 inline" />}
                  </span>
                  <span>
                    Ráfaga:{' '}
                    <strong className="text-amber-500">{proc.remainingTime}s</strong>
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Suspended Processes Section */}
      {suspendedProcesses.length > 0 && (
        <div className="mt-4 pt-3.5 border-t border-[var(--border-color)]">
          <div className="flex items-center gap-1.5 text-xs text-amber-500 font-bold mb-2">
            <PauseCircle className="w-3.5 h-3.5" />
            <span>Procesos Suspendidos ({suspendedProcesses.length}) — Modo Ahorro de Energía (Batería Baja)</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {suspendedProcesses.map((sp) => (
              <span
                key={sp.pid}
                className="text-[10px] font-mono px-2.5 py-1 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-600 dark:text-amber-300 flex items-center gap-1.5 font-medium"
              >
                <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                {sp.name} (P{sp.pid}) — {sp.powerConsumptionWatts}W ahorrados
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
