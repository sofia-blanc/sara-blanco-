import React, { useState, useEffect, useRef, useCallback } from 'react';
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

import { HardwareStatusGrid } from './components/HardwareStatusGrid';
import { AlgorithmComparisonModal } from './components/AlgorithmComparisonModal';
import { NewProcessModal } from './components/NewProcessModal';
import { EventsLog } from './components/EventsLog';
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
} from 'lucide-react';

const INITIAL_VEHICLE_DEVICES: VehicleDevice[] = [
  {
    id: 'dev_01',
    code: 'DEV_GPS_01',
    name: 'Receptor GNSS / GPS Diferencial',
    subsystem: 'NavegaciÃ³n',
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
    name: 'CÃ¡mara EstereoscÃ³pica ADAS Frontal',
    subsystem: 'VisiÃ³n',
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
    name: 'Sensor LiDAR 360Â° Solid-State',
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
    name: 'Radar MilimÃ©trico 77GHz (ACC)',
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
    name: 'BMS BaterÃ­a LiFePO4 Alta TensiÃ³n',
    subsystem: 'BaterÃ­a',
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
    subsystem: 'Seguridad DinÃ¡mica',
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
    name: 'Actuador DirecciÃ³n ElÃ©ctrica EPS',
    subsystem: 'Seguridad DinÃ¡mica',
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
    name: 'MÃ³dulo TelemetrÃ­a 5G / V2X Cloud',
    subsystem: 'ComunicaciÃ³n',
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
    name: 'ClimatizaciÃ³n y GestiÃ³n TÃ©rmica',
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
  const [activeTab, setActiveTab] = useState<'SCHEDULER' | 'COCKPIT'>('SCHEDULER');

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
  }, [theme, userRole]);

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

  // If role changes to 'conductor', force COCKPIT tab
  useEffect(() => {
    if (userRole === 'conductor' || userRole === 'pasajero') {
      setActiveTab('COCKPIT');
    }
  }, [userRole]);

  // Sync scheduler metrics + device states to cockpit iframe on every sim tick
  useEffect(() => {
    try {
      iframeRef.current?.contentWindow?.postMessage(
        {
          type: 'AUTOOS_SYNC_STATE',
          metrics: calculateMetrics(simState),
          battery,
          devices,
        },
        '*'
      );
    } catch (_) {}
  }, [simState.currentTime, battery, devices]);

  // Bidirectional listener from Cockpit iframe
  useEffect(() => {
    const handleIframeMessage = (e: MessageEvent) => {
      if (!e.data) return;
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
    const roleName = userRole === 'pasajero' ? 'Pasajero' : userRole === 'conductor' ? 'Conductor' : 'MecÃ¡nico';
    setRbacAlertMessage(
      `â›” Acceso Denegado por PolÃ­tica RBAC! El rol actual [${roleName}] no posee privilegios de seguridad para: ${action}. Cambia de rol en la barra superior para continuar.`
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
  const [simState, setSimState] = useState<SimulationState>(() =>
    createInitialSimulationState(baseProcesses, 'RR', 2)
  );

  // Metrics
  const metrics = calculateMetrics(simState);

  // Reset simulation handler
  const handleReset = useCallback(
    (alg?: AlgorithmType, q?: number, procs?: Process[]) => {
      setIsPlaying(false);
      const targetAlg = alg || algorithm;
      const targetQ = q !== undefined ? q : quantum;
      const targetProcs = procs || baseProcesses;
      const freshState = createInitialSimulationState(targetProcs, targetAlg, targetQ);
      setSimState(freshState);
    },
    [algorithm, quantum, baseProcesses]
  );

  const handleAlgorithmChange = (newAlg: AlgorithmType) => {
    if (userRole === 'pasajero') {
      handleRoleRestricted('Modificar Algoritmo de PlanificaciÃ³n de CPU');
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
      handleRoleRestricted('Iniciar / Pausar la EjecuciÃ³n de CPU');
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
              ? `âš¡ [BATERÃA BAJA ${newLevel}%] Activado Limp-Mode: Procesos de confort y multimedia suspendidos para proteger la tracciÃ³n y direcciÃ³n.`
              : `âœ“ [BATERÃA NOMINAL ${newLevel}%] Carga restablecida al ${newLevel}%. Procesos reactivados.`,
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
        message: `ðŸš¨ PROCESO CRÃTICO ASIL-D INYECTADO! '${newProc.name}' [DTC: ${dtc || 'U0100'}] (PID ${newProc.pid}, P${newProc.priority}) ingresa a la CPU.`,
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
          message: `âš¡ DESALOJO PREEMPTIVO! PID ${newProc.pid} (${newProc.name}) desaloja a PID ${preempted.pid} (${preempted.name}) en el nÃºcleo.`,
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
          message: `âœ“ CalibraciÃ³n OBD-II completada: Dispositivo [${deviceCode}] restablecido a OPERATIVO (100% Nominal).`,
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
          message: `âœ“ RESTABLECIMIENTO GLOBAL: Todos los subsistemas y buses CAN/Ethernet restablecidos a 100% NOMINAL ASIL-D.`,
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
      category: dev.subsystem === 'Seguridad DinÃ¡mica' ? 'seguridad' : dev.subsystem === 'Sensores' ? 'sensor' : 'control',
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
    handleInjectCriticalProcess(procData, deviceCode, dtc, 'Prueba de DiagnÃ³stico Forzado OBD-II');
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
            message: `Proceso '${newProc.name}' (PID ${newProc.pid}, RÃ¡faga: ${newProc.burstTime}s, Prio: ${newProc.priority}) aÃ±adido.`,
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
    <div className={`flex flex-col font-sans transition-colors duration-200 bg-[var(--bg-base)] text-[var(--text-primary)] ${activeTab === 'COCKPIT' ? 'h-screen overflow-hidden' : 'min-h-screen'}`}>
      {/* Top Header with Universal Theme Switcher & RBAC Role Selector */}
      <header className="sticky top-0 z-40 autoos-surface border-b px-4 lg:px-8 py-3">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          {/* Brand & Status */}
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-2xl bg-[var(--accent-primary)]/15 text-[var(--accent-primary)] border border-[var(--accent-primary)]/30 shadow-sm">
              <Car className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-serif font-bold text-[var(--text-primary)] tracking-wide">
                  AutoOS <span className="text-[var(--accent-primary)] font-mono text-xs font-semibold">v2.5.0</span>
                </h1>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-bold flex items-center gap-1 ${
                  failingDevices.length > 0
                    ? 'bg-red-500/15 text-red-500 border border-red-500/30 animate-pulse'
                    : degradedDevices.length > 0
                    ? 'bg-amber-500/15 text-amber-500 border border-amber-500/30'
                    : 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
                }`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${
                    failingDevices.length > 0 ? 'bg-red-500 animate-ping' : degradedDevices.length > 0 ? 'bg-amber-500' : 'bg-emerald-500 animate-pulse'
                  }`}></span>
                  {failingDevices.length > 0 ? 'FALLA ACTIVA' : degradedDevices.length > 0 ? 'DEGRADADO' : 'OPERATIVO 100%'}
                </span>
              </div>
              <p className="text-[11px] text-[var(--text-muted)]">
                Sistema Operativo para VehÃ­culo Inteligente â€” RTOS ISO 26262 ASIL-D
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center autoos-card p-1 rounded-2xl border text-xs font-mono">
            {userRole !== 'conductor' && userRole !== 'pasajero' && (
              <button
                onClick={() => setActiveTab('SCHEDULER')}
                className={`px-3.5 py-2 rounded-xl font-bold flex items-center gap-2 transition-all ${
                  activeTab === 'SCHEDULER'
                    ? 'bg-[var(--accent-primary)] text-white shadow-sm'
                    : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                }`}
              >
                <Cpu className="w-4 h-4" />
                <span>Planificador &amp; Simuladores</span>
              </button>
            )}
            <button
              onClick={() => setActiveTab('COCKPIT')}
              className={`px-3.5 py-2 rounded-xl font-bold flex items-center gap-2 transition-all ${
                activeTab === 'COCKPIT'
                  ? 'bg-[var(--accent-primary)] text-white shadow-sm'
                  : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
              }`}
            >
              <Car className="w-4 h-4" />
              <span>Cockpit AutoOS Completo</span>
            </button>
          </div>

          {/* User Role Selector & Universal Theme Switcher */}
          <div className="flex items-center gap-2.5 text-xs font-mono">
            {/* Role RBAC Selector */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl autoos-card border text-[var(--text-primary)]">
              <Shield className="w-3.5 h-3.5 text-[var(--accent-primary)]" />
              <span className="text-[11px] text-[var(--text-muted)] font-semibold">Usuario:</span>
              <select
                value={userRole}
                onChange={(e) => setUserRole(e.target.value as UserRole)}
                className="bg-transparent text-[var(--text-primary)] font-bold text-xs focus:outline-none cursor-pointer"
              >
                <option value="mecanico" className="text-black dark:text-white dark:bg-[#180E24]">ðŸ”§ Carlos VÃ©lez (MecÃ¡nico / Admin)</option>
                <option value="conductor" className="text-black dark:text-white dark:bg-[#180E24]">ðŸš— Laura GÃ³mez (Conductora)</option>
                <option value="pasajero" className="text-black dark:text-white dark:bg-[#180E24]">ðŸ‘¤ AndrÃ©s Rivera (Pasajero)</option>
              </select>
            </div>

            {/* Battery gauge pill */}
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl autoos-card border text-[var(--text-primary)]">
              <BatteryCharging className="w-3.5 h-3.5 text-[var(--accent-primary)]" />
              <span>{battery.level}% ({battery.voltage}V)</span>
            </div>

            {/* Universal Theme Toggle Button */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl autoos-card border hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] transition flex items-center gap-1.5"
              title={theme === 'dark' ? 'Cambiar a Modo Claro (Soft Dove)' : 'Cambiar a Modo Oscuro (Purple Night)'}
            >
              {theme === 'dark' ? (
                <Sun className="w-4 h-4 text-amber-400" />
              ) : (
                <Moon className="w-4 h-4 text-[#391214]" />
              )}
              <span className="hidden md:inline text-[11px]">
                {theme === 'dark' ? 'Modo Claro' : 'Modo Oscuro'}
              </span>
            </button>
          </div>
        </div>
      </header>

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

      {/* TAB 1: SCHEDULER & SIMULATORS */}
      <main className={`flex-1 max-w-7xl w-full mx-auto p-4 lg:p-8 space-y-6 ${activeTab === 'SCHEDULER' ? '' : 'hidden'}`}>
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
                    ? `ðŸš¨ ALERTA ASIL-D: ${failingDevices.length} FALLA(S) ACTIVA(S) EN HARDWARE`
                    : degradedDevices.length > 0
                    ? `âš ï¸ ADVERTENCIA: ${degradedDevices.length} SUBSISTEMA(S) EN MODO DEGRADADO`
                    : 'âœ“ SISTEMA VEHICULAR NOMINAL (100% OPERATIVO)'}
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
                  : 'Buses CAN-FD, Automotive Ethernet y LIN sincronizados. PlanificaciÃ³n de tiempo real en rango de latencia < 2ms.'}
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
                Algoritmo de PlanificaciÃ³n:
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
                Controles de SimulaciÃ³n:
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
                  <span>AÃ±adir</span>
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

        {/* Real-time Hardware & Subsystems Matrix */}
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

        {/* The Two Dedicated Simulators: Battery and Configurable Fault Simulator */}
        <section className="space-y-3">
          <div className="flex items-center gap-2 px-1">
            <Activity className="w-4 h-4 text-[var(--accent-primary)]" />
            <h3 className="text-sm font-serif font-bold text-[var(--text-primary)] uppercase tracking-wider">
              Simuladores de Contingencia y GestiÃ³n EnergÃ©tica
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

      {/* TAB 2: ORIGINAL FULL VEHICLE COCKPIT */}
      <main className={`flex-1 w-full flex flex-col ${activeTab === 'COCKPIT' ? '' : 'hidden'}`}>
        <div className="autoos-surface border-b px-6 py-2.5 flex items-center justify-between text-xs font-mono text-[var(--text-muted)]">
          <span className="flex items-center gap-2">
            <Car className="w-4 h-4 text-[var(--accent-primary)]" />
            <span className="text-[var(--text-primary)] font-semibold">Cockpit AutoOS Completo (VelocÃ­metro, Medidores, Audio Player, Chat y CÃ¡maras)</span>
          </span>
          <span className={`font-bold flex items-center gap-1.5 ${
            failingDevices.length > 0
              ? 'text-red-500 animate-pulse'
              : degradedDevices.length > 0
              ? 'text-amber-500'
              : 'text-emerald-600 dark:text-emerald-400'
          }`}>
            <span className={`w-2 h-2 rounded-full ${
              failingDevices.length > 0 ? 'bg-red-500 animate-ping' : degradedDevices.length > 0 ? 'bg-amber-500' : 'bg-emerald-500 animate-pulse'
            }`}></span>
            {failingDevices.length > 0
              ? `Falla en ${failingDevices.length} Subsistema(s)`
              : degradedDevices.length > 0
              ? 'Rendimiento Degradado'
              : 'Sistemas Activos 100%'}
          </span>
        </div>
        <iframe
          ref={iframeRef}
          onLoad={syncIframeState}
          src={cockpitHtml ? undefined : "/autoos_interactive.html"}
          srcDoc={cockpitHtml || undefined}
          title="AutoOS Cockpit Completo"
          className="w-full flex-1 border-none"
          style={{ height: 'calc(100vh - 120px)' }}
        />
      </main>

      {/* Footer */}
      <footer className="autoos-surface border-t text-xs text-[var(--text-muted)] py-3.5 px-6 text-center font-mono">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
          <span>AutoOS â€” Sistema Operativo Vehicular</span>
          <span className="text-[var(--accent-primary)] font-bold">
            {theme === 'dark' ? 'Tema: Purple Night (Oscuro)' : 'Tema: Soft Dove (Claro)'}
          </span>
          <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5 font-bold">
            <CheckCircle className="w-3.5 h-3.5" /> FCFS â€¢ Round Robin â€¢ Prioridad â€¢ BaterÃ­a Baja â€¢ Falla Configurable â€¢ GPS DinÃ¡mico
          </span>
        </div>
      </footer>

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
  );
}
