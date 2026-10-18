import React, { useMemo } from 'react';
import { Process, AlgorithmType } from '../types/scheduler';
import { runStaticSimulation, getAlgorithmName } from '../utils/schedulerEngine';
import { BarChart3, X, Award, TrendingUp } from 'lucide-react';

interface AlgorithmComparisonModalProps {
  isOpen: boolean;
  onClose: () => void;
  processes: Process[];
  quantum: number;
}

export const AlgorithmComparisonModal: React.FC<AlgorithmComparisonModalProps> = ({
  isOpen,
  onClose,
  processes,
  quantum,
}) => {
  if (!isOpen) return null;

  const comparisonData = useMemo(() => {
    const algorithms: AlgorithmType[] = ['FCFS', 'RR', 'PRIORITY', 'PRIORITY_PREEMPTIVE'];
    return algorithms.map((alg) => {
      const { state, metrics } = runStaticSimulation(processes, alg, quantum);
      return {
        algorithm: alg,
        name: getAlgorithmName(alg),
        metrics,
        state,
      };
    });
  }, [processes, quantum]);

  const bestWait = Math.min(...comparisonData.map((d) => d.metrics.averageWaitingTime));
  const bestTAT = Math.min(...comparisonData.map((d) => d.metrics.averageTurnaroundTime));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-4xl max-h-[90vh] autoos-card rounded-3xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-[var(--border-color)] autoos-surface">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-[var(--accent-primary)]/15 text-[var(--accent-primary)] border border-[var(--accent-primary)]/30">
              <BarChart3 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-serif font-bold text-[var(--text-primary)]">
                Comparativa de Algoritmos de Planificación
              </h3>
              <p className="text-xs text-[var(--text-muted)]">
                Evaluación con la carga activa ({processes.length} procesos)
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-[var(--text-muted)] hover:text-[var(--text-primary)] autoos-surface transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3.5">
            {comparisonData.map((item) => {
              const isBestWait = item.metrics.averageWaitingTime === bestWait;
              const isBestTAT = item.metrics.averageTurnaroundTime === bestTAT;

              return (
                <div
                  key={item.algorithm}
                  className={`p-4 rounded-2xl border relative flex flex-col justify-between ${
                    isBestWait
                      ? 'autoos-card border-[var(--accent-primary)] ring-1 ring-[var(--accent-primary)]/40 shadow-md'
                      : 'autoos-surface'
                  }`}
                >
                  {isBestWait && (
                    <span className="absolute -top-3 right-3 px-2.5 py-0.5 rounded-full text-[9px] font-bold bg-[var(--accent-primary)] text-white font-mono flex items-center gap-1 shadow-sm">
                      <Award className="w-3 h-3" /> MENOR ESPERA
                    </span>
                  )}

                  <div>
                    <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[var(--accent-primary)] block mb-1">
                      {item.algorithm}
                    </span>
                    <h4 className="text-xs font-bold text-[var(--text-primary)] line-clamp-2 h-8">
                      {item.name}
                    </h4>

                    <div className="space-y-2.5 mt-3 pt-3 border-t border-[var(--border-color)] text-xs font-mono">
                      <div className="flex justify-between items-center">
                        <span className="text-[var(--text-muted)] text-[11px]">T. Espera Prom:</span>
                        <strong className={isBestWait ? 'text-[var(--accent-primary)] font-bold text-sm' : 'text-[var(--text-primary)]'}>
                          {item.metrics.averageWaitingTime}s
                        </strong>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-[var(--text-muted)] text-[11px]">T. Retorno Prom:</span>
                        <strong className={isBestTAT ? 'text-emerald-500 font-bold' : 'text-[var(--text-primary)]'}>
                          {item.metrics.averageTurnaroundTime}s
                        </strong>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-[var(--text-muted)] text-[11px]">Conmutaciones:</span>
                        <strong className="text-[var(--text-primary)]">
                          {item.metrics.contextSwitches}
                        </strong>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-[var(--text-muted)] text-[11px]">Uso CPU:</span>
                        <strong className="text-emerald-500 font-bold">
                          {item.metrics.cpuUtilization}%
                        </strong>
                      </div>
                    </div>
                  </div>

                  <div className="mt-3.5 pt-2.5 border-t border-[var(--border-color)]">
                    <span className="text-[9px] text-[var(--text-muted)] font-mono block mb-1.5">Traza Gantt:</span>
                    <div className="flex h-4 rounded-lg overflow-hidden bg-[var(--bg-base)] border border-[var(--border-color)]">
                      {item.state.ganttSlots.map((slot, sIdx) => {
                        const duration = slot.end - slot.start;
                        return (
                          <div
                            key={sIdx}
                            style={{
                              flex: duration,
                              backgroundColor: slot.isIdle ? 'var(--border-color)' : slot.color,
                            }}
                            title={`P${slot.processId || 'Idle'} (${duration}s)`}
                            className="h-full border-r border-[var(--border-color)]/40"
                          />
                        );
                      })}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="p-4 rounded-2xl autoos-surface space-y-2 text-xs text-[var(--text-primary)]">
            <h4 className="font-serif font-bold text-[var(--text-primary)] flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-[var(--accent-primary)]" />
              Conclusiones Teóricas para Sistemas Operativos Automotrices:
            </h4>
            <ul className="list-disc list-inside space-y-1 text-[var(--text-muted)] text-[11px] leading-relaxed">
              <li>
                <strong className="text-[var(--text-primary)]">FCFS:</strong> No recomendado para sistemas automotrices porque tareas críticas de frenado o dirección pueden quedar bloqueadas detrás de procesos pesados de infoentretenimiento (*Efecto Convoy*).
              </li>
              <li>
                <strong className="text-[var(--text-primary)]">Round Robin (q = {quantum}s):</strong> Excelente para tareas interactivas como la pantalla táctil y el chat de cabina, pero con mayor sobrecarga de conmutaciones.
              </li>
              <li>
                <strong className="text-[var(--text-primary)]">Priority Scheduling (Apropiativo):</strong> Es la política obligatoria según el estándar **ASIL-D / ISO 26262**. Permite desalojar al instante la CPU para atender frenado autónomo (AEB) y fallo de servomotores.
              </li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[var(--border-color)] autoos-surface flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-[var(--accent-primary)] text-white text-xs font-semibold shadow-sm transition"
          >
            Cerrar Comparativa
          </button>
        </div>
      </div>
    </div>
  );
};
