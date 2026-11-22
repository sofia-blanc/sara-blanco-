import React, { useEffect, useMemo, useState } from 'react';
import {
  Activity, AlertTriangle, Battery, Camera, CheckCircle, ClipboardList, CloudRain,
  Cpu, Download, Gauge, HardDrive, Navigation, Pause, Play, Radio, RotateCcw,
  Shield, Sliders, Timer, Wrench, Zap, Car, Wifi, ArrowRight,
} from 'lucide-react';
import type { BatteryState, UserRole, VehicleDevice } from '../types/scheduler';
import type { SimulationState } from '../utils/schedulerEngine';
import type { OSResourceSnapshot, OSResourceSample } from '../simulation/resources';
import { OSResourceMonitor } from './OSResourceMonitor';
import { SCENARIOS, scenarioById, type ScenarioId, type SimulationAction, type Weather } from '../simulation/scenarios';
import {
  downloadReport, readReports, reportAsText, saveReport,
  type AutoOSReport, type SimulationDecisionRecord, type SimulationSnapshot,
} from '../simulation/report';
import { isSupabaseConfigured } from '../supabaseClient';
import { MissionStageV17 } from './MissionStageV17'; // AUTOOS_V17_BIFURCACIONES
import { maySimulate, decisionCheckpoint, canRunMission } from '../simulation/missionGameV16';

