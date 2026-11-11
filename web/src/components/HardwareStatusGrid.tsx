import React from 'react';
import {
  Navigation,
  Eye,
  Radio,
  Disc,
  Flame,
  ShieldAlert,
  Car,
  Wifi,
  Cpu,
  Monitor,
  Thermometer,
  CheckCircle,
  AlertTriangle,
  RotateCcw,
  Wrench,
  Zap,
} from 'lucide-react';
import { VehicleDevice, UserRole } from '../types/scheduler';
import { CriticalProcessSimulator } from './CriticalProcessSimulator';



interface HardwareStatusGridProps {
  devices: VehicleDevice[];
  onResetDevice: (deviceCode: string) => void;
  onResetAllDevices: () => void;
  onTriggerQuickFault: (deviceCode: string) => void;
  userRole: UserRole;
  onRoleRestricted: (action: string) => void;
  // New callbacks for fault injection and time
  onInjectCriticalProcess: (
    proc: Omit<Process, 'waitingTime' | 'turnaroundTime'>,
    deviceCode?: string,
    dtc?: string,
    failureMode?: string
  ) => void;
  onResetAllScenarios: () => void;
  currentTime: number;
}

export const HARDWARE_DEVICE_ICONS: Record<string, React.FC<{ className?: string }>> = {
  DEV_GPS_01: Navigation,
  DEV_CAM_FRONT: Eye,
  DEV_LIDAR_01: Radio,
  DEV_RADAR_01: Disc,
  DEV_BATTERY_BMS: Flame,
  DEV_ACT_BRAKE: Disc,
  DEV_ACT_STEER: Car,
  DEV_COM_V2X: Wifi,
  DEV_GATEWAY_CAN: Cpu,
  DEV_INFOTAINMENT: Monitor,
  DEV_HVAC_CLIMA: Thermometer,
};

