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
  Sliders,
  Wrench,
  Sparkles,
  X,
} from 'lucide-react';
import { Process, UserRole, ProcessCategory, ProcessPriority } from '../types/scheduler';

interface CriticalProcessSimulatorProps {
  onInjectCriticalProcess: (
    proc: Omit<Process, 'waitingTime' | 'turnaroundTime'>,
    deviceCode?: string,
    dtc?: string,
    failureMode?: string
  ) => void;
  onResetDevice?: (deviceCode: string) => void;
  onResetAllScenarios?: () => void;
  currentTime: number;
  userRole: UserRole;
  onRoleRestricted: (action: string) => void;
  activeFaultDeviceCode?: string | null;
  initialDeviceCode?: string | null;
  onClose?: () => void;
}

export const AVAILABLE_DEVICES = [
  { code: 'DEV_GPS_01', name: 'Receptor GNSS / GPS Diferencial', defaultDtc: 'U0100-87', category: 'sensor' as const, color: '#06b6d4' },
  { code: 'DEV_CAM_FRONT', name: 'Cámara Estereoscópica ADAS Frontal', defaultDtc: 'B1203-54', category: 'sensor' as const, color: '#8b5cf6' },
  { code: 'DEV_LIDAR_01', name: 'Sensor LiDAR 360° Solid-State', defaultDtc: 'U0100-87', category: 'sensor' as const, color: '#06b6d4' },
  { code: 'DEV_RADAR_01', name: 'Radar Milimétrico 77GHz (ACC)', defaultDtc: 'B1000-01', category: 'sensor' as const, color: '#3b82f6' },
  { code: 'DEV_BATTERY_BMS', name: 'BMS Batería LiFePO4 Alta Tensión', defaultDtc: 'P0A7E-00', category: 'control' as const, color: '#f59e0b' },
  { code: 'DEV_ACT_BRAKE', name: 'Actuador Frenado By-Wire AEB', defaultDtc: 'B1000-01', category: 'seguridad' as const, color: '#dc2626' },
  { code: 'DEV_ACT_STEER', name: 'Actuador Dirección Eléctrica EPS', defaultDtc: 'C0040-04', category: 'control' as const, color: '#e11d48' },
  { code: 'DEV_COM_V2X', name: 'Módulo Telemetría 5G / V2X Cloud', defaultDtc: 'U0140-00', category: 'control' as const, color: '#3b82f6' },
  { code: 'DEV_GATEWAY_CAN', name: 'Gateway Bus CAN-FD Chasis', defaultDtc: 'U1101-08', category: 'seguridad' as const, color: '#ec4899' },
  { code: 'DEV_INFOTAINMENT', name: 'Pantalla Central Cockpit & Audio', defaultDtc: 'U0155-00', category: 'multimedia' as const, color: '#a855f7' },
  { code: 'DEV_HVAC_CLIMA', name: 'Climatización y Gestión Térmica', defaultDtc: 'B1081-00', category: 'confort' as const, color: '#10b981' },
];

