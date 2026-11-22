/**
 * AUTOOS V16 — Escena jugable de la misión.
 *
 * El componente es PRESENTACIONAL: no fabrica CPU, RAM ni batería.
 * Esas métricas vienen del estado React compartido con el planificador.
 * Las acciones se envían a SimulationCenter, que llama a App.tsx,
 * aplica efectos mediante applyScenarioAction y registra eventos.
 *
 * Representación didáctica: no se controla un automóvil físico.
 */
import React from 'react';
import { AlertTriangle, ArrowRight, Battery, ChevronRight, CloudOff, Cpu, Gauge,
  HardDrive, MapPin, Pause, Play, RotateCcw, ShieldAlert, ShieldCheck,
  Signal, Sparkles, Zap } from 'lucide-react';
import type { BatteryState, UserRole, VehicleDevice } from '../types/scheduler';
import type { OSResourceSnapshot } from '../simulation/resources';
import type { ScenarioDefinition, SimulationAction, Weather } from '../simulation/scenarios';
import type { SimulationDecisionRecord } from '../simulation/report';
import { maySimulate } from '../simulation/missionGameV16';

export interface MissionStageV16Props {
  scenario: ScenarioDefinition;
  active: boolean;
  running: boolean;
  finished: boolean;
  checkpointDue: boolean;
  battery: BatteryState;
  devices: VehicleDevice[];
  resources: OSResourceSnapshot;
  weather: Weather;
  speed: number;
  elapsed: number;
  distance: number;
  offline: boolean;
  risk: string;
  decisions: SimulationDecisionRecord[];
  role: UserRole;
  onStart: () => void;
  onTogglePause: () => void;
  onRestart: () => void;
  onSelect: (id: SimulationAction) => void;
  onSpeed: (speed: number) => void;
}

const flag = (status?: string) => status === 'operativo' ? 'ok' : status === 'degradado' ? 'warn' : 'danger';
const shortStatus = (status?: string) => status === 'operativo' ? 'NORMAL' : status === 'degradado' ? 'ALERTA' : 'FALLA';

