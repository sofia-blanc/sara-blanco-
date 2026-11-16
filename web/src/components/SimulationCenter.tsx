import React, { useEffect, useMemo, useState } from 'react';
import {
  Activity, AlertTriangle, Battery, Camera, CheckCircle, ClipboardList, CloudRain,
  Cpu, Download, Gauge, HardDrive, Navigation, Pause, Play, Radio, RotateCcw,
  Shield, Sliders, Timer, Wrench, Zap, Car, Wifi, ArrowRight,
} from 'lucide-react';
import type { BatteryState, UserRole, VehicleDevice } from '../types/scheduler';
import type { SimulationState } from '../utils/schedulerEngine';
import { SCENARIOS, scenarioById, type ScenarioId, type SimulationAction, type Weather } from '../simulation/scenarios';
import {
  downloadReport, readReports, reportAsText, saveReport,
  type AutoOSReport, type SimulationDecisionRecord, type SimulationSnapshot,
} from '../simulation/report';
import { isSupabaseConfigured } from '../supabaseClient';

interface Props {
  battery: BatteryState;
  devices: VehicleDevice[];
  state: SimulationState;
  userRole: UserRole;
  onStart: (id: ScenarioId) => void;
  onAction: (id: SimulationAction) => void;
  onDriveTick: (speedKmh: number, weather: Weather) => void;
  onBattery: (level: number) => void;
  onFault: (deviceCode: string) => void;
  onCpuStress: () => void;
  onWeather: (value: Weather) => void;
}

const readClock = () => new Date().toLocaleTimeString('es-CO', { hour12: false });
const formatNum = (value: number) => Math.round(value).toLocaleString('es-CO');

