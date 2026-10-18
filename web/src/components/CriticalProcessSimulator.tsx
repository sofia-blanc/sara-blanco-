import React, { useState } from 'react';
import {
  ShieldAlert,
  AlertTriangle,
  Play,
  RotateCcw,
  Flame,
  Car,
  Disc,
  Activity,
  ShieldX,
  Radio,
  Eye,
  WifiOff,
  Cpu,
  Gauge,
  Thermometer,
  Zap,
} from 'lucide-react';
import { Process, UserRole } from '../types/scheduler';

interface CriticalProcessSimulatorProps {
  onInjectCriticalProcess: (proc: Omit<Process, 'waitingTime' | 'turnaroundTime'>) => void;
  currentTime: number;
  userRole: UserRole;
  onRoleRestricted: (action: string) => void;
}

export const COCKPIT_INCIDENT_SCENARIOS = [
  {
    id: 'scen_lidar',
    name: 'Falla Sensor LiDAR 360°',
    dispositivo: 'DEV_LIDAR_01',
    dtc: 'U0100-87 (Pérdida de comunicación LiDAR)',
    burstTime: 4,
    category: 'sensor' as const,
    color: '#06b6d4',
    icon: Radio,
    desc: 'Oclusión óptica de lentes y pérdida del 80% de nube de puntos reflectiva. Conmuta a radar secundario.',
    powerWatts: 40,
    memoryMb: 180,
  },
  {
    id: 'scen_bms_thermal',
    name: 'Sobrecalentamiento BMS (48°C)',
    dispositivo: 'DEV_BMS_01',
    dtc: 'P0A7E-00 (Sobretemperatura módulo celdas tracción)',
    burstTime: 5,
    category: 'control' as const,
    color: '#f59e0b',
    icon: Flame,
    desc: 'Celdas HV en límite térmico. Corte automático de potencia al motor e inyección de refrigeración forzada.',
    powerWatts: 70,
    memoryMb: 110,
  },
  {
    id: 'scen_can_attack',
    name: 'Inyección Anómala Bus CAN-FD',
    dispositivo: 'DEV_GATEWAY_CAN',
    dtc: 'U1101-08 (Tráfico malicioso DoS en bus de chasis)',
    burstTime: 3,
    category: 'seguridad' as const,
    color: '#ec4899',
    icon: ShieldAlert,
    desc: 'Saturación por DoS con tramas no autorizadas. Aislamiento de nodos y conmutación a bus redundante.',
    powerWatts: 45,
    memoryMb: 85,
  },
  {
    id: 'scen_camera_occlusion',
    name: 'Descalibración Cámara ADAS',
    dispositivo: 'DEV_CAM_FRONT',
    dtc: 'B1203-54 (Ceguera óptica frontal niebla/suciedad)',
    burstTime: 4,
    category: 'sensor' as const,
    color: '#8b5cf6',
    icon: Eye,
    desc: 'Pérdida de reconocimiento de carril 4K. Despliega advertencia en HUD y eleva distancia de seguridad.',
    powerWatts: 35,
    memoryMb: 240,
  },
  {
    id: 'scen_telemetry_drop',
    name: 'Corte de Cobertura 5G Nube',
    dispositivo: 'DEV_MODEM_5G',
    dtc: 'U0140-00 (Desconexión de enlace telemático OTA)',
    burstTime: 3,
    category: 'control' as const,
    color: '#3b82f6',
    icon: WifiOff,
    desc: 'Pérdida de señal satelital/celular. Activa búfer NVRAM local determinístico para telemetría pendiente.',
    powerWatts: 25,
    memoryMb: 64,
  },
  {
    id: 'scen_aeb',
    name: 'Frenado Autónomo Emergencia (AEB)',
    dispositivo: 'DEV_BRAKE_BOOSTER',
    dtc: 'B1000-01 (Desaceleración inminente radar/cámara)',
    burstTime: 3,
    category: 'seguridad' as const,
    color: '#dc2626',
    icon: Disc,
    desc: 'Obstáculo inminente a 15m. Requiere desalojo inmediato de CPU para actuación de booster hidráulico.',
    powerWatts: 65,
    memoryMb: 64,
  },
  {
    id: 'scen_steer',
    name: 'Fallo Crítico Dirección By-Wire',
    dispositivo: 'DEV_ACT_STEER',
    dtc: 'C0040-04 (Desfase de ángulo y sobrecorriente EPS)',
    burstTime: 4,
    category: 'control' as const,
    color: '#e11d48',
    icon: Car,
    desc: 'Desfase anómalo en servomotores EPS. Requiere conmutación forzosa a canal redundante.',
    powerWatts: 55,
    memoryMb: 96,
  },
];

