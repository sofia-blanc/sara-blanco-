import React from 'react';
import { Battery, BatteryCharging, BatteryWarning, Zap, Power, Gauge, ShieldX } from 'lucide-react';
import { BatteryState, UserRole } from '../types/scheduler';

interface BatterySimulatorPanelProps {
  battery: BatteryState;
  onUpdateBatteryLevel: (level: number) => void;
  onTogglePowerSaving: () => void;
  wattsSaved: number;
  suspendedCount: number;
  userRole: UserRole;
  onRoleRestricted: (action: string) => void;
}

export const BatterySimulatorPanel: React.FC<BatterySimulatorPanelProps> = ({
  battery,
  onUpdateBatteryLevel,
  onTogglePowerSaving,
  wattsSaved,
  suspendedCount,
  userRole,
  onRoleRestricted,
}) => {
  const isCritical = battery.level <= 10;
  const isLow = battery.level <= 20 && !isCritical;
  const isPassenger = userRole === 'pasajero';

  const getBatteryColor = () => {
    if (isCritical) return 'text-red-500 border-red-500/50 bg-red-500/15';
    if (isLow) return 'text-amber-500 border-amber-500/50 bg-amber-500/15';
    return 'text-[var(--accent-primary)] border-[var(--accent-primary)]/40 bg-[var(--accent-primary)]/15';
  };

  const getProgressColor = () => {
    if (isCritical) return 'bg-red-500';
    if (isLow) return 'bg-amber-400';
    return 'bg-[var(--accent-primary)]';
  };

  const handleSliderChange = (newVal: number) => {
    if (isPassenger) {
      onRoleRestricted('Ajustar Parámetros de Batería de Tracción HV');
      return;
    }
    onUpdateBatteryLevel(newVal);
  };

  const handleToggleClick = () => {
    if (isPassenger) {
      onRoleRestricted('Activar/Desactivar Limp-Mode de Emergencia');
      return;
    }
    onTogglePowerSaving();
  };

  return (
    <div className={`rounded-2xl border p-5 shadow-xl transition-all duration-300 autoos-card ${
      isCritical
        ? 'border-red-500/80 ring-2 ring-red-500/20'
        : isLow
        ? 'border-amber-500/80 ring-1 ring-amber-500/20'
        : ''
    }`}>
      {/* Title */}
      <div className="flex flex-wrap items-center justify-between pb-3.5 border-b border-[var(--border-color)] mb-3.5 gap-2">
        <div className="flex items-center gap-2.5">
          <div className={`p-2 rounded-xl border ${getBatteryColor()}`}>
            {isCritical ? (
              <BatteryWarning className="w-4 h-4 animate-bounce text-red-500" />
            ) : isLow ? (
              <Battery className="w-4 h-4 text-amber-500" />
            ) : (
              <BatteryCharging className="w-4 h-4 text-[var(--accent-primary)]" />
            )}
          </div>
          <div>
            <h3 className="text-sm font-serif font-bold text-[var(--text-primary)] flex items-center gap-2">
              Simulador: Batería de Tracción HV (AutoOS BMS)
              {battery.isLowBatteryMode && (
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-600 dark:text-amber-300 border border-amber-500/40 font-mono font-bold">
                  LIMP-MODE
                </span>
              )}
            </h3>
            <p className="text-[11px] text-[var(--text-muted)]">
              Controlador Térmico BMS (DEV_BATTERY_BMS) y adaptación energética de CPU
            </p>
          </div>
        </div>

        <button
          onClick={handleToggleClick}
          className={`text-xs px-3 py-1.5 rounded-xl font-mono font-semibold transition-all flex items-center gap-1.5 shadow-sm ${
            battery.isLowBatteryMode
              ? 'bg-amber-500 text-white font-bold hover:bg-amber-400'
              : 'autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] border border-[var(--border-color)]'
          }`}
        >
          <Power className="w-3.5 h-3.5" />
          {battery.isLowBatteryMode ? 'Desactivar Limp-Mode' : 'Forzar Modo Ahorro'}
        </button>
      </div>

      {isPassenger && (
        <div className="mb-3 px-3 py-1.5 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-600 dark:text-amber-300 text-xs font-mono flex items-center gap-2">
          <ShieldX className="w-4 h-4 shrink-0" />
          <span>Modo Lectura (Rol Pasajero): Modificación de telemetría de tracción restringida.</span>
        </div>
      )}

      {/* Main Content */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
        {/* Left: Gauge & Slider */}
        <div className="md:col-span-2 space-y-3.5">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-[var(--text-muted)] flex items-center gap-1.5">
              <Gauge className="w-3.5 h-3.5 text-[var(--accent-primary)]" />
              Estado de Carga (SoC):
            </span>
            <span className={`text-base font-bold ${
              isCritical ? 'text-red-500 animate-pulse' : isLow ? 'text-amber-500' : 'text-[var(--text-primary)]'
            }`}>
              {battery.level}% ({battery.voltage}V | {battery.temperature}°C)
            </span>
          </div>

          {/* Progress bar */}
          <div className="w-full bg-[var(--bg-surface)] rounded-full h-3 overflow-hidden border border-[var(--border-color)] p-0.5">
            <div
              className={`h-full rounded-full transition-all duration-300 ${getProgressColor()}`}
              style={{ width: `${battery.level}%` }}
            />
          </div>

          {/* Range Slider */}
          <div className="space-y-1">
            <input
              type="range"
              min="2"
              max="100"
              disabled={isPassenger}
              value={battery.level}
              onChange={(e) => handleSliderChange(Number(e.target.value))}
              className="w-full accent-[var(--accent-primary)] h-1.5 bg-[var(--bg-surface)] rounded-lg cursor-pointer disabled:opacity-50"
            />
            <div className="flex justify-between text-[10px] text-[var(--text-muted)] font-mono">
              <span>0% Crítica (SoC ≤6.5%)</span>
              <span>20% Alerta Eco</span>
              <span>50% Media</span>
              <span>100% Carga Plena</span>
            </div>
          </div>

          {/* Quick preset buttons */}
          <div className="flex flex-wrap gap-2 pt-1">
            <button
              onClick={() => handleSliderChange(90)}
              className="text-[11px] font-mono px-2.5 py-1.5 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] transition"
            >
              ⚡ 90% Carga Plena
            </button>
            <button
              onClick={() => handleSliderChange(18)}
              className="text-[11px] font-mono px-2.5 py-1.5 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 text-amber-600 dark:text-amber-300 border border-amber-500/30 transition font-medium"
            >
              ⚠️ 18% Batería Baja (Eco)
            </button>
            <button
              onClick={() => handleSliderChange(6)}
              className="text-[11px] font-mono px-2.5 py-1.5 rounded-xl bg-red-500/15 hover:bg-red-500/25 text-red-600 dark:text-red-300 border border-red-500/30 transition font-bold"
            >
              🚨 6.5% Escenario: Batería Crítica & Térmico
            </button>
          </div>
        </div>

        {/* Right: Impact Box */}
        <div className="autoos-surface rounded-xl p-3.5 space-y-2 text-xs font-mono">
          <div className="text-[11px] font-bold text-[var(--text-primary)] border-b border-[var(--border-color)] pb-1.5 flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5 text-[var(--accent-primary)]" />
            Telemetría de Energía Ahorrada:
          </div>
          <div className="flex justify-between items-center text-[var(--text-muted)]">
            <span>Procesos Suspendidos:</span>
            <strong className={`text-sm ${suspendedCount > 0 ? 'text-amber-500' : 'text-[var(--text-primary)]'}`}>
              {suspendedCount}
            </strong>
          </div>
          <div className="flex justify-between items-center text-[var(--text-muted)]">
            <span>Potencia Protegida:</span>
            <strong className="text-emerald-500 font-bold">
              +{wattsSaved} W
            </strong>
          </div>
          <div className="flex justify-between items-center text-[var(--text-muted)]">
            <span>Autonomía Ganada:</span>
            <strong className="text-[var(--accent-primary)] font-bold">
              +{Math.round(wattsSaved * 0.28)} km est.
            </strong>
          </div>
          <div className="pt-2 border-t border-[var(--border-color)] text-[10px] leading-tight">
            {battery.isLowBatteryMode ? (
              <span className="text-amber-600 dark:text-amber-300 font-medium">
                ⚡ [Escenario Activo]: Paquete de 75 kWh con celdas degradadas. Se limita torque al 30% y se desactiva A/C y multimedia para garantizar dirección y frenado.
              </span>
            ) : (
              <span className="text-[var(--text-muted)]">
                ✓ Parámetros nominales: Despacho normal de tareas de confort y multimedia.
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