export function SimulationCenter({ battery, devices, state, userRole, onStart, onAction, onDriveTick, onBattery, onFault, onCpuStress, onWeather }: Props) {
  const [selected, setSelected] = useState<ScenarioId>('battery');
  const [activeId, setActiveId] = useState<ScenarioId | null>(null);
  const [running, setRunning] = useState(false);
  const [speed, setSpeed] = useState(0);
  const [weather, setWeather] = useState<Weather>('soleado');
  const [elapsed, setElapsed] = useState(0);
  const [distance, setDistance] = useState(0);
  const [offlineMode, setOfflineMode] = useState(false);
  const [decisions, setDecisions] = useState<SimulationDecisionRecord[]>([]);
  const [startedAt, setStartedAt] = useState('');
  const [initial, setInitial] = useState<SimulationSnapshot | null>(null);
  const [report, setReport] = useState<AutoOSReport | null>(null);
  const [history, setHistory] = useState<AutoOSReport[]>(() => readReports());
  const [faultTarget, setFaultTarget] = useState('DEV_CAM_FRONT');
  const [showHistory, setShowHistory] = useState(false);

  const definition = scenarioById(activeId || selected);
  const activeProcesses = state.processes.filter((p) => p.state === 'LISTO' || p.state === 'EJECUTANDO' || p.state === 'BLOQUEADO');
  // Carga solicitada, no utilización física: suma de demandas de procesos en la simulación.
  const cpuLoad = Math.min(100, activeProcesses.reduce((sum, p) => sum + p.cpuUsagePct, 0));
  const usedMemory = activeProcesses.reduce((sum, p) => sum + p.memoryMb, 0);
  const suspended = state.processes.filter((p) => p.state === 'SUSPENDIDO').length;
  const faults = devices.filter((d) => d.status !== 'operativo');
  const wifiFail = devices.some((d) => d.code === 'DEV_COM_V2X' && d.status !== 'operativo');
  const gpsFail = devices.some((d) => d.code === 'DEV_GPS_01' && d.status !== 'operativo');
  const risk = battery.level <= 10 || faults.some((d) => d.criticalLevel === 'critico' && d.status === 'falla') || (cpuLoad >= 95 && speed > 0)
    ? 'CRÍTICO' : battery.level <= 20 || faults.length || (weather !== 'soleado' && speed > 60) || cpuLoad > 85
      ? 'PRECAUCIÓN' : 'NORMAL';

  const takeSnapshot = (): SimulationSnapshot => ({
    battery: battery.level, speed, weather, cpuLoad, usedMemory,
    running: activeProcesses.length, suspended,
    failures: faults.map((d) => `${d.code} (${d.status})`),
    scheduler: state.algorithm, tick: state.currentTime,
  });

  const selectedDefinition = useMemo(() => scenarioById(selected), [selected]);
  const latestEvents = state.events.slice(0, 6);

  useEffect(() => {
    if (!activeId || !running || report) return;
    const timer = window.setInterval(() => {
      setElapsed((t) => t + 1);
      setDistance((km) => km + speed / 3600);
      onDriveTick(speed, weather);
    }, 1000);
    return () => window.clearInterval(timer);
  }, [activeId, running, report, speed, weather, onDriveTick]);

  // La instantánea se obtiene cuando React termina de renderizar el estado de arranque del SO.
  useEffect(() => {
    if (activeId && !initial && !report) setInitial(takeSnapshot());
    // takeSnapshot intentionally reads the latest props for the newly started session.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeId, initial, report]);

  const start = (id: ScenarioId) => {
    const scenario = scenarioById(id);
    onStart(id);
    setSelected(id);
    setActiveId(id);
    setSpeed(scenario.speed);
    setWeather(scenario.weather);
    setElapsed(0);
    setDistance(0);
    setOfflineMode(false);
    setDecisions([]);
    setStartedAt(new Date().toISOString());
    setInitial(null);
    setReport(null);
    setRunning(true);
  };

  const choose = (id: SimulationAction) => {
    if (!activeId || report || (userRole === 'pasajero' && id !== 'ignore')) return;
    const option = definition.options.find((a) => a.id === id);
    if (!option) return;
    onAction(id);
    if (id === 'reduce_speed') setSpeed((v) => Math.min(v, 35));
    if (id === 'offline_navigation' || id === 'local_mode') setOfflineMode(true);
    if (id === 'restart_gps' || id === 'restart_network') setOfflineMode(false);
    setDecisions((old) => [...old, { time: readClock(), choice: option.label, effect: option.explanation }]);
  };

  const addIntervention = (name: string, effect: string) => {
    setDecisions((old) => [...old, { time: readClock(), choice: name, effect }]);
  };

  const finish = () => {
    if (!activeId || !initial) return;
    setRunning(false);
    const end = takeSnapshot();
    const recommendations = [
      ...(end.battery <= 20 ? ['Mantener servicios no esenciales suspendidos y reducir consumo de la simulación.'] : []),
      ...(end.failures.length ? ['Revisar los códigos de diagnóstico y recuperar los dispositivos afectados.'] : []),
      ...(end.cpuLoad >= 90 ? ['Priorizar tareas críticas y reducir procesos de baja prioridad.'] : []),
      ...(end.weather !== 'soleado' && end.speed > 55 ? ['Disminuir la velocidad virtual en condiciones de visibilidad adversa.'] : []),
      ...(decisions.length === 0 ? ['Evaluar al menos una de las acciones sugeridas por AutoOS.'] : []),
    ];
    if (!recommendations.length) recommendations.push('La simulación terminó sin alertas pendientes de los indicadores analizados.');
    const generated: AutoOSReport = {
      id: `${Date.now()}`,
      scenario: activeId,
      title: definition.title,
      startedAt: startedAt || new Date().toISOString(),
      completedAt: new Date().toISOString(),
      diagnosis: definition.cause,
      initial,
      final: end,
      actions: decisions,
      recommendations,
      status: end.battery <= 10 || end.failures.length > 0 || end.cpuLoad > 90 ? 'RIESGOS PENDIENTES' : 'ESTABLE SEGÚN INDICADORES SIMULADOS',
    };
    saveReport(generated);
    setReport(generated);
    setHistory(readReports());
  };

  const dangerClass = risk === 'CRÍTICO' ? 'text-red-400' : risk === 'PRECAUCIÓN' ? 'text-amber-400' : 'text-emerald-400';
  const canEditHardware = userRole !== 'pasajero';

  return (
    <div className="w-full max-w-[1560px] mx-auto p-4 lg:p-7 space-y-5 font-sans">
      <section className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs font-mono uppercase tracking-[.26em] text-[var(--accent-primary)] font-bold">AutoOS · Laboratorio interactivo</p>
          <h2 className="text-2xl lg:text-3xl font-bold tracking-tight">Centro de simulación vehicular</h2>
          <p className="text-sm mt-1 text-[var(--text-muted)]">Experimenta con escenarios, toma decisiones y observa cómo responde el sistema operativo.</p>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className={`rounded-lg border px-3 py-2 flex items-center gap-1.5 ${
            isSupabaseConfigured()
              ? 'border-emerald-500/50 bg-emerald-500/10 text-emerald-400'
              : 'border-amber-500/50 bg-amber-500/10 text-amber-300'
          }`}>
            <span className={`w-2 h-2 rounded-full ${isSupabaseConfigured() ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
            {isSupabaseConfigured() ? 'Supabase: Conectado' : 'Modo Local (Sin credenciales)'}
          </span>
          <span className={`rounded-lg border px-3 py-2 ${activeId ? 'border-emerald-500/50 bg-emerald-500/10' : 'border-[var(--border-color)]'}`}>
            {activeId ? (running ? '● Simulación en marcha' : '◼ Simulación pausada') : '○ Sin sesión activa'}
          </span>
          <button onClick={() => setShowHistory((v) => !v)} className="rounded-lg border border-[var(--border-color)] px-3 py-2 flex gap-2 items-center hover:bg-[var(--bg-card-hover)]"><ClipboardList size={15} /> Historial ({history.length})</button>
        </div>
      </section>

      {showHistory && (
        <section className="autoos-card rounded-2xl p-4 space-y-2">
          <h3 className="font-bold text-sm">Informes guardados en este navegador y Supabase</h3>
          {!history.length && <p className="text-xs text-[var(--text-muted)]">Todavía no hay informes. Finaliza una simulación para guardar el primero.</p>}
          {history.map((item) => <div key={item.id} className="flex items-center justify-between gap-3 border-b border-[var(--border-color)] py-2 text-xs">
            <span className="min-w-0 truncate">{item.title} · {new Date(item.completedAt).toLocaleString('es-CO')} · {item.status}</span>
            <button onClick={() => downloadReport(item)} className="shrink-0 text-[var(--accent-primary)] flex items-center gap-1"><Download size={14} /> Descargar</button>
          </div>)}
          <p className="text-[11px] text-[var(--text-muted)]">
            {isSupabaseConfigured()
              ? '🟢 Sincronización activa con Supabase Cloud (tabla reportes_simulacion y eventos).'
              : '🟡 Almacenamiento local en el navegador; para sincronizar con la nube, configura web/.env con tus credenciales de Supabase.'}
          </p>
        </section>
      )}

      <section className="autoos-card rounded-2xl p-4 space-y-3">
        <div className="flex items-center justify-between gap-2">
          <h3 className="text-sm font-bold flex items-center gap-2"><Sliders size={17} /> Selecciona un escenario</h3>
          <span className="text-[11px] text-[var(--text-muted)] font-mono">7 guiados + laboratorio libre</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {SCENARIOS.map((item) => (
            <button key={item.id} onClick={() => setSelected(item.id)} className={`text-left rounded-xl border p-3 min-h-[93px] transition-all hover:-translate-y-0.5 ${selected === item.id ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/10 ring-1 ring-[var(--accent-primary)]/30' : 'border-[var(--border-color)] bg-[var(--bg-surface)] hover:bg-[var(--bg-card-hover)]'}`}>
              <span className="text-xl" aria-hidden>{item.icon}</span>
              <span className="text-xs font-bold block mt-1">{item.title}</span>
              <span className="text-[10px] text-[var(--text-muted)] block leading-tight mt-1">{item.description}</span>
            </button>
          ))}
        </div>
        <div className="flex flex-wrap gap-2 items-center justify-between border-t border-[var(--border-color)] pt-3">
          <p className="text-xs text-[var(--text-muted)] max-w-[720px]"><b className="text-[var(--text-primary)]">{selectedDefinition.icon} {selectedDefinition.title}:</b> {selectedDefinition.cause}</p>
          <button onClick={() => start(selected)} className="px-5 py-2.5 rounded-xl bg-[var(--accent-primary)] text-white text-sm font-bold flex items-center gap-2 hover:brightness-110"><Play size={16} /> {activeId ? 'Iniciar nuevo escenario' : 'Iniciar simulación'}</button>
        </div>
      </section>

      <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1.7fr)_minmax(320px,1fr)] gap-5">
        <div className="space-y-5 min-w-0">
          <section className="autoos-card rounded-2xl overflow-hidden">
            <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 border-b border-[var(--border-color)]">
              <span className="font-bold text-sm flex gap-2 items-center"><Car size={18} /> Cabina de conducción · Vehículo virtual</span>
              <span className={`text-xs font-mono font-bold ${dangerClass}`}>● {risk}</span>
            </div>
            <div className="relative overflow-hidden bg-[#101e30] text-white" style={{ minHeight: 315 }}>
              <svg className="w-full h-[315px]" viewBox="0 0 900 380" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Carretera virtual con montaña, cielo, calzada y vehículo">
                <defs>
                  <linearGradient id="simSky" x1="0" x2="0" y1="0" y2="1"><stop stopColor={weather === 'soleado' ? '#4179c5' : '#25374f'} /><stop offset="1" stopColor={weather === 'soleado' ? '#a9d5ec' : '#607187'} /></linearGradient>
                  <linearGradient id="simRoad" x1="0" x2="0" y1="0" y2="1"><stop stopColor="#555967" /><stop offset="1" stopColor="#141923" /></linearGradient>
                </defs>
                <rect width="900" height="380" fill="url(#simSky)" />
                <circle cx="730" cy="70" r="32" fill={weather === 'soleado' ? '#f6e8aa' : '#b7c2d2'} opacity="0.85" />
                <path d="M0 210 L115 112 L231 207 L385 108 L545 211 L710 135 L900 205 V380 H0" fill="#365b65" />
                <path d="M0 245 L165 182 L280 233 L475 163 L610 221 L770 182 L900 228 V380 H0" fill="#294b53" />
                <path d="M0 251 Q260 231 450 245 Q670 227 900 253 V380 H0" fill="#365541" />
                <path d="M418 233 L482 233 L885 380 L17 380 Z" fill="url(#simRoad)" />
                <path d="M418 233 L17 380" stroke="#e2dddd" strokeWidth="4" opacity=".65" />
                <path d="M482 233 L885 380" stroke="#e2dddd" strokeWidth="4" opacity=".65" />
                <path d="M450 240 L450 250 M450 275 L450 303 M450 332 L450 380" stroke="#ffd986" strokeWidth="5" strokeDasharray="20 18" className={running ? 'autoos-lane-moving' : ''} opacity=".88" />
                <g transform="translate(450 316)">
                  <ellipse cy="35" rx="81" ry="13" fill="#000" opacity=".5" />
                  <path d="M-62 0 L-44 -27 Q0 -46 44 -27 L62 0 L66 36 Q0 49 -66 36 Z" fill="#c6d5e8" stroke="#64748b" strokeWidth="3" />
                  <path d="M-40 -24 Q0 -35 40 -24 L48 -3 L-48 -3 Z" fill="#19283e" />
                  <rect x="-60" y="15" width="22" height="10" rx="3" fill="#ff5e5e" />
                  <rect x="38" y="15" width="22" height="10" rx="3" fill="#ff5e5e" />
                  <rect x="-44" y="32" width="88" height="6" rx="3" fill="#233145" />
                </g>
                {weather === 'lluvia' && Array.from({ length: 28 }, (_, i) => <line key={i} x1={(i * 101) % 900} y1={(i * 71) % 330} x2={(i * 101) % 900 - 14} y2={(i * 71) % 330 + 23} stroke="#dbeafe" strokeWidth="2" opacity=".45" />)}
                {weather === 'niebla' && <rect width="900" height="380" fill="#e6ebf0" opacity=".38" />}
              </svg>
              <div className="absolute top-4 left-4 bg-[#07101c]/85 rounded-xl px-4 py-2 text-white text-xs font-mono border border-white/15">
                <div className="flex items-center gap-2"><Navigation size={15} className={gpsFail ? 'text-red-400' : 'text-emerald-400'} /> {gpsFail ? 'GPS sin señal' : offlineMode ? 'Navegación offline' : 'Ruta virtual activa'}</div>
                <div className="mt-1 text-white/60">{weather === 'soleado' ? '☀️ Despejado' : weather === 'lluvia' ? '🌧️ Lluvia' : '🌫️ Niebla'} · {wifiFail ? 'Sin enlace V2X' : 'V2X conectado'}</div>
              </div>
              <div className="absolute top-4 right-4 text-right bg-[#07101c]/85 rounded-xl px-4 py-2 border border-white/15">
                <div className="text-3xl font-bold tabular-nums">{speed} <span className="text-xs text-white/60">km/h</span></div>
                <span className="text-xs text-white/60">{distance.toFixed(2)} km recorridos</span>
              </div>
              <div className="absolute bottom-3 left-3 right-3 bg-[#07101c]/85 rounded-xl p-2 flex flex-wrap gap-x-5 gap-y-1 justify-between text-[11px] font-mono border border-white/15">
                <span>⚡ {battery.level.toFixed(1)} % batería</span><span>🧠 CPU demandada {cpuLoad} %</span><span>💾 {formatNum(usedMemory)} MB</span><span>⏱ {elapsed} s</span>
              </div>
            </div>
            <div className="p-4 space-y-3">
              <div className="flex gap-2 flex-wrap items-center">
                <button disabled={!activeId || !!report} onClick={() => setRunning((v) => !v)} className="bg-[var(--accent-primary)] text-white px-4 py-2 rounded-lg text-xs font-bold disabled:opacity-40 flex gap-2 items-center">{running ? <Pause size={14} /> : <Play size={14} />} {running ? 'Pausar' : 'Continuar'}</button>
                <button disabled={!activeId} onClick={() => activeId && start(activeId)} className="border border-[var(--border-color)] px-3 py-2 rounded-lg text-xs flex gap-1 items-center disabled:opacity-40"><RotateCcw size={14} /> Reiniciar</button>
                <span className="text-xs text-[var(--text-muted)]">El tiempo avanza al reproducir y ejecuta ciclos del planificador.</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-[1fr_auto] gap-3 items-center">
                <label className="text-xs font-semibold flex gap-2 items-center"><Gauge size={15} /> Velocidad del vehículo: <b>{speed} km/h</b></label>
                <span className="text-xs text-[var(--text-muted)]">Control de conducción</span>
                <input type="range" min="0" max="120" step="5" disabled={!activeId || !!report} value={speed} onChange={(e) => setSpeed(Number(e.target.value))} className="w-full accent-[var(--accent-primary)] disabled:opacity-30" aria-label="Velocidad de conducción virtual" />
                <div className="flex gap-1">{[0, 35, 80].map((v) => <button key={v} disabled={!activeId || !!report} onClick={() => setSpeed(v)} className="px-2 py-1 rounded border border-[var(--border-color)] text-[11px] disabled:opacity-30">{v} km/h</button>)}</div>
              </div>
            </div>
          </section>

          <section className="autoos-card rounded-2xl p-4 space-y-3">
            <h3 className="font-bold flex items-center gap-2 text-sm"><Activity size={16} /> Telemetría del sistema operativo <span className="text-[10px] text-[var(--text-muted)] font-normal">(datos simulados)</span></h3>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              {[
                { icon: <Battery size={17}/>, label: 'Batería', value: `${battery.level.toFixed(1)} %`, sub: battery.isLowBatteryMode ? 'Ahorro activo' : 'Normal' },
                { icon: <Cpu size={17}/>, label: 'Demanda CPU', value: `${cpuLoad} %`, sub: state.algorithm.replaceAll('_',' ') },
                { icon: <HardDrive size={17}/>, label: 'Memoria', value: `${formatNum(usedMemory)} MB`, sub: `${suspended} procesos suspendidos` },
                { icon: <Radio size={17}/>, label: 'Dispositivos', value: `${devices.length - faults.length}/${devices.length}`, sub: faults.length ? `${faults.length} con anomalía` : 'Todos operativos' },
              ].map((item) => <div key={item.label} className="autoos-surface rounded-xl p-3 min-w-0">
                <div className="text-xs text-[var(--text-muted)] flex items-center gap-1.5">{item.icon} {item.label}</div>
                <div className="font-bold text-xl mt-2 tabular-nums">{item.value}</div>
                <div className="text-[10px] truncate mt-1 text-[var(--text-muted)]">{item.sub}</div>
              </div>)}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="autoos-surface rounded-xl p-3">
                <div className="font-semibold text-xs mb-2">Dispositivos y buses</div>
                <div className="max-h-48 overflow-y-auto space-y-1">{devices.map((d) => <div key={d.code} className="text-[11px] flex items-center justify-between gap-2"><span className="truncate" title={d.name}>{d.name}</span><span className={`font-bold shrink-0 ${d.status === 'operativo' ? 'text-emerald-500' : d.status === 'degradado' ? 'text-amber-500' : 'text-red-500'}`}>{d.status}</span></div>)}</div>
              </div>
              <div className="autoos-surface rounded-xl p-3">
                <div className="font-semibold text-xs mb-2">Bitácora del kernel · últimos eventos</div>
                <div className="max-h-48 overflow-y-auto space-y-2">{latestEvents.map((event) => <div key={event.id} className="text-[11px] flex gap-2"><span className="text-[var(--text-muted)] shrink-0">t={event.time}</span><span className="leading-tight">{event.message}</span></div>)}</div>
              </div>
            </div>
          </section>
        </div>

        <div className="space-y-5 min-w-0">
          <section className="autoos-card rounded-2xl p-4 space-y-3">
            <h3 className="font-bold text-sm flex items-center gap-2"><Shield size={17} /> Diagnóstico automático de AutoOS</h3>
            <div className={`rounded-xl border p-3 ${risk === 'CRÍTICO' ? 'bg-red-500/10 border-red-500/40' : risk === 'PRECAUCIÓN' ? 'bg-amber-500/10 border-amber-500/40' : 'bg-emerald-500/10 border-emerald-500/40'}`}>
              <div className={`font-bold text-sm flex gap-2 items-center ${dangerClass}`}>{risk === 'NORMAL' ? <CheckCircle size={17} /> : <AlertTriangle size={17} />} Estado {risk}</div>
              <p className="text-xs mt-2 leading-relaxed">{activeId ? definition.cause : 'Selecciona e inicia un escenario para que AutoOS analice los recursos del vehículo.'}</p>
              {!!activeId && <ul className="text-xs space-y-1 mt-3 list-disc pl-4">
                {battery.level <= 20 && <li>Batería en umbral bajo: {battery.level.toFixed(1)} %.</li>}
                {faults.length > 0 && <li>{faults.length} dispositivo(s) reportan anomalías.</li>}
                {cpuLoad >= 90 && <li>Demanda alta de CPU: {cpuLoad} %.</li>}
                {weather !== 'soleado' && <li>Clima adverso, visibilidad reducida.</li>}
                {risk === 'NORMAL' && <li>Los indicadores monitoreados permanecen estables.</li>}
              </ul>}
            </div>
            <h4 className="font-semibold text-xs">Opciones que propone el SO</h4>
            {userRole === 'pasajero' && <p className="text-xs text-amber-400">Rol pasajero: las intervenciones de sistema están restringidas (solo observación).</p>}
            <div className="space-y-2">{definition.options.map((option) => (
              <button disabled={!activeId || !!report || (userRole === 'pasajero' && option.id !== 'ignore')} onClick={() => choose(option.id)} key={option.id} className="group w-full text-left rounded-xl p-3 border border-[var(--border-color)] bg-[var(--bg-surface)] hover:border-[var(--accent-primary)] hover:bg-[var(--bg-card-hover)] disabled:opacity-40 transition">
                <span className="font-bold text-xs flex justify-between items-center gap-2">{option.label}<ArrowRight size={15} className="shrink-0" /></span>
                <span className="text-[11px] text-[var(--text-muted)] block mt-1">{option.detail}</span>
              </button>
            ))}</div>
            {decisions.length > 0 && <div className="border-t border-[var(--border-color)] pt-3 space-y-2">
              <h4 className="font-semibold text-xs">Decisiones del usuario y consecuencias</h4>
              {decisions.slice(-4).map((d, i) => <div key={i} className="rounded-lg bg-[var(--bg-surface)] p-2 text-[11px]"><b>{d.time} · {d.choice}</b><p className="text-[var(--text-muted)] mt-1">{d.effect}</p></div>)}
            </div>}
          </section>

          <section className="autoos-card rounded-2xl p-4 space-y-3">
            <h3 className="font-bold text-sm flex items-center gap-2"><Wrench size={17} /> Laboratorio de condiciones</h3>
            <p className="text-xs text-[var(--text-muted)]">En el modo libre puedes combinar fallas. Cada operación modifica dispositivos, procesos o eventos del SO.</p>
            <div className="space-y-2 opacity-100">
              <label className="text-xs block font-semibold">Clima simulado</label>
              <div className="grid grid-cols-3 gap-2">{(['soleado', 'lluvia', 'niebla'] as Weather[]).map((value) => <button key={value} disabled={!activeId || activeId !== 'sandbox' || !!report} onClick={() => { setWeather(value); onWeather(value); addIntervention(`Clima: ${value}`, 'Se actualizan condiciones ambientales y eventos de sensores.'); }} className={`px-2 py-2 text-xs border rounded-lg disabled:opacity-35 ${weather === value ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/10' : 'border-[var(--border-color)]'}`}>{value === 'soleado' ? '☀️ Sol' : value === 'lluvia' ? '🌧️ Lluvia' : '🌫️ Niebla'}</button>)}</div>
              <label className="text-xs block font-semibold pt-2">Batería de prueba: {Math.round(battery.level)} %</label>
              <input disabled={activeId !== 'sandbox' || !!report || !canEditHardware} aria-label="Batería configurable" type="range" min="3" max="100" step="1" value={Math.round(battery.level)} onChange={(e) => onBattery(Number(e.target.value))} className="w-full accent-[var(--accent-primary)] disabled:opacity-35" />
              <label className="text-xs block font-semibold pt-2">Inyectar falla de hardware</label>
              <div className="flex gap-2"><select disabled={activeId !== 'sandbox' || !!report || !canEditHardware} value={faultTarget} onChange={(e) => setFaultTarget(e.target.value)} className="min-w-0 flex-1 rounded-lg bg-[var(--bg-surface)] text-[var(--text-primary)] border border-[var(--border-color)] text-xs p-2 disabled:opacity-35">
                {devices.map((d) => <option key={d.code} value={d.code}>{d.name}</option>)}
              </select><button disabled={activeId !== 'sandbox' || !!report || !canEditHardware} onClick={() => { onFault(faultTarget); addIntervention('Falla inyectada', `Dispositivo ${faultTarget} marcado con error y proceso de diagnóstico insertado en el scheduler.`); }} className="rounded-lg px-3 py-2 bg-red-500/15 border border-red-500/40 text-red-400 text-xs disabled:opacity-35">Provocar falla</button></div>
              <button disabled={activeId !== 'sandbox' || !!report || !canEditHardware} onClick={() => { onCpuStress(); addIntervention('Sobrecarga CPU', 'Se agrega un proceso de fondo con demanda alta de CPU y memoria.'); }} className="w-full text-xs text-left rounded-lg border border-[var(--border-color)] px-3 py-2 flex gap-2 items-center disabled:opacity-35"><Cpu size={14} /> Añadir proceso pesado (sobrecarga)</button>
              {!canEditHardware && <p className="text-[11px] text-amber-400">El rol pasajero es solo lectura para cambios de hardware.</p>}
            </div>
          </section>

          <section className="autoos-card rounded-2xl p-4 space-y-3">
            <h3 className="font-bold text-sm flex items-center gap-2"><ClipboardList size={17} /> Informe técnico de sesión</h3>
            <p className="text-xs text-[var(--text-muted)]">AutoOS compara el estado inicial y final, registra tus intervenciones y genera recomendaciones.</p>
            <button disabled={!activeId || !!report || !initial} onClick={finish} className="w-full rounded-xl bg-[var(--accent-primary)] text-white font-bold text-sm py-3 disabled:opacity-35 flex gap-2 items-center justify-center"><ClipboardList size={16} /> Finalizar y generar informe</button>
            {report && <div className="space-y-3 border-t border-[var(--border-color)] pt-3">
              <div className="font-bold text-xs text-emerald-500 flex gap-2 items-center"><CheckCircle size={16}/> Informe generado y guardado</div>
              <div className="text-xs"><b>{report.title}</b> · {report.status}</div>
              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div className="rounded-lg p-2 bg-[var(--bg-surface)]"><b>Antes</b><p>Batería: {report.initial.battery.toFixed(1)} %</p><p>CPU: {report.initial.cpuLoad} %</p><p>Fallas: {report.initial.failures.length}</p></div>
                <div className="rounded-lg p-2 bg-[var(--bg-surface)]"><b>Después</b><p>Batería: {report.final.battery.toFixed(1)} %</p><p>CPU: {report.final.cpuLoad} %</p><p>Fallas: {report.final.failures.length}</p></div>
              </div>
              <p className="text-[11px]">Acciones registradas: <b>{report.actions.length}</b>. {report.recommendations[0]}</p>
              <button onClick={() => downloadReport(report)} className="w-full rounded-xl border border-[var(--accent-primary)] px-4 py-2 text-xs font-bold flex gap-2 items-center justify-center"><Download size={15}/> Descargar informe .txt</button>
              <details className="text-[11px]"><summary className="cursor-pointer">Ver informe completo</summary><pre className="overflow-auto max-h-64 mt-2 whitespace-pre-wrap bg-[var(--bg-surface)] rounded-lg p-3 text-[11px]">{reportAsText(report)}</pre></details>
            </div>}
          </section>
        </div>
      </div>
      <p className="text-center text-[11px] text-[var(--text-muted)] pb-3">AutoOS Simulation Center · Abstracción educativa. No controla ni interpreta sensores de vehículos físicos.</p>
    </div>
  );
}
