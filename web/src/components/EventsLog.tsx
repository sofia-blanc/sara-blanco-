import React from 'react';
import { SimulationEvent } from '../types/scheduler';
import { ScrollText, ShieldAlert, Zap, Cpu, CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react';

interface EventsLogProps {
  events: SimulationEvent[];
}

export const EventsLog: React.FC<EventsLogProps> = ({ events }) => {
  const getEventIcon = (type: SimulationEvent['type']) => {
    switch (type) {
      case 'PREEMPTION':
        return <AlertTriangle className="w-3.5 h-3.5 text-amber-500 shrink-0" />;
      case 'CRITICAL_INJECT':
        return <ShieldAlert className="w-3.5 h-3.5 text-red-500 shrink-0 animate-bounce" />;
      case 'BATTERY_ALERT':
        return <Zap className="w-3.5 h-3.5 text-amber-500 shrink-0" />;
      case 'DISPATCH':
        return <Cpu className="w-3.5 h-3.5 text-[var(--accent-primary)] shrink-0" />;
      case 'COMPLETION':
        return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />;
      default:
        return <ArrowRight className="w-3.5 h-3.5 text-[var(--text-muted)] shrink-0" />;
    }
  };

  return (
    <div className="autoos-card rounded-2xl p-5 shadow-xl flex flex-col h-[320px]">
      <div className="flex items-center justify-between pb-3 border-b border-[var(--border-color)] mb-2.5">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-[var(--accent-primary)]/15 text-[var(--accent-primary)] border border-[var(--accent-primary)]/30">
            <ScrollText className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-serif font-bold text-[var(--text-primary)]">
              Bitácora de Auditoría (Kernel Log)
            </h3>
            <p className="text-[11px] text-[var(--text-muted)]">
              Eventos cronológicos inmutables de despacho y conmutación
            </p>
          </div>
        </div>
        <span className="text-[10px] font-mono text-[var(--text-muted)]">
          {events.length} evento{events.length === 1 ? '' : 's'}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2 pr-1 font-mono text-xs">
        {events.length === 0 ? (
          <div className="py-12 text-center text-[var(--text-muted)] italic">
            Esperando eventos del despachador...
          </div>
        ) : (
          events.map((evt) => (
            <div
              key={evt.id}
              className={`p-2.5 rounded-xl border flex items-start gap-2.5 transition-all ${
                evt.severity === 'critical'
                  ? 'bg-red-500/15 border-red-500/30 text-red-600 dark:text-red-300'
                  : evt.severity === 'warning'
                  ? 'bg-amber-500/15 border-amber-500/30 text-amber-600 dark:text-amber-300'
                  : evt.severity === 'success'
                  ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-600 dark:text-emerald-300'
                  : 'autoos-surface text-[var(--text-primary)]'
              }`}
            >
              <div className="mt-0.5">{getEventIcon(evt.type)}</div>
              <div className="flex-1 leading-tight">
                <div className="flex items-center justify-between text-[10px] text-[var(--text-muted)] mb-1">
                  <span className="font-bold text-[var(--accent-primary)]">t = {evt.time}s</span>
                  <span>{evt.timestamp}</span>
                </div>
                <p className="text-[11px]">{evt.message}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