interface Props {
  battery: BatteryState;
  devices: VehicleDevice[];
  state: SimulationState;
  resources: OSResourceSnapshot;
  resourceHistory: OSResourceSample[];
  onOpenScheduler: () => void;
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

export function SimulationCenter({ battery, devices, state, resources, resourceHistory, onOpenScheduler, userRole, onStart, onAction, onDriveTick, onBattery, onFault, onCpuStress, onWeather }: Props) {
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
  const [decisionHint, setDecisionHint] = useState('');

  const definition = scenarioById(activeId || selected);
  const activeProcesses = state.processes.filter((p) => p.state === 'LISTO' || p.state === 'EJECUTANDO' || p.state === 'BLOQUEADO');
  // Carga solicitada, no utilización física: suma de demandas de procesos en la simulación.
  // V9: demanda y memoria vienen del mismo modelo que usan CPU y Conducción.
  // La demanda no se limita a 100%: así se hace visible la sobresaturación.
  const cpuLoad = resources.cpuDemandPct;
  const usedMemory = resources.ramPhysicalMb;
  const suspended = state.processes.filter((p) => p.state === 'SUSPENDIDO').length;
  const faults = devices.filter((d) => d.status !== 'operativo');
  const wifiFail = devices.some((d) => d.code === 'DEV_COM_V2X' && d.status !== 'operativo');
  const gpsFail = devices.some((d) => d.code === 'DEV_GPS_01' && d.status !== 'operativo');
  const risk = battery.level <= 10 || faults.some((d) => d.criticalLevel === 'critico' && d.status === 'falla') || (cpuLoad >= 95 && speed > 0)
    ? 'CRÍTICO' : battery.level <= 20 || faults.length || (weather !== 'soleado' && speed > 60) || cpuLoad > 85
      ? 'PRECAUCIÓN' : 'NORMAL';

  const takeSnapshot = (): SimulationSnapshot => ({
    battery: battery.level, speed, weather, cpuLoad, usedMemory,
    energyWh: resources.consumedWh,
    powerW: resources.totalPowerW,
    swapMb: resources.swapRequestedMb,
    cpuBusyPct: resources.cpuBusyPct,
    running: activeProcesses.length, suspended,
    failures: faults.map((d) => `${d.code} (${d.status})`),
    scheduler: state.algorithm, tick: state.currentTime,
  });

  const selectedDefinition = useMemo(() => scenarioById(selected), [selected]);
  const latestEvents = state.events.slice(0, 6);
  const checkpointDue = Boolean(activeId && !report && decisionCheckpoint(elapsed, decisions.length));
  const allowed = maySimulate(userRole);

  useEffect(() => {
    if (!activeId || !running || report || !canRunMission(true, false, battery.level)) return;
    const timer = window.setInterval(() => {
      setElapsed((t) => t + 1);
      // 1 s de demostración = 1 minuto de ruta virtual acelerada.
      setDistance((km) => km + speed / 60);
      onDriveTick(speed, weather);
    }, 1000);
    return () => window.clearInterval(timer);
  }, [activeId, running, report, speed, weather, onDriveTick, battery.level]);

  // V16: cada 5 ticks de viaje se congela la escena hasta elegir una respuesta.
  useEffect(() => { if (checkpointDue && running) setRunning(false); }, [checkpointDue, running]);
  useEffect(() => { if (activeId && battery.level <= 0 && running) { setRunning(false); setSpeed(0); } }, [activeId, battery.level, running]);

  // La instantánea se obtiene cuando React termina de renderizar el estado de arranque del SO.
  useEffect(() => {
    if (activeId && !initial && !report) setInitial(takeSnapshot());
    // takeSnapshot intentionally reads the latest props for the newly started session.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeId, initial, report]);

  const start = (id: ScenarioId) => {
    if (!maySimulate(userRole)) { setDecisionHint('El perfil actual no puede iniciar el laboratorio.'); return; }
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
    setDecisionHint('Misión iniciada. Gestiona los recursos y espera el próximo punto de decisión.');
  };

  const choose = (id: SimulationAction) => {
    // V17: no se pueden ejecutar decisiones por fuera de la bifurcacion.
    if (!activeId || report || !maySimulate(userRole) || !checkpointDue) return;
    const option = definition.options.find((a) => a.id === id);
    if (!option) return;
    onAction(id);
    let effect = option.explanation;
    let autoResume = true; // AUTOOS_V18_CONSECUENCIAS
    if (id === 'reduce_speed') setSpeed((v) => Math.min(v, 35));
    if (id === 'offline_navigation' || id === 'local_mode') setOfflineMode(true);
    if (id === 'restart_gps' || id === 'restart_network') setOfflineMode(false);
    if (id === 'ignore') {
      setSpeed(0);
      setRunning(false);
      onBattery(Math.max(0, battery.level - 6));
      effect = `${option.explanation} AutoOS detuvo el vehículo para evitar que el riesgo siguiera aumentando.`;
      setDecisionHint(`Decisión ejecutada: ${option.label}. El vehículo quedó detenido por riesgo sostenido.`);
      autoResume = false;
    } else {
      setDecisionHint(`Decisión ejecutada: ${option.label}. ${option.explanation}`);
    }
    setDecisions((old) => [...old, { time: readClock(), choice: option.label, effect }]);
    if (autoResume && canRunMission(true, false, battery.level)) setRunning(true);
  };

  const addIntervention = (name: string, effect: string) => {
    setDecisions((old) => [...old, { time: readClock(), choice: name, effect }]);
  };

  const finish = () => {
    if (!activeId || !initial || !maySimulate(userRole)) return;
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
  // V16: el laboratorio modifica el kernel simulado; solo técnicos autorizados.
  const canEditHardware = allowed;

  return (
    <div className="v16-center w-full space-y-5 font-sans" data-v16="escena-jugable">
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
            {isSupabaseConfigured() ? 'Cliente React configurado' : 'Persistencia: verificar en Nube'}
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
              ? 'Cliente configurado. La persistencia real se verifica en Nube / Supabase y Caja Negra.'
              : '🟡 Almacenamiento local en el navegador; para sincronizar con la nube, configura web/.env con tus credenciales de Supabase.'}
          </p>
        </section>
      )}

      <section className="autoos-card rounded-2xl p-4 space-y-3 v16-scenario-tray">
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
          {activeId && selected !== activeId ? <button type="button" onClick={() => start(selected)} disabled={!allowed} className="px-5 py-2.5 rounded-xl bg-[var(--accent-primary)] text-white text-sm font-bold disabled:opacity-40">CARGAR ESCENARIO SELECCIONADO</button> : <span className="text-xs font-semibold text-[var(--text-muted)]">Pulsa INICIAR desde la escena; para cambiar de misión elige otra tarjeta y cárgala aquí.</span>}
        </div>
      </section>

      {/* AUTOOS_V16_ESCENA_JUGABLE: escena de ancho completo y decisiones del mismo motor React. */}
      <MissionStageV17 scenario={definition} active={!!activeId} running={running} finished={!!report}
        checkpointDue={checkpointDue} battery={battery} devices={devices} resources={resources} weather={weather}
        speed={speed} elapsed={elapsed} distance={distance} offline={offlineMode} risk={risk}
        decisions={decisions} role={userRole} onStart={()=>start(selected)}
        onTogglePause={()=>setRunning(v=> !v && canRunMission(!!activeId,!!report,battery.level) && !checkpointDue)}
        onRestart={()=>{if(activeId)start(activeId);}} onSelect={choose}
        onSpeed={v=>setSpeed(v)} />
      <div className="v16-stage-feedback" role="status">{decisionHint || 'La Caja Negra registra las decisiones a través de los eventos del planificador.'}</div>
      {/* Monitor completo conservado como panel técnico desplegable; el HUD de la escena usa los mismos datos. */}
      <details className="v16-aux-monitor autoos-card rounded-xl p-3">
        <summary className="cursor-pointer font-bold text-sm">Ver monitor avanzado de recursos del SO</summary>
        <OSResourceMonitor snapshot={resources} history={resourceHistory} onOpenScheduler={allowed ? onOpenScheduler : undefined} />
      </details>

      <div className="v16-secondary-grid">
        <div className="space-y-5 min-w-0">
          <section className="autoos-card rounded-2xl p-4 space-y-3">
            <h3 className="font-bold text-sm">DISPOSITIVOS Y BITÁCORA DEL SISTEMA</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="autoos-surface rounded-xl p-3">
                <div className="font-semibold text-xs mb-2">Hardware / buses</div>
                <div className="max-h-48 overflow-y-auto space-y-1">{devices.map((d) => <div key={d.code} className="text-[11px] flex justify-between gap-2"><span className="truncate" title={d.name}>{d.name}</span><span className={d.status === 'operativo' ? 'text-emerald-500' : 'text-red-500'}>{d.status}</span></div>)}</div>
              </div>
              <div className="autoos-surface rounded-xl p-3">
                <div className="font-semibold text-xs mb-2">Últimos eventos del planificador</div>
                <div className="max-h-48 overflow-y-auto space-y-2">{latestEvents.map((e) => <div key={e.id} className="text-[11px] flex gap-2"><span className="text-[var(--text-muted)]">t={e.time}</span><span>{e.message}</span></div>)}</div>
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
                {cpuLoad >= 90 && <li>Demanda alta de CPU: {cpuLoad} % (por encima de la capacidad cuando supera 100%).</li>}
                {resources.swapRequestedMb > 0 && <li>Presión de memoria: {resources.swapRequestedMb} MB requieren SWAP estimada.</li>}
                {resources.totalPowerW > 0 && <li>Potencia estimada: {(resources.totalPowerW / 1000).toFixed(2)} kW.</li>}
                {weather !== 'soleado' && <li>Clima adverso, visibilidad reducida.</li>}
                {risk === 'NORMAL' && <li>Los indicadores monitoreados permanecen estables.</li>}
              </ul>}
            </div>
            <p className="text-xs text-[var(--text-muted)]">Las opciones jugables están dentro de la escena principal. Aquí se conserva el diagnóstico y el historial técnico.</p>
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
                <div className="rounded-lg p-2 bg-[var(--bg-surface)]"><b>Antes</b><p>Batería: {report.initial.battery.toFixed(2)} %</p><p>CPU solicitada: {report.initial.cpuLoad} %</p><p>RAM: {report.initial.usedMemory} MB</p><p>SWAP: {report.initial.swapMb || 0} MB</p><p>Fallas: {report.initial.failures.length}</p></div>
                <div className="rounded-lg p-2 bg-[var(--bg-surface)]"><b>Después</b><p>Batería: {report.final.battery.toFixed(2)} %</p><p>CPU solicitada: {report.final.cpuLoad} %</p><p>RAM: {report.final.usedMemory} MB</p><p>SWAP: {report.final.swapMb || 0} MB</p><p>Consumo: {Math.round(report.final.energyWh || 0)} Wh</p><p>Fallas: {report.final.failures.length}</p></div>
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

// AUTOOS_V15_APLICADO — Administrador tiene acceso técnico; backend independiente.