export const CriticalProcessSimulator: React.FC<CriticalProcessSimulatorProps> = ({
  onInjectCriticalProcess,
  currentTime,
  userRole,
  onRoleRestricted,
}) => {
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [activeScenarioId, setActiveScenarioId] = useState<string | null>(null);
  const [lastInjectedPhase, setLastInjectedPhase] = useState<string | null>(null);
  const [viewSubtab, setViewSubtab] = useState<'INCIDENTS' | 'POWERTRAIN'>('INCIDENTS');

  const canInject = userRole === 'mecanico';

  const handleInject = () => {
    if (!canInject) {
      onRoleRestricted('Inyectar Fallas Críticas de Hardware ASIL-D (Requiere Rol Mecánico / Nivel 10)');
      return;
    }

    const sc = COCKPIT_INCIDENT_SCENARIOS[selectedIdx];
    const procToInject: Omit<Process, 'waitingTime' | 'turnaroundTime'> = {
      pid: Math.floor(Math.random() * 800) + 200,
      name: sc.name,
      category: sc.category,
      arrivalTime: currentTime,
      burstTime: sc.burstTime,
      remainingTime: sc.burstTime,
      priority: 1, // Highest priority ASIL-D
      critical: true,
      color: sc.color,
      state: 'LISTO',
      powerConsumptionWatts: sc.powerWatts,
      cpuUsagePct: 35,
      memoryMb: sc.memoryMb,
    };

    setActiveScenarioId(sc.id);
    setLastInjectedPhase(`DTC ${sc.dtc} detectado en ${sc.dispositivo} → Desalojando CPU con Prioridad 1`);
    onInjectCriticalProcess(procToInject);
  };

  const handleResetScenarios = () => {
    setActiveScenarioId(null);
    setLastInjectedPhase('Todos los escenarios restablecidos. Parámetros nominales ISO 26262 ASIL-D.');
  };

  return (
    <div className="autoos-card rounded-2xl p-5 shadow-xl space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3.5 border-b border-[var(--border-color)]">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-red-500/15 text-red-500 border border-red-500/30 animate-pulse">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-serif font-bold text-[var(--text-primary)] flex items-center gap-2">
              Simulador de Fallas e Inyección de Incidentes (Cockpit AutoOS)
            </h3>
            <p className="text-[11px] text-[var(--text-muted)]">
              Verificación de resiliencia del kernel RTOS, inyección ASIL-D y telemetría térmica
            </p>
          </div>
        </div>

        {/* Subtabs to switch between Incident Injection and Powertrain Telemetry */}
        <div className="flex items-center gap-1.5 autoos-surface p-1 rounded-xl text-xs font-mono">
          <button
            onClick={() => setViewSubtab('INCIDENTS')}
            className={`px-3 py-1.5 rounded-lg font-bold transition ${
              viewSubtab === 'INCIDENTS'
                ? 'bg-[var(--accent-primary)] text-white shadow-sm'
                : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
            }`}
          >
            Escenarios de Falla (7)
          </button>
          <button
            onClick={() => setViewSubtab('POWERTRAIN')}
            className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 ${
              viewSubtab === 'POWERTRAIN'
                ? 'bg-[var(--accent-primary)] text-white shadow-sm'
                : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
            }`}
          >
            <Gauge className="w-3.5 h-3.5" />
            <span>Tren Motriz Térmico</span>
          </button>
        </div>
      </div>

      {!canInject && (
        <div className="px-3 py-1.5 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-600 dark:text-amber-300 text-xs font-mono flex items-center gap-2">
          <ShieldX className="w-4 h-4 shrink-0" />
          <span>Acceso Restringido: Solo el Mecánico Certificado (Nivel 10) tiene privilegios para disparar incidentes ASIL-D.</span>
        </div>
      )}

      {/* VIEW 1: 7 INCIDENT SCENARIOS */}
      {viewSubtab === 'INCIDENTS' && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 max-h-[290px] overflow-y-auto pr-1">
            {COCKPIT_INCIDENT_SCENARIOS.map((sc, idx) => {
              const isSelected = selectedIdx === idx;
              const isActive = activeScenarioId === sc.id;
              const IconComp = sc.icon;

              return (
                <button
                  key={sc.id}
                  onClick={() => setSelectedIdx(idx)}
                  className={`p-3 rounded-xl border text-left transition-all relative flex flex-col justify-between ${
                    isActive
                      ? 'border-red-500 ring-2 ring-red-500/30 bg-red-500/10'
                      : isSelected
                      ? 'autoos-card border-[var(--accent-primary)] ring-1 ring-[var(--accent-primary)]/40 shadow-sm'
                      : 'autoos-surface hover:border-[var(--accent-primary)]/40'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold flex items-center gap-1.5 text-red-500">
                      <IconComp className="w-3.5 h-3.5" />
                      <span className="font-mono">{sc.dispositivo}</span>
                    </span>
                    <div className="flex items-center gap-1">
                      {isActive && (
                        <span className="text-[9px] font-mono px-1.5 py-0.2 rounded-full bg-red-600 text-white font-bold uppercase animate-pulse">
                          Activo
                        </span>
                      )}
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded autoos-surface text-[var(--text-muted)]">
                        {sc.burstTime}s
                      </span>
                    </div>
                  </div>
                  <h5 className="text-[11px] font-semibold text-[var(--text-primary)] line-clamp-1 mb-1">
                    {sc.name}
                  </h5>
                  <p className="text-[10px] text-[var(--text-muted)] line-clamp-2 leading-tight">
                    {sc.desc}
                  </p>
                </button>
              );
            })}
          </div>

          {/* OS Mitigation Phases Preview */}
          <div className="p-3 autoos-surface rounded-xl flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono text-[var(--text-muted)]">
            <div className="flex items-center gap-2">
              <Activity className="w-3.5 h-3.5 text-[var(--accent-primary)]" />
              <span>Mitigación RTOS: </span>
              <span className="text-[var(--text-primary)] font-semibold">1. Detectar DTC</span>
              <span>→</span>
              <span className="text-amber-500 font-semibold">2. Preempt CPU</span>
              <span>→</span>
              <span className="text-emerald-500 font-semibold">3. Fail-Safe Nominal</span>
            </div>
            {lastInjectedPhase && (
              <span className="text-red-500 font-bold animate-pulse text-[10px]">
                ⚡ {lastInjectedPhase}
              </span>
            )}
          </div>

          {/* Action Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-[var(--border-color)]">
            <button
              onClick={handleResetScenarios}
              className="px-3.5 py-2 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold flex items-center gap-1.5 transition"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Restablecer Sistema a Normal</span>
            </button>

            <button
              onClick={handleInject}
              className={`px-4 py-2.5 rounded-xl font-bold text-xs uppercase tracking-wider flex items-center gap-2 shadow-md transition ${
                canInject
                  ? 'bg-red-600 hover:bg-red-500 text-white shadow-red-500/20 hover:scale-[1.02] active:scale-[0.98]'
                  : 'bg-[var(--bg-surface)] text-[var(--text-muted)] border border-[var(--border-color)] cursor-not-allowed opacity-60'
              }`}
            >
              <Play className="w-4 h-4 fill-current" />
              <span>⚡ Disparar Incidente en CPU!</span>
            </button>
          </div>
        </>
      )}

      {/* VIEW 2: POWERTRAIN & INVERTER THERMAL TELEMETRY (FROM COCKPIT PROCESS MANAGER) */}
      {viewSubtab === 'POWERTRAIN' && (
        <div className="space-y-3 font-mono">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
              <span className="text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1">
                <Thermometer className="w-3 h-3 text-amber-500" /> Motor Delantero
              </span>
              <strong className="text-lg text-[var(--text-primary)] font-bold">58.4 °C</strong>
              <span className="text-[10px] text-emerald-500 block">Nominal (&lt; 85°C)</span>
            </div>
            <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
              <span className="text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1">
                <Thermometer className="w-3 h-3 text-amber-500" /> Motor Trasero
              </span>
              <strong className="text-lg text-[var(--text-primary)] font-bold">62.1 °C</strong>
              <span className="text-[10px] text-emerald-500 block">Nominal (&lt; 85°C)</span>
            </div>
            <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
              <span className="text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1">
                <Zap className="w-3 h-3 text-[var(--accent-primary)]" /> Inversor IGBT
              </span>
              <strong className="text-lg text-[var(--accent-primary)] font-bold">49.2 °C</strong>
              <span className="text-[10px] text-emerald-500 block">PWM 16 kHz</span>
            </div>
            <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
              <span className="text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1">
                <Gauge className="w-3 h-3 text-emerald-500" /> Caudal Refrig.
              </span>
              <strong className="text-lg text-emerald-600 dark:text-emerald-400 font-bold">14.2 L/min</strong>
              <span className="text-[10px] text-[var(--text-muted)] block">Bomba Lin Bus</span>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3 text-xs">
            <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
              <span className="text-[10px] text-[var(--text-muted)] uppercase block">RPM Motor</span>
              <strong className="text-base text-[var(--text-primary)]">4,850 RPM</strong>
            </div>
            <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
              <span className="text-[10px] text-[var(--text-muted)] uppercase block">Torque Inmediato</span>
              <strong className="text-base text-[var(--text-primary)]">285 Nm</strong>
            </div>
            <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
              <span className="text-[10px] text-[var(--text-muted)] uppercase block">Potencia Neta</span>
              <strong className="text-base text-[var(--text-primary)]">142.8 kW</strong>
            </div>
          </div>

          <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-xs flex items-center justify-between">
            <span className="flex items-center gap-2 font-bold">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              Watchdog RTOS ASIL-D Nominal
            </span>
            <span>Aislamiento de Memoria MPU Activo</span>
          </div>
        </div>
      )}
    </div>
  );
};
