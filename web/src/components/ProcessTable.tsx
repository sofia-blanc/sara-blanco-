import React, { useState } from 'react';
import { Process, ProcessState, UserRole } from '../types/scheduler';
import { Table, ShieldAlert, Pause, Play, Trash2, CheckCircle } from 'lucide-react';

interface ProcessTableProps {
  processes: Process[];
  onToggleSuspend: (pid: number) => void;
  onTerminate: (pid: number) => void;
  currentTime: number;
  userRole: UserRole;
  onRoleRestricted: (action: string) => void;
}

export const ProcessTable: React.FC<ProcessTableProps> = ({
  processes,
  onToggleSuspend,
  onTerminate,
  userRole,
  onRoleRestricted,
}) => {
  const [filterState, setFilterState] = useState<string>('TODOS');

  const filteredProcesses = processes.filter((p) => {
    if (filterState === 'TODOS') return true;
    return p.state === filterState;
  });

  const handleActionSuspend = (proc: Process) => {
    if (userRole === 'pasajero') {
      onRoleRestricted('Pausar / Reanudar Procesos en la CPU');
      return;
    }
    onToggleSuspend(proc.pid);
  };

  const handleActionTerminate = (proc: Process) => {
    if (userRole === 'pasajero') {
      onRoleRestricted('Terminar Procesos del Sistema (SIGKILL)');
      return;
    }
    if (proc.critical && userRole !== 'mecanico') {
      onRoleRestricted(`Abortar Proceso Crítico ASIL-D '${proc.name}' (Solo Mecánico / Nivel 10)`);
      return;
    }
    onTerminate(proc.pid);
  };

  const getStateBadge = (state: ProcessState) => {
    switch (state) {
      case 'EJECUTANDO':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-[var(--accent-primary)]/20 text-[var(--accent-primary)] border border-[var(--accent-primary)]/40 animate-pulse">
            EJECUTANDO
          </span>
        );
      case 'LISTO':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-indigo-500/15 text-indigo-600 dark:text-indigo-300 border border-indigo-500/30">
            LISTO
          </span>
        );
      case 'NUEVO':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono text-[var(--text-muted)] bg-[var(--bg-surface)] border border-[var(--border-color)]">
            NUEVO
          </span>
        );
      case 'SUSPENDIDO':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-amber-500/20 text-amber-600 dark:text-amber-300 border border-amber-500/40">
            SUSPENDIDO
          </span>
        );
      case 'TERMINADO':
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-emerald-500/20 text-emerald-600 dark:text-emerald-300 border border-emerald-500/40">
            TERMINADO
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="autoos-card rounded-2xl p-5 shadow-xl">
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3.5 border-b border-[var(--border-color)] mb-3.5">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-[var(--accent-primary)]/15 text-[var(--accent-primary)] border border-[var(--accent-primary)]/30">
            <Table className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-serif font-bold text-[var(--text-primary)]">
              Tabla de Bloques de Control de Proceso (PCB)
            </h3>
            <p className="text-[11px] text-[var(--text-muted)]">
              Estructura formal de procesos del Kernel AutoOS y validación de permisos RBAC
            </p>
          </div>
        </div>

        {/* Filter buttons */}
        <div className="flex items-center gap-1 autoos-surface p-1 rounded-xl text-[11px] font-mono">
          {['TODOS', 'LISTO', 'EJECUTANDO', 'SUSPENDIDO', 'TERMINADO'].map((s) => (
            <button
              key={s}
              onClick={() => setFilterState(s)}
              className={`px-2.5 py-1 rounded-lg transition ${
                filterState === s
                  ? 'bg-[var(--accent-primary)] text-white font-bold shadow-sm'
                  : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead className="bg-[var(--bg-surface)] text-[10px] text-[var(--text-muted)] uppercase tracking-wider border-b border-[var(--border-color)]">
            <tr>
              <th className="py-2.5 px-3">PID</th>
              <th className="py-2.5 px-3">Nombre del Proceso</th>
              <th className="py-2.5 px-3">Estado</th>
              <th className="py-2.5 px-3">Prioridad</th>
              <th className="py-2.5 px-3 text-center">Llegada (AT)</th>
              <th className="py-2.5 px-3 text-center">Ráfaga (BT)</th>
              <th className="py-2.5 px-3 text-center">Restante</th>
              <th className="py-2.5 px-3 text-center">Fin (CT)</th>
              <th className="py-2.5 px-3 text-center">Retorno (TAT)</th>
              <th className="py-2.5 px-3 text-center">Espera (WT)</th>
              <th className="py-2.5 px-3 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--border-color)]/60">
            {filteredProcesses.length === 0 ? (
              <tr>
                <td colSpan={11} className="py-6 text-center text-[var(--text-muted)] italic">
                  No hay procesos con el filtro seleccionado.
                </td>
              </tr>
            ) : (
              filteredProcesses.map((proc) => (
                <tr
                  key={proc.pid}
                  className={`hover:bg-[var(--bg-card-hover)] transition-colors ${
                    proc.state === 'EJECUTANDO'
                      ? 'bg-[var(--accent-primary)]/10'
                      : proc.critical
                      ? 'bg-red-500/10'
                      : ''
                  }`}
                >
                  <td className="py-2.5 px-3 font-bold text-[var(--text-primary)]">
                    P{proc.pid}
                  </td>
                  <td className="py-2.5 px-3">
                    <div className="flex items-center gap-2">
                      <span
                        className="w-2.5 h-2.5 rounded-full shrink-0"
                        style={{ backgroundColor: proc.color }}
                      />
                      <span className="font-semibold text-[var(--text-primary)]">
                        {proc.name}
                      </span>
                      {proc.critical && (
                        <span title="Proceso Crítico ASIL-D">
                          <ShieldAlert className="w-3.5 h-3.5 text-red-500 shrink-0" />
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-2.5 px-3">
                    {getStateBadge(proc.state)}
                  </td>
                  <td className="py-2.5 px-3">
                    <span className={`px-2 py-0.5 rounded-full text-[11px] font-bold ${
                      proc.priority === 1
                        ? 'bg-red-500/20 text-red-500 border border-red-500/30'
                        : proc.priority === 2
                        ? 'bg-orange-500/20 text-orange-500'
                        : 'autoos-surface text-[var(--text-muted)]'
                    }`}>
                      {proc.priority === 1 ? '1 (Crítico)' : proc.priority}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-center text-[var(--text-primary)]">{proc.arrivalTime}s</td>
                  <td className="py-2.5 px-3 text-center text-[var(--text-primary)]">{proc.burstTime}s</td>
                  <td className="py-2.5 px-3 text-center font-bold text-amber-500">
                    {proc.state === 'TERMINADO' ? '0s' : `${proc.remainingTime}s`}
                  </td>
                  <td className="py-2.5 px-3 text-center text-[var(--text-primary)]">
                    {proc.completionTime !== undefined ? `${proc.completionTime}s` : '-'}
                  </td>
                  <td className="py-2.5 px-3 text-center text-[var(--text-primary)]">
                    {proc.turnaroundTime ? `${proc.turnaroundTime}s` : '-'}
                  </td>
                  <td className="py-2.5 px-3 text-center text-[var(--text-primary)]">
                    {proc.waitingTime ? `${proc.waitingTime}s` : proc.state === 'TERMINADO' ? '0s' : '-'}
                  </td>
                  <td className="py-2.5 px-3 text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      {proc.state !== 'TERMINADO' && (
                        <>
                          <button
                            onClick={() => handleActionSuspend(proc)}
                            title={proc.state === 'SUSPENDIDO' ? 'Reanudar' : 'Suspender'}
                            className="p-1.5 rounded-lg autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] transition"
                          >
                            {proc.state === 'SUSPENDIDO' ? (
                              <Play className="w-3.5 h-3.5 text-emerald-500" />
                            ) : (
                              <Pause className="w-3.5 h-3.5 text-amber-500" />
                            )}
                          </button>
                          <button
                            onClick={() => handleActionTerminate(proc)}
                            title="Finalizar (SIGKILL)"
                            className="p-1.5 rounded-lg autoos-surface hover:bg-red-500/20 text-[var(--text-muted)] hover:text-red-500 transition"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </>
                      )}
                      {proc.state === 'TERMINADO' && (
                        <CheckCircle className="w-4 h-4 text-emerald-500" />
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
