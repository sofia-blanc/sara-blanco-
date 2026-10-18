import React, { useRef, useEffect } from 'react';
import { GanttSlot, Process } from '../types/scheduler';
import { Clock, ShieldAlert, Cpu } from 'lucide-react';

interface GanttChartProps {
  slots: GanttSlot[];
  currentTime: number;
  totalTime: number;
  processes: Process[];
}

export const GanttChart: React.FC<GanttChartProps> = ({
  slots,
  currentTime,
  totalTime,
}) => {
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollLeft = scrollContainerRef.current.scrollWidth;
    }
  }, [currentTime, slots.length]);

  const maxTime = Math.max(currentTime, totalTime, 14);
  const unitWidth = 36;

  return (
    <div className="autoos-card rounded-2xl p-5 shadow-xl transition-all">
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[var(--border-color)] mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-[var(--accent-primary)]/15 text-[var(--accent-primary)] border border-[var(--accent-primary)]/30 shadow-sm">
            <Clock className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-serif font-bold text-[var(--text-primary)] tracking-wide">
              Diagrama de Gantt — Despacho Temporal de CPU (RTOS)
            </h3>
            <p className="text-[11px] text-[var(--text-muted)]">
              Trazabilidad en tiempo real de intervalos de ejecución y conmutaciones de proceso
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-2 px-3 py-1 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-color)] text-[var(--text-primary)]">
            <span className="w-2 h-2 rounded-full bg-[var(--accent-primary)] animate-ping"></span>
            Reloj: <strong className="text-[var(--accent-primary)] text-sm">t = {currentTime}s</strong>
          </div>
          <div className="flex items-center gap-3 text-[11px] text-[var(--text-muted)] hidden sm:flex">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded bg-red-500 shadow-sm"></span> P1 Crítico
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded bg-[var(--accent-primary)] shadow-sm"></span> Tarea Normal
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded bg-[var(--bg-surface)] border border-[var(--border-color)]"></span> CPU Idle
            </span>
          </div>
        </div>
      </div>

      {/* Gantt Timeline Area */}
      <div
        ref={scrollContainerRef}
        className="overflow-x-auto pb-4 pt-1"
        style={{ minHeight: '135px' }}
      >
        <div style={{ minWidth: `${Math.max(maxTime * unitWidth + 80, 640)}px` }} className="relative select-none">
          {/* Gantt Block Strip */}
          <div className="flex h-16 rounded-xl bg-[var(--bg-surface)] border border-[var(--border-color)] overflow-hidden relative shadow-inner">
            {slots.length === 0 ? (
              <div className="flex-1 flex items-center justify-center text-xs text-[var(--text-muted)] italic">
                <Cpu className="w-4 h-4 mr-2 opacity-50 animate-pulse text-[var(--accent-primary)]" />
                Inicie la planificación para visualizar la traza de despacho...
              </div>
            ) : (
              slots.map((slot) => {
                const width = (slot.end - slot.start) * unitWidth;
                return (
                  <div
                    key={slot.id}
                    title={`${slot.processName} | Intervalo: [${slot.start}s - ${slot.end}s] ${slot.isCritical ? '(CRÍTICO ASIL-D)' : ''}`}
                    style={{
                      width: `${width}px`,
                      backgroundColor: slot.isIdle ? 'var(--bg-base)' : slot.color,
                    }}
                    className={`relative flex flex-col items-center justify-center h-full px-1 border-r border-[var(--border-color)]/60 transition-all duration-150 ${
                      slot.isCritical
                        ? 'ring-2 ring-red-400 ring-inset shadow-[0_0_14px_rgba(239,68,68,0.5)] z-10'
                        : ''
                    }`}
                  >
                    {slot.isCritical && (
                      <ShieldAlert className="w-3.5 h-3.5 text-white absolute top-1 right-1 drop-shadow animate-bounce" />
                    )}
                    <span className="text-[11px] font-bold text-white tracking-tight drop-shadow truncate max-w-full">
                      {slot.isIdle ? 'IDLE' : `P${slot.processId}`}
                    </span>
                    <span className="text-[9px] text-white/90 font-mono tracking-tighter truncate max-w-full">
                      {slot.end - slot.start}s
                    </span>
                  </div>
                );
              })
            )}

            {/* Playhead Indicator */}
            <div
              style={{ left: `${currentTime * unitWidth}px` }}
              className="absolute top-0 bottom-0 w-0.5 bg-[var(--accent-primary)] z-20 shadow-[0_0_10px_var(--accent-primary)] pointer-events-none transition-all duration-150"
            >
              <div className="w-2.5 h-2.5 -ml-1 -top-1 absolute rounded-full bg-[var(--accent-primary)] border-2 border-[var(--bg-card)]"></div>
            </div>
          </div>

          {/* Time axis ruler */}
          <div className="flex relative mt-2 text-[10px] font-mono text-[var(--text-muted)]">
            {Array.from({ length: maxTime + 1 }).map((_, i) => (
              <div
                key={i}
                style={{
                  position: 'absolute',
                  left: `${i * unitWidth}px`,
                  transform: 'translateX(-50%)',
                }}
                className="flex flex-col items-center"
              >
                <div
                  className={`w-px ${
                    i === currentTime ? 'h-3 bg-[var(--accent-primary)]' : 'h-2 bg-[var(--border-color)]'
                  }`}
                />
                <span
                  className={`mt-0.5 ${
                    i === currentTime ? 'text-[var(--accent-primary)] font-bold' : ''
                  }`}
                >
                  {i}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
