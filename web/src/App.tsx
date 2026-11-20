import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import {
  AlgorithmType,
  BatteryState,
  Process,
  ProcessState,
  UserRole,
  VehicleDevice,
} from './types/scheduler';
import { INITIAL_VEHICLE_PROCESSES } from './utils/presets';
import {
  createInitialSimulationState,
  stepSimulationTick,
  calculateMetrics,
  SimulationState,
} from './utils/schedulerEngine';
import { GanttChart } from './components/GanttChart';
import { CPUCoreCard } from './components/CPUCoreCard';
import { QueueVisualizer } from './components/QueueVisualizer';
import { ProcessTable } from './components/ProcessTable';
import { BatterySimulatorPanel } from './components/BatterySimulatorPanel';
import { CriticalProcessSimulator } from './components/CriticalProcessSimulator';
import { SimulationCenter } from './components/SimulationCenter';
import { OSResourceMonitor } from './components/OSResourceMonitor';
import { PythonKernelPanel } from './components/PythonKernelPanel';
import { useBlackboxCloudSync } from './cloud/blackboxSync'; // AUTOOS_V14_BLACKBOX_CLOUD
import { getPythonKernelStatus, onPythonKernelStatus, sendKernelSyncRequest, type PythonKernelStatus } from './kernelBridge';
import { buildOSResourceSnapshot, batteryAfterEnergyTick, estimatePowerW, toResourceSample, advanceOperatingSystemTick, type OSResourceSample } from './simulation/resources';
import { CinematicMenu } from './components/CinematicMenu';
import { AutoOSModulesV11 } from './components/AutoOSModulesV11';
import { advanceMission, createMission, startMission, type MissionState, type MissionEvent, type RouteId } from './simulation/navigation';
import { ModuleScene } from './components/ModuleScene';
import { ModuleOrientationV3 } from './components/ModuleOrientationV3';
import { CockpitExplorerV4 } from './components/CockpitExplorerV4';
import type { CockpitFeatureId } from './components/CockpitExplorerV4';
import { CockpitOverviewV5, CockpitSecurityV5 } from './components/CockpitWorkspaceV5';
import { CockpitToolSceneV6 } from './components/CockpitToolSceneV6'; // AUTOOS_EXPERIENCE_V6
import type { AutoOSModule } from './components/CinematicMenu';
import { initialScenarioState, applyScenarioAction, makeBattery, markFault, insertWorkload, applyWeather, simEvent, recoverFault } from './simulation/engine';
import { scenarioById, type ScenarioId, type SimulationAction, type Weather } from './simulation/scenarios';

import { HardwareStatusGrid } from './components/HardwareStatusGrid';
import { AlgorithmComparisonModal } from './components/AlgorithmComparisonModal';
import { NewProcessModal } from './components/NewProcessModal';
import { EventsLog } from './components/EventsLog';
import { isSupabaseConfigured } from './supabaseClient';
import {
  Play,
  Pause,
  SkipForward,
  RotateCcw,
  PlusCircle,
  BarChart3,
  Car,
  Cpu,
  BatteryCharging,
  Activity,
  Sun,
  Moon,
  Shield,
  ShieldAlert,
  X,
  CheckCircle,
  AlertTriangle,
  Zap,
  Navigation,
  FlaskConical,
  Menu,
} from 'lucide-react';

const INITIAL_VEHICLE_DEVICES: VehicleDevice[] = [
  {
    id: 'dev_01',
    code: 'DEV_GPS_01',
    name: 'Receptor GNSS / GPS Diferencial',
    subsystem: 'Navegación',
    status: 'operativo',
    health: 98,
    criticalLevel: 'esencial',
    bus: 'CAN-Bus Principal',
    activeDtc: null,
    failureMode: null,
  },
  {
    id: 'dev_02',
    code: 'DEV_CAM_FRONT',
    name: 'Cámara Estereoscópica ADAS Frontal',
    subsystem: 'Visión',
    status: 'operativo',
    health: 95,
    criticalLevel: 'critico',
    bus: 'Automotive Ethernet',
    activeDtc: null,
    failureMode: null,
  },
  {
    id: 'dev_03',
    code: 'DEV_LIDAR_01',
    name: 'Sensor LiDAR 360° Solid-State',
    subsystem: 'Sensores',
    status: 'operativo',
    health: 99,
    criticalLevel: 'critico',
    bus: 'Automotive Ethernet',
    activeDtc: null,
    failureMode: null,
  },
  {
    id: 'dev_04',
    code: 'DEV_RADAR_01',
    name: 'Radar Milimétrico 77GHz (ACC)',
    subsystem: 'Sensores',
    status: 'operativo',
    health: 94,
    criticalLevel: 'critico',
    bus: 'CAN-Bus ADAS',
    activeDtc: null,
    failureMode: null,
  },
  {
    id: 'dev_05',
    code: 'DEV_BATTERY_BMS',
    name: 'BMS Batería LiFePO4 Alta Tensión',
    subsystem: 'Batería',
    status: 'operativo',
    health: 92,
    criticalLevel: 'critico',
    bus: 'CAN-Bus Principal',
    activeDtc: null,
    failureMode: null,
  },
  {
    id: 'dev_06',
    code: 'DEV_ACT_BRAKE',
    name: 'Actuador Frenado By-Wire AEB',
    subsystem: 'Seguridad Dinámica',
    status: 'operativo',
    health: 100,
    criticalLevel: 'critico',
    bus: 'CAN-Bus ADAS',
    activeDtc: null,
    failureMode: null,
  },
  {
    id: 'dev_07',
    code: 'DEV_ACT_STEER',
    name: 'Actuador Dirección Eléctrica EPS',
    subsystem: 'Seguridad Dinámica',
    status: 'operativo',
    health: 97,
    criticalLevel: 'critico',
    bus: 'CAN-Bus ADAS',
    activeDtc: null,
    failureMode: null,
  },
  {
    id: 'dev_08',
    code: 'DEV_COM_V2X',
    name: 'Módulo Telemetría 5G / V2X Cloud',
    subsystem: 'Comunicación',
    status: 'operativo',
    health: 91,
    criticalLevel: 'esencial',
    bus: 'Automotive Ethernet',
    activeDtc: null,
    failureMode: null,
  },
  {
    id: 'dev_09',
    code: 'DEV_GATEWAY_CAN',
    name: 'Gateway Bus CAN-FD Chasis',
    subsystem: 'Chasis',
    status: 'operativo',
    health: 98,
    criticalLevel: 'critico',
    bus: 'CAN-Bus Principal',
    activeDtc: null,
    failureMode: null,
  },
  {
    id: 'dev_10',
    code: 'DEV_INFOTAINMENT',
    name: 'Pantalla Central Cockpit & Audio',
    subsystem: 'Multimedia',
    status: 'operativo',
    health: 96,
    criticalLevel: 'confort',
    bus: 'LIN-Bus Confort',
    activeDtc: null,
    failureMode: null,
  },
  {
    id: 'dev_11',
    code: 'DEV_HVAC_CLIMA',
    name: 'Climatización y Gestión Térmica',
    subsystem: 'Confort',
    status: 'operativo',
    health: 89,
    criticalLevel: 'confort',
    bus: 'LIN-Bus Confort',
    activeDtc: null,
    failureMode: null,
  },
];