/** Arte vectorial original con movimiento opcional solo de marcas de carretera (transform). */
function RoadStage({ weather, running, critical }: { weather: Weather; running: boolean; critical: boolean }) {
  return <svg className="v16-road" viewBox="0 0 1440 740" preserveAspectRatio="xMidYMid slice"
    aria-label="Carretera virtual, vehículo visto desde atrás y señales de navegación" role="img">
    <defs>
      <linearGradient id="v16-sky" x2="0" y2="1"><stop stopColor={weather === 'soleado' ? '#1262b6' : '#19335e'}/><stop offset="1" stopColor={weather === 'niebla' ? '#688ba1' : '#69a7c8'}/></linearGradient>
      <linearGradient id="v16-asphalt" x2="0" y2="1"><stop stopColor="#263b5c"/><stop offset="1" stopColor="#0a1930"/></linearGradient>
      <linearGradient id="v16-auto" x2="0" y2="1"><stop stopColor="#ecffff"/><stop offset=".52" stopColor="#57c9eb"/><stop offset="1" stopColor="#155caa"/></linearGradient>
    </defs>
    <rect width="1440" height="740" fill="url(#v16-sky)"/>
    <circle cx="1080" cy="145" r="73" fill="#fff5d5" opacity=".86"/>
    <path d="M0 370 100 275 240 368 420 210 645 385 795 280 980 367 1130 235 1440 381V740H0Z" fill="#315d78"/>
    <path d="M0 424 245 343 428 402 680 298 830 394 1050 328 1440 440V740H0Z" fill="#1c4763"/>
    <path d="M0 470Q350 420 720 442T1440 462V740H0Z" fill="#164c65"/>
    <path d="M625 402H803L1440 740H0Z" fill="url(#v16-asphalt)"/>
    <path d="M626 402 0 740M803 402 1440 740" stroke="#adf0ff" strokeWidth="7" opacity=".8"/>
    <path d="M718 407 718 445M718 482 718 527M718 574 718 632M718 675 718 750"
      className={running ? 'v16-lane--moving' : undefined} stroke="#ffefaa" strokeWidth="10" strokeDasharray="22 22" strokeLinecap="square"/>
    <g opacity=".7"><path d="M161 413 161 366M122 386H200" stroke="#90f5ff" strokeWidth="6"/>
      <path d="M1240 423V355M1195 375H1285" stroke="#90f5ff" strokeWidth="6"/>
      <circle cx="1240" cy="375" r="26" stroke="#90f5ff" fill="none" strokeWidth="4"/></g>
    {/* Vehículo destacado: dibujo original, estático y centrado. */}
    <g transform="translate(717 600)">
      <ellipse cy="102" rx="174" ry="27" fill="#000b1f" opacity=".68"/>
      <path d="M-145 -20 Q-124 -95 -92 -121Q-40 -146 40 -146Q102 -139 126 -86L148 -20 161 84Q0 108-161 84Z"
        fill="url(#v16-auto)" stroke="#adf2ff" strokeWidth="6"/>
      <path d="M-101 -77Q-40 -121 38 -119Q85 -119 109 -79L126 -21-126-21Z" fill="#092344" stroke="#7de6ff" strokeWidth="5"/>
      <path d="M-138 8H138" stroke="#e6ffff" strokeWidth="6" opacity=".7"/>
      <rect x="-145" y="32" width="56" height="20" rx="5" fill="#ff4d85"/>
      <rect x="89" y="32" width="56" height="20" rx="5" fill="#ff4d85"/>
      <path d="M-108 70H109" stroke="#06254a" strokeWidth="10" strokeLinecap="round"/>
      <rect x="-34" y="62" width="68" height="16" rx="4" fill="#071a38"/>
      <path d="M-77-142Q0-157 74-142" fill="none" stroke="#aff7ff" strokeWidth="7"/>
      {critical && <path d="M-166-36H-189M166-36H189" stroke="#ff4d85" strokeWidth="10"/>}
    </g>
    {weather === 'lluvia' && Array.from({length:19},(_,i)=><path key={i} d={`M${(i*137)%1440} ${(i*83)%740}l-17 30`} stroke="#e0f7ff" strokeWidth="3" opacity=".38"/>)}
    {weather === 'niebla' && <rect width="1440" height="740" fill="#e4f3ff" opacity=".22"/>}
  </svg>;
}