export const HardwareStatusGrid: React.FC<HardwareStatusGridProps> = ({
  devices,
  onResetDevice,
  onResetAllDevices,
  onTriggerQuickFault,
  userRole,
  onRoleRestricted,
  // New callbacks for fault injection and time
  onInjectCriticalProcess,
  onResetAllScenarios,
  currentTime,
}) => {
  const canModify = userRole === 'mecanico';

  // Calculate overall health
  const totalHealth = devices.reduce((acc, d) => acc + d.health, 0);
  const averageHealth = Math.round(totalHealth / devices.length);

  const faultCount = devices.filter((d) => d.status === 'falla' || d.status === 'desconectado').length;
  const degradedCount = devices.filter((d) => d.status === 'degradado').length;

  return (
    <div className="autoos-card rounded-2xl p-5 shadow-xl space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[var(--border-color)]">
        <div className="flex items-center gap-2.5">
          <div className={`p-2 rounded-xl border ${
            faultCount > 0
              ? 'bg-red-500/15 text-red-500 border-red-500/30 animate-pulse'
              : degradedCount > 0
              ? 'bg-amber-500/15 text-amber-500 border-amber-500/30'
              : 'bg-emerald-500/15 text-emerald-500 border-emerald-500/30'
          }`}>
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-serif font-bold text-[var(--text-primary)]">
                Matriz de Salud de Hardware y Subsistemas Vehiculares
              </h3>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-bold uppercase ${
                faultCount > 0
                  ? 'bg-red-600 text-white animate-pulse'
                  : degradedCount > 0
                  ? 'bg-amber-500 text-white'
                  : 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
              }`}>
                {faultCount > 0
                  ? `🚨 ${faultCount} Falla(s) Crítica(s)`
                  : degradedCount > 0
                  ? `⚠️ ${degradedCount} Degradado(s)`
                  : '✓ Todos los Sistemas Nominales'}
              </span>
            </div>
            <p className="text-[11px] text-[var(--text-muted)]">
              Supervisión en tiempo real de buses CAN-FD, Automotive Ethernet y LIN con inyección bidireccional
            </p>
          </div>
        </div>

        {/* Global Reset Action */}
        <div className="flex items-center gap-3">
          <div className="text-right font-mono hidden sm:block">
            <span className="text-[10px] text-[var(--text-muted)] uppercase block">Salud Global:</span>
            <strong className={`text-base font-bold ${
              averageHealth < 60 ? 'text-red-500' : averageHealth < 85 ? 'text-amber-500' : 'text-emerald-500'
            }`}>
              {averageHealth}%
            </strong>
          </div>

          <button
            onClick={() => {
              if (!canModify) {
                onRoleRestricted('Restablecer Parámetros de Hardware y Diagnóstico OBD-II');
                return;
              }
              onResetAllDevices();
            }}
            className="px-3.5 py-2 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold flex items-center gap-1.5 transition font-mono shadow-sm"
          >
            <RotateCcw className="w-3.5 h-3.5 text-[var(--accent-primary)]" />
            <span>Restablecer Todo a Nominal</span>
          </button>
        </div>
      </div>

      {/* Grid of Devices */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
        {devices.map((dev) => {
          const IconComp = HARDWARE_DEVICE_ICONS[dev.code] || Cpu;
          const isFailing = dev.status === 'falla' || dev.status === 'desconectado';
          const isDegraded = dev.status === 'degradado';

          return (
            <div
              key={dev.id}
              className={`p-3.5 rounded-xl border transition-all relative flex flex-col justify-between gap-2.5 ${
                isFailing
                  ? 'border-red-500/70 bg-red-500/10 shadow-md ring-1 ring-red-500/40'
                  : isDegraded
                  ? 'border-amber-500/60 bg-amber-500/5 ring-1 ring-amber-500/30'
                  : 'autoos-surface hover:border-[var(--accent-primary)]/40'
              }`}
            >
              {/* Header inside card */}
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <div className={`p-1.5 rounded-lg shrink-0 ${
                    isFailing
                      ? 'bg-red-500/20 text-red-500'
                      : isDegraded
                      ? 'bg-amber-500/20 text-amber-500'
                      : 'autoos-card text-[var(--accent-primary)]'
                  }`}>
                    <IconComp className="w-4 h-4" />
                  </div>
                  <div>
                    <h5 className="text-xs font-bold text-[var(--text-primary)] leading-tight">
                      {dev.name}
                    </h5>
                    <span className="text-[9px] font-mono text-[var(--text-muted)] block">
                      {dev.code} • {dev.bus}
                    </span>
                  </div>
                </div>

                {/* Status Pill */}
                <span className={`text-[9px] font-mono px-2 py-0.5 rounded-full font-bold uppercase shrink-0 ${
                  isFailing
                    ? 'bg-red-600 text-white animate-pulse'
                    : isDegraded
                    ? 'bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-500/30'
                    : 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
                }`}>
                  {dev.status}
                </span>
              </div>

              {/* Health Bar */}
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px] font-mono">
                  <span className="text-[var(--text-muted)]">Salud Operativa:</span>
                  <span className={`font-bold ${
                    isFailing ? 'text-red-500' : isDegraded ? 'text-amber-500' : 'text-emerald-500'
                  }`}>
                    {dev.health}%
                  </span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      isFailing
                        ? 'bg-red-500'
                        : isDegraded
                        ? 'bg-amber-500'
                        : 'bg-emerald-500'
                    }`}
                    style={{ width: `${dev.health}%` }}
                  />
                </div>
              </div>

              {/* Active DTC info if failing */}
              {dev.activeDtc && (
                <div className="p-1.5 rounded-lg bg-red-500/15 border border-red-500/30 text-[10px] font-mono text-red-600 dark:text-red-400">
                  <span className="font-bold">DTC: {dev.activeDtc}</span>
                  {dev.failureMode && <div className="text-[9px] opacity-90 truncate">{dev.failureMode}</div>}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center justify-between gap-2 pt-1 border-t border-[var(--border-color)]">
                {isFailing || isDegraded ? (
                  <button
                    onClick={() => {
                      if (!canModify) {
                        onRoleRestricted('Calibrar / Restablecer Dispositivo de Hardware');
                        return;
                      }
                      onResetDevice(dev.code);
                    }}
                    className="w-full py-1 px-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-[10px] font-bold flex items-center justify-center gap-1 transition shadow-sm"
                  >
                    <Wrench className="w-3 h-3" />
                    <span>Calibrar / Restaurar</span>
                  </button>
                ) : (
                  <button
                    onClick={() => {
                      if (!canModify) {
                        onRoleRestricted('Inyectar Fallas en Sensores o Actuadores');
                        return;
                      }
                      onTriggerQuickFault(dev.code);
                    }}
                    className="w-full py-1 px-2 rounded-lg autoos-card hover:bg-red-500/15 hover:text-red-500 hover:border-red-500/30 text-[var(--text-muted)] font-mono text-[10px] font-semibold flex items-center justify-center gap-1 transition border border-[var(--border-color)]"
                  >
                    <Zap className="w-3 h-3" />
                    <span>Inyectar Falla de Prueba</span>
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