export default function App() {
  // Navigation tabs
  const [activeTab, setActiveTab] = useState<AutoOSModule>('HOME');
  // AUTOOS_CINEMATIC_V1: menú de bienvenida; los estados de simulación se conservan.
  const [showCinematicMenu, setShowCinematicMenu] = useState(true);
  // AUTOOS_EXPERIENCE_V4: entrada a Conducción por explorador, no por una
  // grilla de diagnóstico. Solo controla PRESENTACIÓN; no estados del vehículo.
  const [cockpitWorkspace, setCockpitWorkspace] = useState(false);
  const [cockpitFeature, setCockpitFeature] = useState<CockpitFeatureId>('overview');
  const [cockpitHeight, setCockpitHeight] = useState(1200);
  // AUTOOS_EXPERIENCE_V3: un único estado para los efectos del menú y el audio
  // del cockpit. Se guarda localmente y se comunica al iframe independiente.
  const [audioMuted, setAudioMuted] = useState(() => localStorage.getItem('autoos_audio_muted') === '1');
  useEffect(() => {
    localStorage.setItem('autoos_audio_muted', audioMuted ? '1' : '0');
    iframeRef.current?.contentWindow?.postMessage({ type: 'AUTOOS_SET_AUDIO_MUTED', muted: audioMuted }, '*');
  }, [audioMuted]);

  // Navigation tabs: only 2 tabs as requested
  // Wrap the whole UI with SimulationProvider (added later)


  // Universal Theme state: 'dark' (Purple Night) | 'light' (Soft Dove)
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    const saved = localStorage.getItem('autoos_theme');
    return saved === 'light' ? 'light' : 'dark';
  });

  // User Role & RBAC State: 'mecanico' | 'conductor' | 'pasajero'
  const [userRole, setUserRole] = useState<UserRole>('mecanico');
  const [rbacAlertMessage, setRbacAlertMessage] = useState<string | null>(null);

  // Hardware Devices State for Real-Time Reflection
  const [devices, setDevices] = useState<VehicleDevice[]>(INITIAL_VEHICLE_DEVICES);

  // Inlined or fetched cockpit HTML for seamless rendering in both Vite dev server and Streamlit iframe
  const [cockpitHtml, setCockpitHtml] = useState<string | null>(() => {
    if (typeof window !== 'undefined' && (window as unknown as { __AUTOOS_COCKPIT_HTML__?: string }).__AUTOOS_COCKPIT_HTML__) {
      return (window as unknown as { __AUTOOS_COCKPIT_HTML__?: string }).__AUTOOS_COCKPIT_HTML__!;
    }
    return null;
  });

  useEffect(() => {
    if (!cockpitHtml) {
      fetch('/autoos_interactive.html')
        .then((res) => (res.ok ? res.text() : ''))
        .then((html) => {
          if (html) setCockpitHtml(html);
        })
        .catch(() => {});
    }
  }, [cockpitHtml]);

  const iframeRef = useRef<HTMLIFrameElement>(null);

  // AUTOOS_V6_NAV_SYNC: cambiar de herramienta no desmonta el Cockpit.
  // El puente V4 pulsa los botones reales del iframe tras cada selección.
  useEffect(() => {
    if (!cockpitWorkspace || cockpitFeature === 'overview' || cockpitFeature === 'security') return;
    const feature = cockpitFeature === 'overview-original' ? 'overview' :
      cockpitFeature === 'security-original' ? 'security' : cockpitFeature;
    const request = () => iframeRef.current?.contentWindow?.postMessage(
      { type: 'AUTOOS_V4_OPEN_FEATURE', feature }, '*');
    const first = window.setTimeout(request, 130);
    const second = window.setTimeout(request, 420);
    return () => { window.clearTimeout(first); window.clearTimeout(second); };
  }, [cockpitWorkspace, cockpitFeature]);

  const syncIframeState = useCallback(() => {
    const iframe = iframeRef.current;
    if (typeof window !== 'undefined') {
      (window as unknown as { __AUTOOS_CURRENT_ROLE__?: string }).__AUTOOS_CURRENT_ROLE__ = userRole;
      (window as unknown as { __AUTOOS_CURRENT_THEME__?: string }).__AUTOOS_CURRENT_THEME__ = theme;
    }
    if (!iframe) return;
    try {
      if (iframe.contentDocument && iframe.contentDocument.documentElement) {
        if (theme === 'dark') {
          iframe.contentDocument.documentElement.classList.add('dark');
        } else {
          iframe.contentDocument.documentElement.classList.remove('dark');
        }
      }
    } catch (_) {}
    try {
      iframe.contentWindow?.postMessage({ type: 'AUTOOS_SET_THEME', theme }, '*');
      iframe.contentWindow?.postMessage({ type: 'AUTOOS_SET_ROLE', role: userRole }, '*');
      iframe.contentWindow?.postMessage({ type: 'AUTOOS_SET_AUDIO_MUTED', muted: audioMuted }, '*');
      const win = iframe.contentWindow as unknown as {
        __AUTOOS_SET_THEME__?: (t: string) => void;
        __AUTOOS_SET_ROLE__?: (r: string) => void;
      };
      if (typeof win?.__AUTOOS_SET_THEME__ === 'function') {
        win.__AUTOOS_SET_THEME__(theme);
      }
      if (typeof win?.__AUTOOS_SET_ROLE__ === 'function') {
        win.__AUTOOS_SET_ROLE__(userRole);
      }
    } catch (_) {}
  }, [theme, userRole, audioMuted]);

  // Apply theme class to document
  useEffect(() => {
    localStorage.setItem('autoos_theme', theme);
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    syncIframeState();
  }, [theme, syncIframeState]);

  useEffect(() => {
    syncIframeState();
    const t1 = setTimeout(syncIframeState, 60);
    const t2 = setTimeout(syncIframeState, 200);
    const t3 = setTimeout(syncIframeState, 500);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [userRole, activeTab, theme, syncIframeState]);

  // V11: conductor y pasajero pueden navegar por GPS, Inicio y Caja Negra.
  // Únicamente se abandona el planificador si deja de estar autorizado.
  useEffect(() => {
    if (userRole !== 'mecanico' && activeTab === 'SCHEDULER') {
      setActiveTab('HOME');
    }
  }, [userRole, activeTab]);

  // Bidirectional listener from Cockpit iframe
  useEffect(() => {
    const handleIframeMessage = (e: MessageEvent) => {
      if (!e.data) return;
      // Altura del cockpit independiente. Validamos origen y límites antes de
      // aplicarla, para evitar scroll doble y valores arbitrarios.
      if (e.data.type === 'AUTOOS_V4_COCKPIT_HEIGHT' && e.source === iframeRef.current?.contentWindow) {
        const next = Number(e.data.height);
        if (Number.isFinite(next) && next >= 480 && next <= 15000) setCockpitHeight(Math.ceil(next));
      }
      if (e.data.type === 'AUTOOS_THEME_CHANGED') {
        const next = e.data.theme === 'dark' ? 'dark' : 'light';
        setTheme(next);
      }
      if (e.data.type === 'AUTOOS_ROLE_CHANGED') {
        if (['mecanico', 'conductor', 'pasajero'].includes(e.data.role)) {
          setUserRole(e.data.role as UserRole);
        }
      }
      if (e.data.type === 'AUTOOS_NAVIGATE_TAB') {
        if (e.data.tab === 'SCHEDULER') {
          setActiveTab('SCHEDULER');
        }
      }
      if (e.data.type === 'AUTOOS_REQUEST_SYNC') {
        syncIframeState();
      }
    };
    window.addEventListener('message', handleIframeMessage);
    return () => window.removeEventListener('message', handleIframeMessage);
  }, [syncIframeState]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  // RBAC rejection trigger
  const handleRoleRestricted = (action: string) => {
    const roleName = userRole === 'pasajero' ? 'Pasajero' : userRole === 'conductor' ? 'Conductor' : 'Mecánico';
    setRbacAlertMessage(
      `⛔ Acceso Denegado por Política RBAC! El rol actual [${roleName}] no posee privilegios de seguridad para: ${action}. Cambia de rol en la barra superior para continuar.`
    );
  };

  // Scheduler parameters
  const [algorithm, setAlgorithm] = useState<AlgorithmType>('RR');
  const [quantum, setQuantum] = useState<number>(2);
  const [speedMs] = useState<number>(800);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);

  // Modals
  const [isCompareModalOpen, setIsCompareModalOpen] = useState(false);
  const [isNewProcessModalOpen, setIsNewProcessModalOpen] = useState(false);

  // Master processes template
  const [baseProcesses, setBaseProcesses] = useState<Process[]>(() =>
    INITIAL_VEHICLE_PROCESSES.map((p) => ({
      ...p,
      waitingTime: 0,
      turnaroundTime: 0,
    }))
  );

  // Battery Simulator State
  const [battery, setBattery] = useState<BatteryState>({
    level: 85,
    voltage: 392,
    temperature: 28,
    isLowBatteryMode: false,
    isCriticalBatteryMode: false,
    autoThrottlingEnabled: true,
    powerSavingWattsSaved: 0,
  });

  // Simulation execution state
  const [simCloudRun, setSimCloudRun] = useState(0);
  const [simState, setSimState] = useState<SimulationState>(() =>
    createInitialSimulationState(baseProcesses, 'RR', 2)
  );

  // AUTOOS V9: un solo modelo de recursos para Simulación, CPU y Conducción.
  // Separamos estado del escenario (velocidad/clima) del scheduler: ambos
  // se combinan en una instantánea derivada, nunca en porcentajes inventados.
  const [driveSpeedKmh, setDriveSpeedKmh] = useState(0);
  const [driveWeather, setDriveWeather] = useState<Weather>('soleado');
  const [tripEnergyWh, setTripEnergyWh] = useState(0);
  const [resourceHistory, setResourceHistory] = useState<OSResourceSample[]>([]);
  // AUTOOS V11: GPS y Caja Negra viven en el mismo propietario de estados.
  // Cada avance usa handleSimulatorDriveTick, que comparte CPU/RAM/batería.
  const [mission, setMission] = useState<MissionState>(() => createMission());
  const [missionEvents, setMissionEvents] = useState<MissionEvent[]>(() => {
    try {return JSON.parse(localStorage.getItem('autoos_v11_blackbox') || '[]').slice(0,150);}
    catch {return [];}
  });
  useEffect(() => {
    try {localStorage.setItem('autoos_v11_blackbox', JSON.stringify(missionEvents.slice(0,150)));}
    catch { /* storage bloqueado: la sesión continúa en memoria */ }
  }, [missionEvents]);
  const simRef = useRef(simState);
  const deviceRef = useRef(devices);
  const batteryRef = useRef(battery);
  useEffect(() => { simRef.current = simState; deviceRef.current = devices; batteryRef.current = battery; }, [simState, devices, battery]);

  const osResources = useMemo(() => buildOSResourceSnapshot(
    simState, battery, devices, driveSpeedKmh, driveWeather, tripEnergyWh,
  ), [simState, battery, devices, driveSpeedKmh, driveWeather, tripEnergyWh]);
  // AUTOOS_V14_BLACKBOX_CLOUD: mismos eventos que la Caja Negra, sin otro motor.
  const eventsForCloud = useMemo(() => [
    ...simState.events.map(e => ({id: `sim${simCloudRun}_${e.id}`, kind: e.type, severity: e.severity,
      message: e.message, tick: e.time})),
    ...missionEvents.map(e => ({id: `gps_${e.id}`, kind: e.kind, severity: e.severity,
      message: e.message, tick: e.tick})),
  ], [simState.events, missionEvents, simCloudRun]);
  const {status: blackboxCloud, retry: retryBlackboxCloud} = useBlackboxCloudSync(
    eventsForCloud, {batteryPct:battery.level, cpuPct:osResources.cpuDemandPct,
      ramMb:osResources.ramPhysicalMb}
  );
  useEffect(() => {
    // Hasta 60 puntos; el mismo tick sustituye la muestra anterior para
    // evitar duplicaciones cuando batería, CPU y RAM cambian en un render.
    const sample = toResourceSample(osResources);
    setResourceHistory((old) => {
      const last = old[old.length - 1];
      if (last && last.tick === sample.tick) return [...old.slice(0, -1), sample];
      return [...old, sample].slice(-60);
    });
  }, [osResources]);

  // AUTOOS V10: puente explícito al kernel Python, sin modificar automáticamente
  // la simulación cuando Streamlit hace un rerun. El botón es deliberado.
  const [pythonKernel, setPythonKernel] = useState<PythonKernelStatus | null>(() => getPythonKernelStatus());
  const [syncingPythonKernel, setSyncingPythonKernel] = useState(false);
  useEffect(() => onPythonKernelStatus(status => {
    setPythonKernel(status);
    setSyncingPythonKernel(false);
  }), []);
  const syncPythonKernel = useCallback(() => {
    const requestId = `v10_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 9)}`;
    // Solo procesos admitidos: el kernel Python asigna RAM First-Fit real.
    // No se envían valores de uso CPU/RAM para forzar artificialmente el backend.
    const processes = simState.processes
      .filter(p => p.state !== 'NUEVO' && p.state !== 'TERMINADO' && p.state !== 'SUSPENDIDO')
      .map(p => ({ pid: p.pid, name: p.name, priority: p.priority,
        burstTime: Math.max(1, p.remainingTime || p.burstTime), memoryMb: p.memoryMb }));
    const submitted = sendKernelSyncRequest({
      type: 'autoos:kernel-sync', requestId, tick: simState.currentTime,
      batteryPct: battery.level, processes,
    });
    if (submitted) setSyncingPythonKernel(true);
  }, [simState.processes, simState.currentTime, battery.level]);

  // Metrics
  const metrics = calculateMetrics(simState);

  // Sync scheduler metrics + device states to cockpit iframe on every sim tick
  useEffect(() => {
    try {
      iframeRef.current?.contentWindow?.postMessage(
        {
          type: 'AUTOOS_SYNC_STATE',
          metrics: calculateMetrics(simState),
          battery,
          devices,
          resources: osResources, // Un mismo cálculo en todas las vistas React.
        },
        '*'
      );
    } catch (_) {}
  }, [simState.currentTime, battery, devices, osResources]);



  // Reset simulation handler
  const handleReset = useCallback(
    (alg?: AlgorithmType, q?: number, procs?: Process[]) => {
      setIsPlaying(false);
      const targetAlg = alg || algorithm;
      const targetQ = q !== undefined ? q : quantum;
      const targetProcs = procs || baseProcesses;
      const freshState = createInitialSimulationState(targetProcs, targetAlg, targetQ);
      setSimCloudRun(n => n + 1);
      setSimState(freshState);
    },
    [algorithm, quantum, baseProcesses]
  );

  const handleAlgorithmChange = (newAlg: AlgorithmType) => {
    if (userRole === 'pasajero') {
      handleRoleRestricted('Modificar Algoritmo de Planificación de CPU');
      return;
    }
    setAlgorithm(newAlg);
    handleReset(newAlg, quantum);
  };

  const handleQuantumChange = (newQ: number) => {
    if (userRole === 'pasajero') {
      handleRoleRestricted('Ajustar Quantum de Tiempo');
      return;
    }
    setQuantum(newQ);
    if (algorithm === 'RR') {
      handleReset(algorithm, newQ);
    }
  };

  const handleStepForward = useCallback(() => {
    if (userRole === 'pasajero') {
      handleRoleRestricted('Avanzar Ciclos de CPU Manualmente');
      return;
    }
    setSimState((prev) => stepSimulationTick(prev, battery.isLowBatteryMode));
  }, [battery.isLowBatteryMode, userRole]);

  const handleTogglePlay = () => {
    if (userRole === 'pasajero') {
      handleRoleRestricted('Iniciar / Pausar la Ejecución de CPU');
      return;
    }
    setIsPlaying(!isPlaying);
  };

  // Simulation timer loop
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  useEffect(() => {
    if (isPlaying) {
      if (simState.isFinished) {
        setIsPlaying(false);
        return;
      }
      timerRef.current = setInterval(() => {
        setSimState((prev) => {
          if (prev.isFinished) {
            setIsPlaying(false);
            return prev;
          }
          return stepSimulationTick(prev, battery.isLowBatteryMode);
        });
      }, speedMs);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, speedMs, battery.isLowBatteryMode, simState.isFinished]);

  // Handle Low Battery adjustment
  const handleUpdateBatteryLevel = (newLevel: number) => {
    const isCritical = newLevel <= 10;
    const isLow = newLevel <= 20;
    const voltage = Math.round(340 + (newLevel / 100) * 60);
    const isLowMode = isLow || isCritical;

    setBattery({
      level: newLevel,
      voltage,
      temperature: isCritical ? 56 : 28,
      isLowBatteryMode: isLowMode,
      isCriticalBatteryMode: isCritical,
      autoThrottlingEnabled: true,
      powerSavingWattsSaved: isLowMode ? 90 : 0,
    });

    setSimState((prev) => {
      const updatedProcesses = prev.processes.map((p) => {
        if (isLowMode && (p.category === 'multimedia' || p.category === 'confort' || p.priority >= 4)) {
          if (p.state !== 'TERMINADO') {
            return {
              ...p,
              state: 'SUSPENDIDO' as const,
              suspendedDueToBattery: true,
            };
          }
        } else if (!isLowMode && p.suspendedDueToBattery) {
          return {
            ...p,
            state: 'LISTO' as const,
            suspendedDueToBattery: false,
          };
        }
        return p;
      });

      const updatedReady = isLowMode
        ? prev.readyQueue.filter((p) => p.category !== 'multimedia' && p.category !== 'confort' && p.priority < 4)
        : [...prev.readyQueue];

      if (!isLowMode) {
        updatedProcesses.forEach((p) => {
          if (p.state === 'LISTO' && !updatedReady.some((rq) => rq.pid === p.pid)) {
            updatedReady.push(p);
          }
        });
      }
      return {
        ...prev,
        processes: updatedProcesses,
        readyQueue: updatedReady,
        events: [
          {
            id: `evt-bat-${Date.now()}`,
            time: prev.currentTime,
            timestamp: new Date().toLocaleTimeString(),
            type: 'BATTERY_ALERT',
            message: isLowMode
              ? `⚡ [BATERÍA BAJA ${newLevel}%] Activado Limp-Mode: Procesos de confort y multimedia suspendidos para proteger la tracción y dirección.`
              : `✓ [BATERÍA NOMINAL ${newLevel}%] Carga restablecida al ${newLevel}%. Procesos reactivados.`,
            severity: isCritical ? 'critical' : isLow ? 'warning' : 'success',
          },
          ...prev.events,
        ],
      };
    });
  };

  const handleTogglePowerSaving = () => {
    handleUpdateBatteryLevel(battery.isLowBatteryMode ? 85 : 18);
  };

  // Critical Process injection with Device State Reflection
  const handleInjectCriticalProcess = (
    procData: Omit<Process, 'waitingTime' | 'turnaroundTime'>,
    deviceCode?: string,
    dtc?: string,
    failureMode?: string
  ) => {
    const fullProc: Process = {
      ...procData,
      waitingTime: 0,
      turnaroundTime: 0,
    };

    // 1. Update Hardware Devices Matrix
    if (deviceCode) {
      setDevices((prev) =>
        prev.map((d) => {
          if (d.code === deviceCode) {
            const isCritical = procData.priority === 1;
            return {
              ...d,
              status: isCritical ? ('falla' as const) : ('degradado' as const),
              health: isCritical ? 15 : 60,
              activeDtc: dtc || d.activeDtc || 'U0100-87',
              failureMode: failureMode || procData.name,
            };
          }
          return d;
        })
      );
    }
    // 2. Dispatch process into CPU Scheduler
    setBaseProcesses((prev) => [...prev, fullProc]);

    setSimState((prev) => {
      const newProc = { ...fullProc };
      const currentT = prev.currentTime;
      const updatedProcesses = [...prev.processes, newProc];
      let updatedRunning = prev.runningProcess;
      let preemptedId = null;
      let newEvents = [...prev.events];
      const updatedReady = [...prev.readyQueue];

      newEvents.unshift({
        id: `evt-crit-inj-${newProc.pid}-${currentT}`,
        time: currentT,
        timestamp: new Date().toLocaleTimeString(),
        type: 'CRITICAL_INJECT',
        message: `🚨 PROCESO CRÍTICO ASIL-D INYECTADO! '${newProc.name}' [DTC: ${dtc || 'U0100'}] (PID ${newProc.pid}, P${newProc.priority}) ingresa a la CPU.`,
        pid: newProc.pid,
        severity: 'critical',
      });

      if (prev.algorithm === 'PRIORITY_PREEMPTIVE' && updatedRunning && updatedRunning.priority > 1) {
        preemptedId = updatedRunning.pid;
        const preempted = { ...updatedRunning, state: 'LISTO' as const };
        updatedReady.unshift(preempted);
        newProc.state = 'EJECUTANDO';
        newProc.startTime = currentT;
        newProc.responseTime = 0;
        updatedRunning = newProc;

        newEvents.unshift({
          id: `evt-crit-preempt-${newProc.pid}-${currentT}`,
          time: currentT,
          timestamp: new Date().toLocaleTimeString(),
          type: 'PREEMPTION',
          message: `⚡ DESALOJO PREEMPTIVO! PID ${newProc.pid} (${newProc.name}) desaloja a PID ${preempted.pid} (${preempted.name}) en el núcleo.`,
          pid: newProc.pid,
          severity: 'critical',
        });
      } else {
        newProc.state = 'LISTO';
        updatedReady.push(newProc);
      }

      return {
        ...prev,
        processes: updatedProcesses,
        readyQueue: updatedReady,
        runningProcess: updatedRunning,
        preemptedProcessId: preemptedId,
        events: newEvents,
      };
    });

    // 3. Post notification to Cockpit iframe
    try {
      iframeRef.current?.contentWindow?.postMessage(
        {
          type: 'AUTOOS_HARDWARE_FAULT',
          deviceCode,
          dtc,
          name: procData.name,
        },
        '*'
      );
    } catch (_) {}
  };

  // Reset single device
  const handleResetDevice = (deviceCode: string) => {
    if (userRole !== 'mecanico') {
      handleRoleRestricted('Restablecer Dispositivo de Hardware (Acción exclusiva del Administrador / Mecánico)');
      return;
    }
    setDevices((prev) =>
      prev.map((d) => {
        if (d.code === deviceCode) {
          return {
            ...d,
            status: 'operativo',
            health: 98,
            activeDtc: null,
            failureMode: null,
          };
        }
        return d;
      })
    );

    setSimState((prev) => ({
      ...prev,
      events: [
        {
          id: `evt-dev-rst-${deviceCode}-${Date.now()}`,
          time: prev.currentTime,
          timestamp: new Date().toLocaleTimeString(),
          type: 'STATE_CHANGE',
          message: `✓ Calibración OBD-II completada: Dispositivo [${deviceCode}] restablecido a OPERATIVO (100% Nominal).`,
          severity: 'success',
        },
        ...prev.events,
      ],
    }));

    try {
      iframeRef.current?.contentWindow?.postMessage(
        {
          type: 'AUTOOS_RESET_DEVICE',
          deviceCode,
        },
        '*'
      );
    } catch (_) {}
  };

  // Reset all devices and faults
  const handleResetAllDevices = () => {
    if (userRole !== 'mecanico') {
      handleRoleRestricted('Restablecer Fallas del Sistema (Acción exclusiva del Administrador / Mecánico)');
      return;
    }
    setDevices(INITIAL_VEHICLE_DEVICES);

    setSimState((prev) => ({
      ...prev,
      events: [
        {
          id: `evt-dev-rstall-${Date.now()}`,
          time: prev.currentTime,
          timestamp: new Date().toLocaleTimeString(),
          type: 'STATE_CHANGE',
          message: `✓ RESTABLECIMIENTO GLOBAL: Todos los subsistemas y buses CAN/Ethernet restablecidos a 100% NOMINAL ASIL-D.`,
          severity: 'success',
        },
        ...prev.events,
      ],
    }));

    try {
      iframeRef.current?.contentWindow?.postMessage(
        {
          type: 'AUTOOS_RESET_ALL_FAULTS',
        },
        '*'
      );
    } catch (_) {}
  };

  // Quick fault trigger on single device
  const handleTriggerQuickFault = (deviceCode: string) => {
    const dev = devices.find((d) => d.code === deviceCode) || INITIAL_VEHICLE_DEVICES[0];
    const dtc = dev.activeDtc || 'P0100-F1';
    const procData: Omit<Process, 'waitingTime' | 'turnaroundTime'> = {
      pid: Math.floor(Math.random() * 800) + 200,
      name: `Falla Simulada en ${dev.name.split('/')[0]}`,
      category: dev.subsystem === 'Seguridad Dinámica' ? 'seguridad' : dev.subsystem === 'Sensores' ? 'sensor' : 'control',
      arrivalTime: simState.currentTime,
      burstTime: 4,
      remainingTime: 4,
      priority: 1,
      critical: true,
      color: '#ef4444',
      state: 'LISTO',
      powerConsumptionWatts: 50,
      cpuUsagePct: 35,
      memoryMb: 128,
    };
    handleInjectCriticalProcess(procData, deviceCode, dtc, 'Prueba de Diagnóstico Forzado OBD-II');
  };

  // Add custom process
  const handleAddCustomProcess = (procData: Omit<Process, 'waitingTime' | 'turnaroundTime'>) => {
    if (userRole === 'pasajero') {
      handleRoleRestricted('Crear Nuevos Procesos en el Kernel');
      return;
    }

    const fullProc: Process = {
      ...procData,
      waitingTime: 0,
      turnaroundTime: 0,
    };

    setBaseProcesses((prev) => [...prev, fullProc]);

    setSimState((prev) => {
      const newProc = { ...fullProc };
      const isReadyNow = newProc.arrivalTime <= prev.currentTime;
      newProc.state = isReadyNow ? 'LISTO' : 'NUEVO';
      const updatedProcs = [...prev.processes, newProc];
      const updatedReady = isReadyNow ? [...prev.readyQueue, newProc] : [...prev.readyQueue];

      return {
        ...prev,
        processes: updatedProcs,
        readyQueue: updatedReady,
        events: [
          {
            id: `evt-add-${newProc.pid}-${prev.currentTime}`,
            time: prev.currentTime,
            timestamp: new Date().toLocaleTimeString(),
            type: 'ARRIVAL',
            message: `Proceso '${newProc.name}' (PID ${newProc.pid}, Ráfaga: ${newProc.burstTime}s, Prio: ${newProc.priority}) añadido.`,
            pid: newProc.pid,
            severity: 'info',
          },
          ...prev.events,
        ],
      };
    });
  };

  // Process table actions
  const handleToggleSuspend = (pid: number) => {
    setSimState((prev) => {
      const updated = prev.processes.map((p) => {
        if (p.pid === pid) {
          const nextState: ProcessState = p.state === 'SUSPENDIDO' ? 'LISTO' : 'SUSPENDIDO';
          return { ...p, state: nextState };
        }
        return p;
      });

      const proc = updated.find((p) => p.pid === pid);
      let ready = [...prev.readyQueue];
      if (proc?.state === 'SUSPENDIDO') {
        ready = ready.filter((p) => p.pid !== pid);
      } else if (proc?.state === 'LISTO') {
        if (!ready.some((p) => p.pid === pid)) ready.push(proc);
      }

      return {
        ...prev,
        processes: updated,
        readyQueue: ready,
        events: [
          {
            id: `evt-user-susp-${pid}-${prev.currentTime}`,
            time: prev.currentTime,
            timestamp: new Date().toLocaleTimeString(),
            type: 'STATE_CHANGE',
            message: `Estado de PID ${pid} (${proc?.name}) cambiado a [${proc?.state}].`,
            pid,
            severity: 'info',
          },
          ...prev.events,
        ],
      };
    });
  };

  const handleTerminateProcess = (pid: number) => {
    setSimState((prev) => {
      const proc = prev.processes.find((p) => p.pid === pid);
      const updated = prev.processes.map((p) => {
        if (p.pid === pid) {
          return {
            ...p,
            state: 'TERMINADO' as const,
            completionTime: prev.currentTime,
            remainingTime: 0,
            turnaroundTime: prev.currentTime - p.arrivalTime,
            waitingTime: Math.max(0, prev.currentTime - p.arrivalTime - (p.burstTime - p.remainingTime)),
          };
        }
        return p;
      });

      const ready = prev.readyQueue.filter((p) => p.pid !== pid);
      let running = prev.runningProcess;
      if (running && running.pid === pid) {
        running = null;
      }

      return {
        ...prev,
        processes: updated,
        readyQueue: ready,
        runningProcess: running,
        events: [
          {
            id: `evt-kill-${pid}-${prev.currentTime}`,
            time: prev.currentTime,
            timestamp: new Date().toLocaleTimeString(),
            type: 'COMPLETION',
            message: `Proceso PID ${pid} (${proc?.name}) finalizado (SIGKILL).`,
            pid,
            severity: 'warning',
          },
          ...prev.events,
        ],
      };
    });
  };


  // Centro de Simulación: estos controladores modifican el mismo estado que usa
  // el scheduler, la matriz de dispositivos y el cockpit (no son datos de maqueta).
  const handleSimulatorStart = useCallback((id: ScenarioId) => {
    setIsPlaying(false);
    const fresh = initialScenarioState(id, INITIAL_VEHICLE_DEVICES);
    setAlgorithm('PRIORITY_PREEMPTIVE');
    setQuantum(2);
    setBaseProcesses(INITIAL_VEHICLE_PROCESSES.map((p) => ({ ...p, waitingTime: 0, turnaroundTime: 0 })));
    setBattery(fresh.battery);
    setDevices(fresh.devices);
    setSimCloudRun(n => n + 1);
    setSimState(fresh.state);
    const definition = scenarioById(id);
    setDriveSpeedKmh(definition.speed);
    setDriveWeather(definition.weather);
    setTripEnergyWh(0);
    setResourceHistory([]);
    try {
      iframeRef.current?.contentWindow?.postMessage({ type: 'AUTOOS_RESET_ALL_FAULTS' }, '*');
      const affected = fresh.devices.filter((d) => d.status !== 'operativo');
      affected.forEach((d) => iframeRef.current?.contentWindow?.postMessage({ type: 'AUTOOS_HARDWARE_FAULT', deviceCode: d.code, dtc: d.activeDtc, name: d.failureMode }, '*'));
    } catch (_) {}
  }, []);

  const handleSimulatorAction = useCallback((action: SimulationAction) => {
    setSimState((prev) => applyScenarioAction(prev, action));
    if (action === 'power_save') setBattery((prev) => makeBattery(prev.level, true));
    if (action === 'reduce_speed') setDriveSpeedKmh((prev) => Math.min(prev, 35));
    if (action === 'restart_gps') setDevices((prev) => recoverFault(prev, 'DEV_GPS_01'));
    if (action === 'restart_network') setDevices((prev) => recoverFault(prev, 'DEV_COM_V2X'));
    if (action === 'isolate_camera') setDevices((prev) => prev.map((d) =>
      d.code === 'DEV_CAM_FRONT' ? { ...d, status: 'desconectado' as const, health: 0, failureMode: 'Aislada por el operador' } : d));
    if (action === 'sensor_backup') setDevices((prev) => prev.map((d) =>
      (d.code === 'DEV_RADAR_01' || d.code === 'DEV_LIDAR_01') && d.status === 'operativo'
        ? { ...d, health: 100 } : d));
    if (action === 'prioritize' || action === 'sensor_backup') setAlgorithm('PRIORITY_PREEMPTIVE');
    if (action === 'restart_gps' || action === 'restart_network') {
      const code = action === 'restart_gps' ? 'DEV_GPS_01' : 'DEV_COM_V2X';
      iframeRef.current?.contentWindow?.postMessage({ type: 'AUTOOS_RESET_DEVICE', deviceCode: code }, '*');
    }
  }, []);

  /**
   * Un tick visual equivale a un minuto virtual de conducción acelerada.
   * Consumo = potencia de tracción + procesos admitidos + dispositivos + auxiliares.
   * La misma batería cambia en todas las pestañas; no hay números de maqueta.
   */
  const handleSimulatorDriveTick = useCallback((velocity: number, weather: Weather) => {
    const watts = estimatePowerW(simRef.current, deviceRef.current, velocity, weather, batteryRef.current.isLowBatteryMode).total;
    const energyWhThisTick = watts / 60;
    setDriveSpeedKmh(velocity);
    setDriveWeather(weather);
    setSimState((prev) => advanceOperatingSystemTick(prev, batteryRef.current.isLowBatteryMode));
    setBattery((prev) => batteryAfterEnergyTick(prev, energyWhThisTick));
    setTripEnergyWh((prev) => prev + energyWhThisTick);
    // AUTOOS V11: cualquier tick del SO (ruta o escenario) mueve el GPS activo.
    // Una falla GNSS inmoviliza la última coordenada válida, no el odómetro.
    setMission((prev) => {
      if (!prev.active) return prev;
      const gpsWorking = deviceRef.current.find(d => d.code === 'DEV_GPS_01')?.status === 'operativo';
      return advanceMission(prev, gpsWorking, velocity);
    });
  }, []);

  const handleSimulatorBattery = useCallback((level: number) => {
    setBattery(makeBattery(level, level <= 10));
    setSimState((prev) => simEvent(prev, `Batería configurada a ${level}% desde laboratorio libre.`, level <= 20 ? 'warning' : 'info'));
  }, []);

  const handleSimulatorFault = useCallback((deviceCode: string) => {
    setDevices((prev) => markFault(prev, deviceCode));
    setSimState((prev) => insertWorkload(simEvent(prev, `Falla OBD simulada en dispositivo ${deviceCode}`, 'critical'), 'diagnostic'));
    iframeRef.current?.contentWindow?.postMessage({ type: 'AUTOOS_HARDWARE_FAULT', deviceCode, dtc: 'SIM-FAULT-01', name: 'Falla de laboratorio' }, '*');
  }, []);

  const handleSimulatorStress = useCallback(() => {
    setSimState((prev) => insertWorkload(prev, 'cpu'));
  }, []);

  const handleSimulatorWeather = useCallback((weather: Weather) => {
    setDriveWeather(weather);
    setDevices((prev) => applyWeather(prev, weather));
    setSimState((prev) => simEvent(prev, `Clima de simulación actualizado: ${weather}. Se recalcula el estado de percepción de sensores.`, weather === 'soleado' ? 'success' : 'warning'));
  }, []);

  /**
   * AUTOOS V11 — Bitácora por evento. No representa medición de vehículo real.
   * La persistencia local no requiere claves; Supabase tiene su diagnóstico aparte.
   */
  const recordMissionEvent = useCallback((message: string, severity: 'info'|'warning'|'critical' = 'info', kind: MissionEvent['kind'] = 'RUTA') => {
    const event:MissionEvent={id:`${Date.now()}_${Math.random().toString(36).slice(2,7)}`,
      tick:simRef.current.currentTime,timestamp:new Date().toISOString(),kind,severity,message};
    setMissionEvents(old=>[event,...old].slice(0,150));
  }, []);

  const routeSelect = useCallback((id:RouteId) => {
    setMission(createMission(id));recordMissionEvent(`Seleccionada ruta didáctica: ${id}.`);
  },[recordMissionEvent]);
  const missionStart = useCallback(() => {
    setMission(prev=>startMission(prev.routeId,prev.speedKmh));
    recordMissionEvent('Navegación iniciada: el SO supervisará recursos y señales.');
  },[recordMissionEvent]);
  const missionStop = useCallback(() => {
    setMission(prev=>({...prev,active:false}));setDriveSpeedKmh(0);
    recordMissionEvent('Ruta detenida por el operador.');
  },[recordMissionEvent]);
  const missionSpeed = useCallback((speed:number)=>{
    setMission(prev=>({...prev,speedKmh:speed}));
  },[]);
  const missionTick = useCallback(()=>{
    if(!mission.active)return;
    const working=deviceRef.current.find(d=>d.code==='DEV_GPS_01')?.status==='operativo';
    handleSimulatorDriveTick(mission.speedKmh,driveWeather);
    recordMissionEvent(working
      ?`Ruta virtual: +${(mission.speedKmh/60).toFixed(2)} km; se actualizan CPU, RAM y batería.`
      :'GNSS sin señal: posición congelada y odómetro virtual en marcha.',
      working?'info':'warning', 'GPS');
  },[mission.active,mission.speedKmh,driveWeather,handleSimulatorDriveTick,recordMissionEvent]);
  // ÚNICO reloj de GPS fuera del laboratorio. En Simulación, su propio
  // onDriveTick dispara handleSimulatorDriveTick para no consumir dos veces.
  useEffect(() => {
    if (!mission.active || activeTab === 'SIMULATOR') return;
    const interval = window.setInterval(missionTick, 1800);
    return () => window.clearInterval(interval);
  }, [mission.active, activeTab, missionTick]);

  const injectMissionFault=useCallback(()=>{
    if(userRole!=='mecanico'){handleRoleRestricted('Inyectar fallo GPS del laboratorio');return;}
    handleSimulatorFault('DEV_GPS_01');recordMissionEvent('Falla GNSS inyectada por mecánico.','critical','GPS');
  },[userRole,handleSimulatorFault,recordMissionEvent]);

  const suspendedProcesses = simState.processes.filter((p) => p.state === 'SUSPENDIDO');

  // Hardware health calculations for top banner
  const failingDevices = devices.filter((d) => d.status === 'falla' || d.status === 'desconectado');
  const degradedDevices = devices.filter((d) => d.status === 'degradado');
  const avgHealth = Math.round(devices.reduce((acc, d) => acc + d.health, 0) / devices.length);

  // GPS device specific status
  const gpsDevice = devices.find((d) => d.code === 'DEV_GPS_01');
  const isGpsFailed = gpsDevice?.status === 'falla' || gpsDevice?.status === 'desconectado';
  const gpsActiveDtc = gpsDevice?.activeDtc;

  return (
    <>
    <div data-autoos-theme={theme} className={`min-h-screen autoos-module-app flex flex-col font-sans transition-colors duration-200 bg-[var(--bg-base)] text-[var(--text-primary)] ${showCinematicMenu ? 'hidden' : ''}`}>
      {/* AUTOOS_MODULE_SCENE_V2
          Cabecera editorial animada. La lógica de roles, nube y simulación
          sigue definida en App.tsx; este componente SOLO recibe callbacks. */}
      <ModuleScene
        active={activeTab}
        role={userRole}
        batteryLevel={battery.level}
        theme={theme}
        status={failingDevices.length > 0 ? 'failure' : degradedDevices.length > 0 ? 'warning' : 'normal'}
        supabaseConfigured={isSupabaseConfigured()}
        audioMuted={audioMuted}
        onToggleAudio={() => setAudioMuted((prev) => !prev)}
        onHome={() => { setIsPlaying(false); setCockpitWorkspace(false); setShowCinematicMenu(true); }}
        onSelect={(destination) => {
          setActiveTab(destination);
          if (destination === 'COCKPIT') setCockpitWorkspace(false);
        }}
        onRoleChange={(nextRole: UserRole) => {
          setUserRole(nextRole);
          if (nextRole !== 'mecanico' && activeTab === 'SCHEDULER') setActiveTab('HOME');
        }}
        onThemeChange={toggleTheme}
        onRestricted={handleRoleRestricted}
      />
      {/* Orientación accesible: qué hace el módulo y cómo usarlo. */}
      <ModuleOrientationV3 active={activeTab} />

      {/* RBAC Rejection Modal Alert */}
      {rbacAlertMessage && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="relative w-full max-w-md autoos-card border-2 border-red-500 rounded-3xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-[var(--border-color)]">
              <div className="flex items-center gap-2.5 text-red-500 font-bold">
                <ShieldAlert className="w-6 h-6 animate-bounce" />
                <h3 className="font-serif text-base text-[var(--text-primary)]">Control de Acceso RBAC</h3>
              </div>
              <button
                onClick={() => setRbacAlertMessage(null)}
                className="p-1 rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <p className="text-xs text-[var(--text-primary)] leading-relaxed">
              {rbacAlertMessage}
            </p>
            <div className="flex justify-end pt-2">
              <button
                onClick={() => setRbacAlertMessage(null)}
                className="px-4 py-2 rounded-xl bg-[var(--accent-primary)] text-white text-xs font-bold"
              >
                Entendido
              </button>
            </div>
          </div>
        </div>
      )}

      {/* AUTOOS V11: páginas de operación REAL sobre estado compartido.
          El Planificador original y las herramientas heredadas se conservan. */}
      {(activeTab === 'HOME' || activeTab === 'GPS' || activeTab === 'BLACKBOX' || activeTab === 'CLOUD') && (
        <main className="v11-operations" aria-label="Centro de operaciones vehiculares">
          <AutoOSModulesV11
            page={activeTab} resources={osResources} resourceHistory={resourceHistory}
            simState={simState} battery={battery} devices={devices}
            mission={mission} missionEvents={missionEvents} role={userRole}
            blackboxCloud={blackboxCloud} onRetryBlackbox={retryBlackboxCloud}
            onNavigate={(next)=>{
              if(next==='SCHEDULER'&&userRole!=='mecanico'){handleRoleRestricted('Abrir planificador técnico');return;}
              setActiveTab(next);if(next==='COCKPIT')setCockpitWorkspace(false);
            }}
            onRoute={routeSelect} onMissionStart={missionStart} onMissionStop={missionStop}
            onMissionTick={missionTick} onMissionSpeed={missionSpeed}
            onInjectGpsFault={injectMissionFault}
          />
        </main>
      )}

      {/* TAB 1: SCHEDULER & SIMULATORS */}
      <main className={`autoos-module-scheduler flex-1 max-w-7xl w-full mx-auto p-4 lg:p-8 space-y-6 ${activeTab === 'SCHEDULER' && userRole !== 'conductor' && userRole !== 'pasajero' ? '' : 'hidden'}`}>
        {/* La misma instantánea de Simulación, sin duplicar estado. */}
        <PythonKernelPanel snapshot={osResources} status={pythonKernel} onSync={syncPythonKernel} syncing={syncingPythonKernel} />
        <OSResourceMonitor snapshot={osResources} history={resourceHistory} compact />
        {/* Dynamic Global Vehicle Health HUD Banner */}
        <div className={`p-4 rounded-2xl border transition-all duration-300 shadow-md flex flex-wrap items-center justify-between gap-3 font-mono text-xs ${
          failingDevices.length > 0
            ? 'bg-red-500/15 border-red-500 text-red-600 dark:text-red-400 ring-2 ring-red-500/30'
            : degradedDevices.length > 0
            ? 'bg-amber-500/15 border-amber-500 text-amber-600 dark:text-amber-400'
            : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-600 dark:text-emerald-400'
        }`}>
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-xl shrink-0 ${
              failingDevices.length > 0
                ? 'bg-red-600 text-white animate-bounce'
                : degradedDevices.length > 0
                ? 'bg-amber-500 text-white'
                : 'bg-emerald-500/20 text-emerald-500'
            }`}>
              {failingDevices.length > 0 ? (
                <ShieldAlert className="w-5 h-5" />
              ) : degradedDevices.length > 0 ? (
                <AlertTriangle className="w-5 h-5" />
              ) : (
                <CheckCircle className="w-5 h-5" />
              )}
            </div>
            <div>
              <div className="font-bold text-sm flex items-center gap-2">
                <span>
                  {failingDevices.length > 0
                    ? `🚨 ALERTA ASIL-D: ${failingDevices.length} FALLA(S) ACTIVA(S) EN HARDWARE`
                    : degradedDevices.length > 0
                    ? `⚠️ ADVERTENCIA: ${degradedDevices.length} SUBSISTEMA(S) EN MODO DEGRADADO`
                    : '✓ SISTEMA VEHICULAR NOMINAL (100% OPERATIVO)'}
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-900/10 dark:bg-white/10 font-bold">
                  Salud: {avgHealth}%
                </span>
              </div>
              <p className="text-[11px] opacity-90">
                {failingDevices.length > 0
                  ? `Fallas detectadas en: ${failingDevices.map((d) => `${d.name.split('/')[0]} [${d.activeDtc || 'DTC'}]`).join(', ')}. Conmutado a algoritmos de contingencia pre-emptivos.`
                  : degradedDevices.length > 0
                  ? `Subsistemas con rendimiento reducido: ${degradedDevices.map((d) => d.name.split('/')[0]).join(', ')}.`
                  : 'Buses CAN-FD, Automotive Ethernet y LIN sincronizados. Planificación de tiempo real en rango de latencia < 2ms.'}
              </p>
            </div>
          </div>

          {/* Quick Clear Faults Button */}
          {failingDevices.length > 0 && (
            <button
              onClick={() => {
                if (userRole !== 'mecanico') {
                  handleRoleRestricted('Restablecer Fallas del Sistema (Acción exclusiva del Administrador / Mecánico)');
                  return;
                }
                handleResetAllDevices();
              }}
              className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white font-bold text-xs uppercase tracking-wider shadow-md hover:scale-105 transition flex items-center gap-1.5"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Restablecer Fallas</span>
            </button>
          )}
        </div>

        {/* Controls Bar */}
        <section className="autoos-card rounded-3xl p-5 shadow-xl">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="space-y-1.5">
              <label className="text-[11px] font-mono text-[var(--text-muted)] uppercase tracking-wider block font-bold">
                Algoritmo de Planificación:
              </label>
              <div className="flex flex-wrap gap-1.5 autoos-surface p-1.5 rounded-2xl">
                <button
                  onClick={() => handleAlgorithmChange('FCFS')}
                  className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold transition-all ${
                    algorithm === 'FCFS'
                      ? 'bg-[var(--accent-primary)] text-white shadow-sm'
                      : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  FCFS (First-Come)
                </button>
                <button
                  onClick={() => handleAlgorithmChange('RR')}
                  className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold transition-all ${
                    algorithm === 'RR'
                      ? 'bg-[var(--accent-primary)] text-white shadow-sm'
                      : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  Round Robin (RR)
                </button>
                <button
                  onClick={() => handleAlgorithmChange('PRIORITY')}
                  className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold transition-all ${
                    algorithm === 'PRIORITY'
                      ? 'bg-[var(--accent-primary)] text-white shadow-sm'
                      : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  Prioridad No Apropiativa
                </button>
                <button
                  onClick={() => handleAlgorithmChange('PRIORITY_PREEMPTIVE')}
                  className={`px-3 py-1.5 rounded-xl text-xs font-mono font-bold transition-all ${
                    algorithm === 'PRIORITY_PREEMPTIVE'
                      ? 'bg-[var(--accent-primary)] text-white shadow-sm'
                      : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  Prioridad Apropiativa (Preemptive)
                </button>
              </div>
            </div>

            {algorithm === 'RR' && (
              <div className="space-y-1.5">
                <label className="text-[11px] font-mono text-[var(--text-muted)] uppercase tracking-wider block font-bold">
                  Quantum (q):
                </label>
                <div className="flex items-center gap-1.5 autoos-surface p-1.5 rounded-2xl font-mono text-xs">
                  {[1, 2, 3, 4, 5].map((q) => (
                    <button
                      key={q}
                      onClick={() => handleQuantumChange(q)}
                      className={`w-7 h-7 rounded-xl font-bold transition ${
                        quantum === q
                          ? 'bg-[var(--accent-primary)] text-white'
                          : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                      }`}
                    >
                      {q}s
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Playback & Action Controls */}
            <div className="space-y-1.5">
              <label className="text-[11px] font-mono text-[var(--text-muted)] uppercase tracking-wider block font-bold">
                Controles de Simulación:
              </label>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleTogglePlay}
                  disabled={simState.isFinished}
                  className={`px-4 py-2 rounded-xl font-bold text-xs flex items-center gap-2 transition shadow-md ${
                    isPlaying
                      ? 'bg-amber-500 hover:bg-amber-400 text-white'
                      : 'bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50'
                  }`}
                >
                  {isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current" />}
                  <span>{isPlaying ? 'Pausar' : 'Reproducir'}</span>
                </button>
                <button
                  onClick={handleStepForward}
                  disabled={isPlaying || simState.isFinished}
                  className="px-3 py-2 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-50"
                >
                  <SkipForward className="w-4 h-4 text-[var(--accent-primary)]" />
                  <span>Paso (+1s)</span>
                </button>
                <button
                  onClick={() => handleReset()}
                  className="px-3 py-2 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-muted)] hover:text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold flex items-center gap-1.5 transition"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>Reiniciar</span>
                </button>
                <button
                  onClick={() => setIsCompareModalOpen(true)}
                  className="px-3 py-2 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold flex items-center gap-1.5 transition"
                >
                  <BarChart3 className="w-4 h-4 text-[var(--accent-primary)]" />
                  <span>Comparar</span>
                </button>
                <button
                  onClick={() => {
                    if (userRole === 'pasajero') {
                      handleRoleRestricted('Crear Procesos en el Sistema');
                      return;
                    }
                    setIsNewProcessModalOpen(true);
                  }}
                  className="px-3.5 py-2 rounded-xl bg-[var(--accent-primary)] text-white font-bold text-xs flex items-center gap-1.5 transition shadow-sm hover:opacity-90"
                >
                  <PlusCircle className="w-4 h-4" />
                  <span>Añadir</span>
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Metrics KPI Cards */}
        <section className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5 font-mono">
          <div className="autoos-card p-3.5 rounded-2xl shadow-sm">
            <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider block font-bold">Reloj Simulado</span>
            <strong className="text-xl text-[var(--accent-primary)] font-bold">t = {simState.currentTime}s</strong>
          </div>
          <div className="autoos-card p-3.5 rounded-2xl shadow-sm">
            <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider block font-bold">Uso de CPU</span>
            <strong className="text-xl text-emerald-600 dark:text-emerald-400 font-bold">{metrics.cpuUtilization}%</strong>
          </div>
          <div className="autoos-card p-3.5 rounded-2xl shadow-sm">
            <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider block font-bold">T. Espera Prom</span>
            <strong className="text-xl text-amber-600 dark:text-amber-400 font-bold">{metrics.averageWaitingTime}s</strong>
          </div>
          <div className="autoos-card p-3.5 rounded-2xl shadow-sm">
            <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider block font-bold">T. Retorno Prom</span>
            <strong className="text-xl text-[var(--text-primary)] font-bold">{metrics.averageTurnaroundTime}s</strong>
          </div>
          <div className="autoos-card p-3.5 rounded-2xl shadow-sm">
            <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider block font-bold">Conmutaciones</span>
            <strong className="text-xl text-[var(--text-primary)] font-bold">{metrics.contextSwitches}</strong>
          </div>
          <div className="autoos-card p-3.5 rounded-2xl shadow-sm">
            <span className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider block font-bold">Completados</span>
            <strong className="text-xl text-emerald-600 dark:text-emerald-400 font-bold">
              {metrics.completedCount} / {metrics.totalProcesses}
            </strong>
          </div>
        </section>

        {/* Gantt Chart */}
        <section>
          <GanttChart
            slots={simState.ganttSlots}
            currentTime={simState.currentTime}
            totalTime={simState.currentTime}
            processes={simState.processes}
          />
        </section>

        {/* CPU Core & Ready Queue */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <CPUCoreCard
              runningProcess={simState.runningProcess}
              algorithm={simState.algorithm}
              quantum={simState.quantum}
              quantumRemaining={simState.quantumRemaining}
              preemptedProcessId={simState.preemptedProcessId}
              contextSwitches={simState.contextSwitchCount}
              currentTime={simState.currentTime}
              isLowBatteryActive={battery.isLowBatteryMode}
            />
          </div>
          <div className="lg:col-span-2">
            <QueueVisualizer
              readyQueue={simState.readyQueue}
              algorithm={simState.algorithm}
              suspendedProcesses={suspendedProcesses}
            />
          </div>
        </section>

        {/* Diagnóstico avanzado: conserva la matriz original sin distraer
            del ejercicio principal de planificación CPU. */}
        <details className="autoos-advanced-v3">
          <summary>DIAGNÓSTICO AVANZADO · Hardware y sensores
            <small>11 dispositivos: calibración, inyección de fallas y estado de buses</small>
          </summary>
          <section>
          <HardwareStatusGrid
            devices={devices}
            onResetDevice={handleResetDevice}
            onResetAllDevices={handleResetAllDevices}
            onTriggerQuickFault={handleTriggerQuickFault}
            userRole={userRole}
            onRoleRestricted={handleRoleRestricted}
            onInjectCriticalProcess={handleInjectCriticalProcess}
            onResetAllScenarios={handleResetAllDevices}
            currentTime={simState.currentTime}
          />
          </section>
        </details>


        {/* The Two Dedicated Simulators: Battery and Configurable Fault Simulator */}
        <section className="space-y-3">
          <div className="flex items-center gap-2 px-1">
            <Activity className="w-4 h-4 text-[var(--accent-primary)]" />
            <h3 className="text-sm font-serif font-bold text-[var(--text-primary)] uppercase tracking-wider">
              Simuladores de Contingencia y Gestión Energética
            </h3>
          </div>
          <div className="grid grid-cols-1 gap-6">
            <BatterySimulatorPanel
              battery={battery}
              onUpdateBatteryLevel={handleUpdateBatteryLevel}
              onTogglePowerSaving={handleTogglePowerSaving}
              wattsSaved={battery.powerSavingWattsSaved}
              suspendedCount={suspendedProcesses.length}
              userRole={userRole}
              onRoleRestricted={handleRoleRestricted}
            />
          </div>
        </section>

        {/* Process Table & Events Log */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <ProcessTable
              processes={simState.processes}
              onToggleSuspend={handleToggleSuspend}
              onTerminate={handleTerminateProcess}
              currentTime={simState.currentTime}
              userRole={userRole}
              onRoleRestricted={handleRoleRestricted}
            />
          </div>
          <div className="lg:col-span-1">
            <EventsLog events={simState.events} />
          </div>
        </section>
      </main>

      {/* AUTOOS_EXPERIENCE_V5
          «overview» y «security» son pantallas NATIVAS de React, con datos
          existentes de App.tsx. Las herramientas técnicas originales se
          abren en el iframe solamente cuando hacen falta. */}
      <main className={`autoos-module-cockpit flex-1 w-full flex flex-col ${activeTab === 'COCKPIT' ? '' : 'hidden'}`}>
        {/* Monitor del motor didáctico compartido. Los instrumentos heredados son independientes. */}
        <OSResourceMonitor snapshot={osResources} history={resourceHistory} compact />
        {!cockpitWorkspace ? (
          <CockpitExplorerV4 role={userRole} onOpen={(feature: CockpitFeatureId) => {
            setCockpitFeature(feature);
            setCockpitHeight(1200);
            setCockpitWorkspace(true);
          }} />
        ) : (
          <section className="autoos-v4-workspace" aria-label="Herramienta de Conducción">
            {(cockpitFeature === 'overview' || cockpitFeature === 'security') && (
            <div className="autoos-v4-workspace__bar">
              <button type="button" onClick={() => setCockpitWorkspace(false)}>
                ← VOLVER AL EXPLORADOR
              </button>
              <span>{cockpitFeature === 'overview' ? 'Resumen del vehículo' :
                     cockpitFeature === 'security' ? 'Seguridad y perfiles' :
                     'Herramienta interactiva · Control original'}</span>
            </div>
            )}
            {cockpitFeature === 'overview' ? (
              <CockpitOverviewV5
                role={userRole}
                batteryLevel={battery.level}
                devices={devices}
                onOpen={(feature) => { setCockpitFeature(feature); setCockpitHeight(1200); }}
              />
            ) : cockpitFeature === 'security' ? (
              <CockpitSecurityV5
                role={userRole}
                events={simState.events}
                onChangeRole={(nextRole) => {
                  setUserRole(nextRole);
                  // La vista de Seguridad permanece visible para permitir
                  // comparar permisos; RBAC se sigue evaluando en cada módulo.
                }}
                onOpenOriginalAudit={() => { setCockpitFeature('security-original'); setCockpitHeight(1200); }}
              />
            ) : (
              <CockpitToolSceneV6 feature={cockpitFeature} role={userRole}
                onBack={() => setCockpitWorkspace(false)}
                onFeature={(next) => {
                  setCockpitFeature(next);
                  setCockpitHeight(1200);
                }}>
              {/* AUTOOS_V12_APLICADO: BLE requiere permiso en todos los iframes. */}
              <iframe
                ref={iframeRef}
                onLoad={() => {
                  syncIframeState();
                  // El Cockpit heredado puede tardar en montar su React interno.
                  // Usamos el mismo puente V4 que navega por botones REALES.
                  window.setTimeout(() => {
                    const legacyFeature = cockpitFeature === 'overview-original' ? 'overview'
                      : cockpitFeature === 'security-original' ? 'security' : cockpitFeature;
                    iframeRef.current?.contentWindow?.postMessage(
                      { type: 'AUTOOS_V4_OPEN_FEATURE', feature: legacyFeature }, '*');
                    iframeRef.current?.contentWindow?.postMessage({ type: 'AUTOOS_V4_MEASURE' }, '*');
                  }, 180);
                }}
                src={cockpitHtml ? undefined : '/autoos_interactive.html'}
                srcDoc={cockpitHtml || undefined}
                title="AutoOS · Cockpit técnico original"
                allow="bluetooth; clipboard-read; clipboard-write"
                className="autoos-v4-cockpit-frame"
                style={{ '--cockpit-content-height': `${cockpitHeight}px` } as React.CSSProperties}
              />
              </CockpitToolSceneV6>
            )}
          </section>
        )}
      </main>

      {/* TAB 3: INTERACTIVE SCENARIO SIMULATION CENTER */}
      <main className={`autoos-module-simulator flex-1 w-full ${activeTab === 'SIMULATOR' ? '' : 'hidden'}`}>
        <PythonKernelPanel snapshot={osResources} status={pythonKernel} onSync={syncPythonKernel} syncing={syncingPythonKernel} />
        <SimulationCenter
          battery={battery}
          devices={devices}
          state={simState}
          resources={osResources}
          resourceHistory={resourceHistory}
          onOpenScheduler={() => {
            if (userRole === 'mecanico') setActiveTab('SCHEDULER');
            else handleRoleRestricted('Ver planificador técnico del sistema operativo');
          }}
          userRole={userRole}
          onStart={handleSimulatorStart}
          onAction={handleSimulatorAction}
          onDriveTick={handleSimulatorDriveTick}
          onBattery={handleSimulatorBattery}
          onFault={handleSimulatorFault}
          onCpuStress={handleSimulatorStress}
          onWeather={handleSimulatorWeather}
        />
      </main>

      {/* Footer */}
      {(activeTab === 'SCHEDULER' || activeTab === 'SIMULATOR') && userRole === 'mecanico' && (
      <footer className="autoos-surface border-t text-xs text-[var(--text-muted)] py-3.5 px-6 text-center font-mono">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
          <span>AutoOS — Sistema Operativo Vehicular</span>
          <span className="text-[var(--accent-primary)] font-bold">
            {theme === 'dark' ? 'Blue Shift · Modo oscuro' : 'Blue Shift · Modo claro'}
          </span>
          <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5 font-bold">
            <CheckCircle className="w-3.5 h-3.5" /> FCFS • Round Robin • Prioridad • Batería Baja • Falla Configurable • GPS Dinámico
          </span>
        </div>
      </footer>
      )}

      {/* Modals */}
      <AlgorithmComparisonModal
        isOpen={isCompareModalOpen}
        onClose={() => setIsCompareModalOpen(false)}
        processes={baseProcesses}
        quantum={quantum}
      />
      <NewProcessModal
        isOpen={isNewProcessModalOpen}
        onClose={() => setIsNewProcessModalOpen(false)}
        onAddProcess={handleAddCustomProcess}
        currentTime={simState.currentTime}
      />
    </div>
    {/* AUTOOS_CINEMATIC_V1: escena inicial. No desmonta ni reinicia simuladores.
        onNavigate es la única vía para seleccionar una pantalla existente. */}
    {showCinematicMenu && (
      <CinematicMenu
        role={userRole}
        health={avgHealth}
        batteryLevel={battery.level}
        onRoleChange={setUserRole}
        audioMuted={audioMuted}
        onToggleAudio={() => setAudioMuted((prev) => !prev)}
        theme={theme}
        onToggleTheme={toggleTheme}
        onNavigate={(destination: AutoOSModule) => {
          if (destination === 'SCHEDULER' && userRole !== 'mecanico') {
            handleRoleRestricted('Abrir el planificador RTOS');
            return;
          }
          setActiveTab(destination);
          setCockpitWorkspace(false);
          setShowCinematicMenu(false);
        }}
      />
    )}
    </>
  );
}