export function MissionStageV16(p: MissionStageV16Props) {
  const permitted = maySimulate(p.role);
  const gps = p.devices.find(d => d.code === 'DEV_GPS_01');
  const v2x = p.devices.find(d => d.code === 'DEV_COM_V2X');
  const recent = p.decisions.at(-1);
  const needsAction = p.active && !p.finished && p.checkpointDue;
  const canRespond = p.active && !p.finished && permitted;
  return <section className="v16-mission" aria-label="Escena interactiva de simulación vehicular">
    <div className="v16-mission__background" aria-hidden="true"><RoadStage weather={p.weather} running={p.running} critical={p.risk === 'CRÍTICO'}/></div>
    <header className="v16-mission__top">
      <div className="v16-mission__title"><span>SIMULACIÓN · AUTOOS / RTOS</span><h2>MISIÓN <em>{p.scenario.title.toUpperCase()}</em></h2>
        <p>{p.scenario.cause}</p></div>
      <span className={`v16-mission__risk v16-mission__risk--${p.risk === 'NORMAL' ? 'ok' : p.risk === 'PRECAUCIÓN' ? 'warn' : 'danger'}`}>
        {p.risk === 'NORMAL' ? <ShieldCheck size={17}/> : <ShieldAlert size={17}/>} {p.risk}</span>
    </header>
    <div className="v16-mission__hud" aria-label="Telemetría de la sesión React">
      <div><Gauge size={19}/><span>VELOCIDAD</span><b>{p.speed}<small> km/h</small></b></div>
      <div><Battery size={19}/><span>BATERÍA BMS</span><b>{p.battery.level.toFixed(1)}<small> %</small></b></div>
      <div><Cpu size={19}/><span>CPU SOLICITADA</span><b>{Math.round(p.resources.cpuDemandPct)}<small> %</small></b></div>
      <div><HardDrive size={19}/><span>RAM ESTIMADA</span><b>{Math.round(p.resources.ramPhysicalMb)}<small> MB</small></b></div>
    </div>
    <div className="v16-mission__middle">
      <div className="v16-mission__route"><div className="v16-mission__route-label"><MapPin size={17}/> TRAYECTO VIRTUAL · {p.distance.toFixed(1)} km
        <span>{p.elapsed} min</span></div>
        <div className="v16-mission__sensorline"><span className={`v16-signal--${flag(gps?.status)}`}><Signal size={15}/> GPS {shortStatus(gps?.status)}</span>
          <span className={`v16-signal--${flag(v2x?.status)}`}>{p.offline ? <CloudOff size={15}/> : <Zap size={15}/>} {p.offline ? 'MODO LOCAL' : `V2X ${shortStatus(v2x?.status)}`}</span></div>
      </div>
      <aside className="v16-mission__dialog" aria-label="Decisiones dentro de la simulación">
        <div className="v16-mission__dialog-head"><span><Sparkles size={16}/> CENTRO DE DECISIONES</span><b>{needsAction ? 'DECISIÓN REQUERIDA' : p.running ? 'EN RUTA' : 'EN ESPERA'}</b></div>
        <h3>{!p.active ? '¿INICIAMOS LA MISIÓN?' : p.finished ? 'MISIÓN FINALIZADA' : needsAction ? 'EL SO NECESITA TU RESPUESTA' : 'TÚ DECIDES EL SIGUIENTE PASO'}</h3>
        <p>{!p.active ? 'Selecciona un escenario y pulsa iniciar. Durante el trayecto tendrás que gestionar riesgos y recursos del SO.' :
          p.finished ? 'Consulta el informe técnico de la sesión y los registros de Caja Negra.' :
          needsAction ? 'El vehículo se ha detenido en un punto de decisión. Elige una respuesta para aplicar sus efectos y continuar.' :
          p.scenario.description}</p>
        {!p.active ? <button type="button" className="v16-mission__primary" onClick={p.onStart} disabled={!permitted}>
          <Play size={18}/> INICIAR ESCENARIO <ArrowRight size={17}/></button> :
          <div className="v16-mission__actions">
            {p.scenario.options.slice(0,4).map((option,i)=><button type="button" key={option.id}
              onClick={()=>p.onSelect(option.id)} disabled={!canRespond} className="v16-mission__choice">
              <span>0{i+1}</span><span><strong>{option.label}</strong><small>{option.detail}</small></span><ChevronRight size={18}/>
            </button>)}
          </div>}
        {recent && <div className="v16-mission__outcome" role="status"><b>ÚLTIMA DECISIÓN · {recent.choice}</b><span>{recent.effect}</span></div>}
        {!permitted && <p className="v16-mission__denied" role="status">Este perfil no puede dirigir simulaciones. Cambia a Mecánico o Administrador desde el menú principal.</p>}
      </aside>
    </div>
    <footer className="v16-mission__bottom">
      <div className="v16-mission__controls">
        <button onClick={p.onTogglePause} disabled={!p.active||p.finished||!permitted||needsAction}>
          {p.running ? <Pause size={16}/> : <Play size={16}/>} {p.running ? 'PAUSAR' : 'REANUDAR'}</button>
        <button onClick={p.onRestart} disabled={!p.active||!permitted}><RotateCcw size={16}/> REINICIAR</button>
      </div>
      <label className="v16-mission__speed">VELOCIDAD VIRTUAL
        <input type="range" min={0} max={120} step={5} value={p.speed}
          onChange={e=>p.onSpeed(Number(e.target.value))} disabled={!p.active||p.finished||!permitted||needsAction}/>
        <b>{p.speed} km/h</b></label>
      <span className="v16-mission__caption"><AlertTriangle size={15}/> 1 s = 1 min virtual · Escenario didáctico, no automóvil real</span>
    </footer>
  </section>;
}