export const FAILURE_TYPES = [
  'Falla Crítica Total / Desconexión de Bus',
  'Degradación de Rendimiento y Descalibración',
  'Sobrecalentamiento Térmico Extremo (>52°C)',
  'Ataque DoS / Inyección Anómala de Tramas',
  'Oclusión Óptica / Ceguera de Sensores',
  'Pérdida de Presión Hidráulica / Retardo Actuador',
  'Desfase de Ángulo y Sobrecorriente By-Wire',
  'Pérdida de Cobertura y Señal Satelital',
  'Personalizado',
];

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
    dispositivo: 'DEV_BATTERY_BMS',
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
    dispositivo: 'DEV_COM_V2X',
    dtc: 'U0140-00 (Desconexión de enlace telemático OTA)',
    burstTime: 3,
    category: 'control' as const,
    color: '#3b82f6',
    icon: WifiOff,
    desc: 'Pérdida de señal celular/satelital. Activa búfer NVRAM local determinístico para telemetría pendiente.',
    powerWatts: 25,
    memoryMb: 64,
  },
  {
    id: 'scen_aeb',
    name: 'Frenado Autónomo Emergencia (AEB)',
    dispositivo: 'DEV_ACT_BRAKE',
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
  onResetDevice,
  onResetAllScenarios,
  currentTime,
  userRole,
  onRoleRestricted,
  initialDeviceCode,
  onClose,
}) => {
  // Subtab navigation: 'CUSTOM' | 'PRESETS' | 'POWERTRAIN'
  const [viewSubtab, setViewSubtab] = useState<'CUSTOM' | 'PRESETS' | 'POWERTRAIN'>('CUSTOM');

  // Custom Failure Builder State
  const [targetDeviceCode, setTargetDeviceCode] = useState<string>(initialDeviceCode || 'DEV_GPS_01');
  const [selectedFailureType, setSelectedFailureType] = useState<string>(FAILURE_TYPES[0]);
  const [customFaultName, setCustomFaultName] = useState<string>('Falla Crítica de Navegación GNSS');
  const [customDtc, setCustomDtc] = useState<string>('U0100-87');
  const [severityLevel, setSeverityLevel] = useState<'ASIL-D' | 'ASIL-B' | 'CONFORT'>('ASIL-D');
  const [burstDuration, setBurstDuration] = useState<number>(4);
  const [cpuUsagePct, setCpuUsagePct] = useState<number>(45);
  const [powerWatts, setPowerWatts] = useState<number>(55);
  const [memoryMb, setMemoryMb] = useState<number>(140);
  const [customDescription, setCustomDescription] = useState<string>(
    'Pérdida súbita de señal diferencial RTK. Conmuta a estimación inercial por giróscopo IMU.'
  );

  // Preset scenarios state
  const [selectedPresetIdx, setSelectedPresetIdx] = useState(0);
  const [activePresetId, setActivePresetId] = useState<string | null>(null);
  const [lastInjectedPhase, setLastInjectedPhase] = useState<string | null>(null);

  const canInject = userRole === 'mecanico';

  // Handle device change in custom builder
  const handleDeviceChange = (devCode: string) => {
    setTargetDeviceCode(devCode);
    const dev = AVAILABLE_DEVICES.find((d) => d.code === devCode);
    if (dev) {
      setCustomDtc(dev.defaultDtc);
      setCustomFaultName(`Falla Crítica en ${dev.name.split('/')[0].trim()}`);
      if (dev.code === 'DEV_GPS_01') {
        setCustomDescription('Pérdida de señal satelital RTK. Conmutación a Dead Reckoning IMU.');
      } else if (dev.code === 'DEV_CAM_FRONT') {
        setCustomDescription('Oclusión óptica frontal y pérdida de reconocimiento de carril.');
      } else if (dev.code === 'DEV_BATTERY_BMS') {
        setCustomDescription('Sobrecalentamiento térmico en celdas de tracción (>48°C). Corte preventivo de potencia.');
      } else if (dev.code === 'DEV_ACT_BRAKE') {
        setCustomDescription('Pérdida de presión en booster hidráulico EBS. Activación de freno redundante.');
      } else {
        setCustomDescription(`Anomalía de comunicación y rendimiento degradado en ${dev.name}.`);
      }
    }
  };

  React.useEffect(() => {
    if (initialDeviceCode) {
      handleDeviceChange(initialDeviceCode);
    }
  }, [initialDeviceCode]);

  // Inject from Custom Builder
  const handleInjectCustomFault = () => {
    if (!canInject) {
      onRoleRestricted('Inyectar Fallas Críticas de Hardware ASIL-D (Requiere Rol Mecánico / Nivel 10)');
      return;
    }

    const dev = AVAILABLE_DEVICES.find((d) => d.code === targetDeviceCode) || AVAILABLE_DEVICES[0];
    const priority: ProcessPriority = severityLevel === 'ASIL-D' ? 1 : severityLevel === 'ASIL-B' ? 2 : 4;

    const procToInject: Omit<Process, 'waitingTime' | 'turnaroundTime'> = {
      pid: Math.floor(Math.random() * 800) + 200,
      name: customFaultName || `Falla en ${dev.name}`,
      category: dev.category,
      arrivalTime: currentTime,
      burstTime: burstDuration,
      remainingTime: burstDuration,
      priority,
      critical: severityLevel === 'ASIL-D',
      color: dev.color,
      state: 'LISTO',
      powerConsumptionWatts: powerWatts,
      cpuUsagePct,
      memoryMb,
    };

    setLastInjectedPhase(`[${dev.code}] ${customFaultName} disparada → Impacto en Hardware y CPU`);
    onInjectCriticalProcess(procToInject, dev.code, customDtc, selectedFailureType);
  };

  // Inject from Preset Scenarios
  const handleInjectPreset = () => {
    if (!canInject) {
      onRoleRestricted('Inyectar Fallas Críticas de Hardware ASIL-D (Requiere Rol Mecánico / Nivel 10)');
      return;
    }

    const sc = COCKPIT_INCIDENT_SCENARIOS[selectedPresetIdx];
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

    setActivePresetId(sc.id);
    setLastInjectedPhase(`${sc.name} detectada → Desalojando CPU con Prioridad 1`);
    onInjectCriticalProcess(procToInject, sc.dispositivo, sc.dtc.split(' ')[0], sc.name);
  };

  const handleResetAll = () => {
    setActivePresetId(null);
    setLastInjectedPhase('Todos los subsistemas restablecidos a Nominal ISO 26262 ASIL-D.');
    if (onResetAllScenarios) {
      onResetAllScenarios();
    }
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
              Simulador & Configurador Total de Fallas Vehiculares
            </h3>
            <p className="text-[11px] text-[var(--text-muted)]">
              Personalización total de modo de falla, dispositivo receptor, código DTC, severidad ASIL e impacto en CPU
            </p>
          </div>
        </div>

        {/* Subtabs */}
        <div className="flex items-center gap-1.5 autoos-surface p-1 rounded-xl text-xs font-mono">
          <button
            onClick={() => setViewSubtab('CUSTOM')}
            className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 ${
              viewSubtab === 'CUSTOM'
                ? 'bg-[var(--accent-primary)] text-white shadow-sm'
                : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>Configurador Personalizado</span>
          </button>
          <button
            onClick={() => setViewSubtab('PRESETS')}
            className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 ${
              viewSubtab === 'PRESETS'
                ? 'bg-[var(--accent-primary)] text-white shadow-sm'
                : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Escenarios Rápidos (7)</span>
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
            <span>Tren Motriz</span>
          </button>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className="px-3 py-1.5 rounded-xl bg-red-500/15 hover:bg-red-500/30 text-red-500 border border-red-500/30 font-mono text-xs font-bold transition flex items-center gap-1.5 shadow-sm"
          >
            <X className="w-4 h-4" />
            <span>Cerrar</span>
          </button>
        )}
      </div>

      {!canInject && (
        <div className="px-3 py-1.5 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-600 dark:text-amber-300 text-xs font-mono flex items-center gap-2">
          <ShieldX className="w-4 h-4 shrink-0" />
          <span>Acceso Restringido: Solo el Mecánico Certificado (Nivel 10) tiene privilegios para inyectar fallas ASIL-D.</span>
        </div>
      )}

      {/* VIEW 1: CUSTOM CONFIGURABLE BUILDER (USER EMPOWERMENT) */}
      {viewSubtab === 'CUSTOM' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            {/* Device Selection */}
            <div className="space-y-1.5">
              <label className="text-[11px] text-[var(--text-muted)] uppercase font-bold block">
                1. Dispositivo / Subsistema a Fallar:
              </label>
              <select
                value={targetDeviceCode}
                onChange={(e) => handleDeviceChange(e.target.value)}
                className="w-full autoos-surface border border-[var(--border-color)] text-[var(--text-primary)] p-2.5 rounded-xl font-bold text-xs focus:outline-none"
              >
                {AVAILABLE_DEVICES.map((d) => (
                  <option key={d.code} value={d.code} className="text-black dark:text-white dark:bg-[#180E24]">
                    {d.name} ({d.code})
                  </option>
                ))}
              </select>
            </div>

            {/* Failure Mode Selection */}
            <div className="space-y-1.5">
              <label className="text-[11px] text-[var(--text-muted)] uppercase font-bold block">
                2. Modo / Tipo de Falla:
              </label>
              <select
                value={selectedFailureType}
                onChange={(e) => setSelectedFailureType(e.target.value)}
                className="w-full autoos-surface border border-[var(--border-color)] text-[var(--text-primary)] p-2.5 rounded-xl font-bold text-xs focus:outline-none"
              >
                {FAILURE_TYPES.map((ft) => (
                  <option key={ft} value={ft} className="text-black dark:text-white dark:bg-[#180E24]">
                    {ft}
                  </option>
                ))}
              </select>
            </div>

            {/* Severity Level */}
            <div className="space-y-1.5">
              <label className="text-[11px] text-[var(--text-muted)] uppercase font-bold block">
                3. Nivel de Severidad ISO 26262:
              </label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => setSeverityLevel('ASIL-D')}
                  className={`py-2 px-2 rounded-xl font-bold transition text-center ${
                    severityLevel === 'ASIL-D'
                      ? 'bg-red-600 text-white shadow-sm ring-2 ring-red-500/40'
                      : 'autoos-surface text-[var(--text-muted)] hover:text-[var(--text-primary)] border border-[var(--border-color)]'
                  }`}
                >
                  🔴 ASIL-D (P1)
                </button>
                <button
                  type="button"
                  onClick={() => setSeverityLevel('ASIL-B')}
                  className={`py-2 px-2 rounded-xl font-bold transition text-center ${
                    severityLevel === 'ASIL-B'
                      ? 'bg-amber-600 text-white shadow-sm ring-2 ring-amber-500/40'
                      : 'autoos-surface text-[var(--text-muted)] hover:text-[var(--text-primary)] border border-[var(--border-color)]'
                  }`}
                >
                  🟡 ASIL-B (P2)
                </button>
                <button
                  type="button"
                  onClick={() => setSeverityLevel('CONFORT')}
                  className={`py-2 px-2 rounded-xl font-bold transition text-center ${
                    severityLevel === 'CONFORT'
                      ? 'bg-blue-600 text-white shadow-sm ring-2 ring-blue-500/40'
                      : 'autoos-surface text-[var(--text-muted)] hover:text-[var(--text-primary)] border border-[var(--border-color)]'
                  }`}
                >
                  🔵 Confort (P4)
                </button>
              </div>
            </div>

            {/* DTC Code input */}
            <div className="space-y-1.5">
              <label className="text-[11px] text-[var(--text-muted)] uppercase font-bold block">
                4. Código DTC OBD-II / UDS:
              </label>
              <input
                type="text"
                value={customDtc}
                onChange={(e) => setCustomDtc(e.target.value)}
                placeholder="Ej. U0100-87, P0A7E, B1203"
                className="w-full autoos-surface border border-[var(--border-color)] text-[var(--text-primary)] p-2.5 rounded-xl font-bold text-xs focus:outline-none"
              />
            </div>

            {/* Custom Name */}
            <div className="space-y-1.5">
              <label className="text-[11px] text-[var(--text-muted)] uppercase font-bold block">
                5. Nombre del Evento / Proceso de Contingencia:
              </label>
              <input
                type="text"
                value={customFaultName}
                onChange={(e) => setCustomFaultName(e.target.value)}
                placeholder="Nombre descriptivo"
                className="w-full autoos-surface border border-[var(--border-color)] text-[var(--text-primary)] p-2.5 rounded-xl font-bold text-xs focus:outline-none"
              />
            </div>

            {/* Duration and Resource Impact */}
            <div className="space-y-1.5">
              <label className="text-[11px] text-[var(--text-muted)] uppercase font-bold block flex justify-between">
                <span>6. Duración Ráfaga CPU:</span>
                <span className="text-[var(--accent-primary)]">{burstDuration}s ({cpuUsagePct}% CPU, {powerWatts}W)</span>
              </label>
              <div className="flex items-center gap-3 autoos-surface p-2.5 rounded-xl border border-[var(--border-color)]">
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={burstDuration}
                  onChange={(e) => setBurstDuration(Number(e.target.value))}
                  className="w-full accent-[var(--accent-primary)] cursor-pointer"
                />
                <span className="font-bold text-xs shrink-0 w-8 text-right">{burstDuration}s</span>
              </div>
            </div>
          </div>

          {/* Description */}
          <div className="space-y-1.5 text-xs font-mono">
            <label className="text-[11px] text-[var(--text-muted)] uppercase font-bold block">
              7. Descripción Técnica del Incidente:
            </label>
            <input
              type="text"
              value={customDescription}
              onChange={(e) => setCustomDescription(e.target.value)}
              placeholder="Detalles del comportamiento anómalo"
              className="w-full autoos-surface border border-[var(--border-color)] text-[var(--text-primary)] p-2.5 rounded-xl text-xs focus:outline-none"
            />
          </div>

          {/* Action Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-[var(--border-color)]">
            <button
              onClick={handleResetAll}
              className="px-3.5 py-2.5 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold flex items-center gap-1.5 transition font-mono"
            >
              <RotateCcw className="w-3.5 h-3.5 text-[var(--accent-primary)]" />
              <span>Restablecer Todo a Nominal</span>
            </button>

            <button
              onClick={handleInjectCustomFault}
              className={`px-5 py-2.5 rounded-xl font-bold text-xs uppercase tracking-wider flex items-center gap-2 shadow-md transition font-mono ${
                canInject
                  ? 'bg-red-600 hover:bg-red-500 text-white shadow-red-500/20 hover:scale-[1.02] active:scale-[0.98]'
                  : 'bg-[var(--bg-surface)] text-[var(--text-muted)] border border-[var(--border-color)] cursor-not-allowed opacity-60'
              }`}
            >
              <Play className="w-4 h-4 fill-current" />
              <span>⚡ Disparar Falla Personalizada al Sistema!</span>
            </button>
          </div>
        </div>
      )}

      {/* VIEW 2: 7 PRESET SCENARIOS */}
      {viewSubtab === 'PRESETS' && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 max-h-[290px] overflow-y-auto pr-1">
            {COCKPIT_INCIDENT_SCENARIOS.map((sc, idx) => {
              const isSelected = selectedPresetIdx === idx;
              const isActive = activePresetId === sc.id;
              const IconComp = sc.icon;

              return (
                <button
                  key={sc.id}
                  onClick={() => setSelectedPresetIdx(idx)}
                  className={`p-3.5 rounded-xl border text-left transition-all relative flex flex-col justify-between gap-2 cursor-pointer ${
                    isActive
                      ? 'border-red-500 ring-2 ring-red-500/30 bg-red-500/10'
                      : isSelected
                      ? 'autoos-card border-[var(--accent-primary)] ring-1 ring-[var(--accent-primary)]/40 shadow-sm'
                      : 'autoos-surface hover:border-[var(--accent-primary)]/40'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <div className={`p-1.5 rounded-lg shrink-0 ${
                        isActive
                          ? 'bg-red-500/20 text-red-500'
                          : isSelected
                          ? 'bg-[var(--accent-primary)]/15 text-[var(--accent-primary)]'
                          : 'autoos-card text-[var(--text-muted)]'
                      }`}>
                        <IconComp className="w-4 h-4" />
                      </div>
                      <h5 className="text-xs font-bold text-[var(--text-primary)] leading-tight">
                        {sc.name}
                      </h5>
                    </div>
                    <div className="flex items-center gap-1 shrink-0">
                      {isActive && (
                        <span className="text-[9px] font-mono px-1.5 py-0.5 rounded-full bg-red-600 text-white font-bold uppercase animate-pulse">
                          Activo
                        </span>
                      )}
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded autoos-surface text-[var(--text-muted)] border border-[var(--border-color)]">
                        {sc.burstTime}s
                      </span>
                    </div>
                  </div>
                  <p className="text-[11px] text-[var(--text-muted)] leading-relaxed">
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
              onClick={handleResetAll}
              className="px-3.5 py-2 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold flex items-center gap-1.5 transition font-mono"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Restablecer Sistema a Normal</span>
            </button>

            <button
              onClick={handleInjectPreset}
              className={`px-4 py-2.5 rounded-xl font-bold text-xs uppercase tracking-wider flex items-center gap-2 shadow-md transition font-mono ${
                canInject
                  ? 'bg-red-600 hover:bg-red-500 text-white shadow-red-500/20 hover:scale-[1.02] active:scale-[0.98]'
                  : 'bg-[var(--bg-surface)] text-[var(--text-muted)] border border-[var(--border-color)] cursor-not-allowed opacity-60'
              }`}
            >
              <Play className="w-4 h-4 fill-current" />
              <span>⚡ Disparar Escenario Seleccionado!</span>
            </button>
          </div>
        </>
      )}

      {/* VIEW 3: POWERTRAIN & THERMAL TELEMETRY */}
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
