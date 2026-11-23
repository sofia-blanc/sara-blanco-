/**
 * AUTOOS V20 · juego de conducción continua con selección de rutas por carril.
 *
 * Corrige dos puntos visuales de V17:
 * 1) el vehículo deja de ser un PNG suelto y vuelve a dibujarse dentro del SVG,
 * 2) la elección riesgosa se traduce en una consecuencia visible: el vehículo se detiene.
 *
 * La lógica de CPU, RAM, batería, permisos y Caja Negra permanece en React/App.
 */
import React, { useEffect, useRef } from 'react';
import { AlertTriangle, BatteryCharging, CheckCircle2, ChevronRight, Cpu,
  Gauge, HardDrive, MapPin, Pause, Play, RotateCcw, Radio, ShieldAlert,
  ShieldCheck, Signal, Zap } from 'lucide-react';
import type { MissionStageV16Props } from './MissionStageV16';
import { missionViewV17, routePathsV17 } from '../simulation/missionGameV17';
import { routeIndexFromLane } from '../simulation/routeDrivingV20'; // AUTOOS_V20_RUTAS_AL_VOLANTE
import { forkVisibleWhileDrivingV21, minutesToDrivingForkV21 } from '../simulation/routeDrivingV21'; // AUTOOS_V21_MENOS_CRUCES
import { maySimulate } from '../simulation/missionGameV16';
import { lanePosition, hazardCaption, type DrivingGameState, type DrivingLane } from '../simulation/drivingGameV19';

function isRiskChoiceLabel(label?: string) {
  return /sin cambios|sin gps|mantener|ignorar/i.test(label ?? '');
}

function VehicleVector({ stopped, critical, compact, lane }: { stopped: boolean; critical: boolean; compact: boolean; lane: DrivingLane }) {
  const scale = compact ? 0.68 : 0.68;
  const y = compact ? 655 : 645;
  const x = lanePosition(lane, .82);
  return <g className="v19-driver" transform={`translate(${x} ${y}) scale(${scale})`}>
    <ellipse cy="104" rx="170" ry="25" fill="#00091d" opacity=".55"/>
    <path d="M-158 83Q0 108 158 83L142-15Q124-96 85-126Q45-149 0-149Q-48-149-88-126Q-126-96-143-15Z"
      fill="#0a2452" stroke="#95ecff" strokeWidth="6"/>
    <path d="M-117 -74Q-78 -120 0 -120Q79 -120 117 -74L128 -26H-128Z"
      fill="#092442" stroke="#73dfff" strokeWidth="4"/>
    <path d="M-36 -121H38" stroke="#d2fbff" strokeWidth="7" strokeLinecap="round"/>
    <path d="M-151 3H151" stroke="#e6fdff" strokeWidth="6" opacity=".7"/>
    <path d="M-142 45H-88" stroke={stopped || critical ? '#ff4b8c' : '#ff8fb4'} strokeWidth="18" strokeLinecap="round"/>
    <path d="M88 45H142" stroke={stopped || critical ? '#ff4b8c' : '#ff8fb4'} strokeWidth="18" strokeLinecap="round"/>
    <rect x="-98" y="62" width="196" height="10" rx="5" fill="#0f3f6b" opacity=".7"/>
    <rect x="-40" y="68" width="80" height="18" rx="4" fill="#071731"/>
    <path d="M-92 81H92" stroke="#042147" strokeWidth="9" strokeLinecap="round"/>
    <path d="M-82 -87V-27M82 -87V-27" stroke="#75ddff" strokeWidth="4" opacity=".75"/>
    <path d="M-124 -27H124" stroke="#7ee7ff" strokeWidth="4" opacity=".7"/>
    <circle cx="-110" cy="93" r="31" fill="#041328" stroke="#78e2ff" strokeWidth="5" opacity=".8"/>
    <circle cx="110" cy="93" r="31" fill="#041328" stroke="#78e2ff" strokeWidth="5" opacity=".8"/>
    <circle cx="-110" cy="93" r="15" fill="#56cbf0"/>
    <circle cx="110" cy="93" r="15" fill="#56cbf0"/>
    {(stopped || critical) && <>
      <path d="M-186 -28H-214" stroke="#ff5c95" strokeWidth="9" strokeLinecap="round"/>
      <path d="M186 -28H214" stroke="#ff5c95" strokeWidth="9" strokeLinecap="round"/>
    </>}
  </g>;
}

/** Escenario vectorial estático. El carro forma parte del SVG, no es un PNG flotando encima. */
function RoadWorldV17({approaching, moving, weather, count, stopped, critical, game}:{approaching:boolean; moving:boolean; weather:string; count:number; stopped:boolean; critical:boolean; game:DrivingGameState}) {
  const paths = count === 2 ? [455, 985] : [300,720,1145];
  return <svg className="v17-world" viewBox="0 0 1440 810" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <defs>
      <linearGradient id="v18Sky" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#0c3974"/><stop offset=".67" stopColor={weather==='soleado'?'#2f77b2':weather==='lluvia'?'#375a81':'#547089'}/><stop offset="1" stopColor="#8db8d4"/></linearGradient>
      <linearGradient id="v18Road" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#31425d"/><stop offset="1" stopColor="#07142a"/></linearGradient>
      <linearGradient id="v18Hills" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#1b607f"/><stop offset="1" stopColor="#10344a"/></linearGradient>
    </defs>
    <rect width="1440" height="810" fill="url(#v18Sky)"/>
    <circle cx="1160" cy="185" r="72" fill="#f7f8db" opacity=".6"/>
    <path d="M0 390 155 241 315 384 492 208 690 393 878 273 1040 376 1227 213 1440 402V810H0Z" fill="#315b83"/>
    <path d="M0 445 185 328 377 412 610 306 820 445 1088 310 1440 427V810H0Z" fill="url(#v18Hills)"/>
    <path d="M0 498Q370 444 735 481T1440 475V810H0Z" fill="#0f3546"/>
    {/* V20: la carretera principal nunca desaparece; las bifurcaciones llegan desde el horizonte. */}
    <path d="M630 420H800L1440 810H0Z" fill="url(#v18Road)"/>
    <path d="M630 420 0 810M800 420 1440 810" stroke="#8bcce0" strokeWidth="6"/>
    <path className={moving?'v17-world__lane--active':''} d="M686 423L470 810M746 423L970 810" stroke="#d5f3ff" strokeWidth="9" strokeDasharray="28 45" opacity=".8"/>
    {approaching && <g className="v20-horizon-fork" opacity=".96">
      {paths.map((x,i)=><g key={`fork-${x}`}>
        <path d={`M${670+i*(100/(paths.length-1))} 418 Q${720+(x-720)*.18} 383 ${x} 335`}
          fill="none" stroke="#061733" strokeWidth="45" strokeLinecap="round"/>
        <path d={`M${670+i*(100/(paths.length-1))} 418 Q${720+(x-720)*.18} 383 ${x} 335`}
          fill="none" stroke="#93e7ff" strokeWidth="4" strokeDasharray="10 12"/>
        <circle cx={x} cy="320" r="21" fill="#0a2854" stroke="#75eaff" strokeWidth="4"/>
        <text x={x} y="327" textAnchor="middle" fontSize="22" fontWeight="900" fill="white">{i+1}</text>
      </g>)}
    </g>}
    {weather==='lluvia'&&Array.from({length:14},(_,i)=><path key={i} d={`M${i*107} ${110+(i*51)%380}l-13 37`} stroke="#e7f7ff" opacity=".4" strokeWidth="3"/>)}
    {weather==='niebla'&&<rect width="1440" height="810" fill="#e1f1ff" opacity=".21"/>}
    {game.hazards.map(h=> {
      const x=lanePosition(h.lane,h.progress);
      const y=430 + h.progress * 340;
      const k=.38+h.progress*.75;
      return <g key={h.id} transform={`translate(${x} ${y}) scale(${k})`} aria-label={hazardCaption(h.kind)}>
        {h.kind==='obstacle' ? <>
          <path d="M-33 25L-10-43H10L33 25Z" fill="#ff7e29" stroke="#fff5d0" strokeWidth="5"/>
          <path d="M-23 -1H23M-14 -23H14" stroke="#fff" strokeWidth="9"/>
          <rect x="-42" y="24" width="84" height="13" rx="5" fill="#101b33"/>
        </>:h.kind==='energy'? <>
          <rect x="-36" y="-47" width="72" height="84" rx="12" fill="#2d183d" stroke="#ff76ab" strokeWidth="6"/>
          <path d="M7-36L-15 0H1L-9 27 23-12H6Z" fill="#ffdd69"/>
        </>:h.kind==='camera'?<>
          <rect x="-45" y="-25" width="90" height="64" rx="11" fill="#202e5e" stroke="#7aeaff" strokeWidth="6"/>
          <circle cx="0" cy="7" r="21" fill="#09132a" stroke="#76f5ff" strokeWidth="6"/>
          <circle cx="0" cy="7" r="9" fill="#ff6b9b"/>
          <rect x="-18" y="-41" width="36" height="16" rx="5" fill="#40dbea"/>
        </>:<>
          <path d="M0-48L44-24V24L0 48-44 24V-24Z" fill="#152d65" stroke="#ffe09a" strokeWidth="5"/>
          <path d="M-22-18H22V18H-22ZM-33-10H-24M-33 10H-24M24-10H33M24 10H33" fill="none" stroke="#ffe09a" strokeWidth="6"/>
        </>}
      </g>;
    })}
    <VehicleVector stopped={stopped} critical={critical} compact={false} lane={game.lane}/>
  </svg>;
}

interface GameExtrasV19 {
  game: DrivingGameState;
  incidentNotice: string | null;
  onSteer: (direction: -1|1) => void;
  onRecover: () => void;
  junctionIndex: number;
  powerSaveActive: boolean;
}

export function MissionStageV17(p: MissionStageV16Props & GameExtrasV19) {
  const stageRef=useRef<HTMLElement>(null);
  // V20: captura el teclado en la ventana, incluso tras pulsar los controles con ratón.
  // Usa ref para no re-registrar el listener 8 veces por segundo con los frames SVG.
  const controlsRef = useRef(p);
  controlsRef.current = p;
  useEffect(()=>{ if(p.active) stageRef.current?.focus({preventScroll:true}); },[p.active]);
  useEffect(()=>{
    if (!p.active) return;
    const handleKey=(e:KeyboardEvent)=>{
      const current=controlsRef.current;
      if (!current.running || current.finished || !maySimulate(current.role) || current.battery.level<=0 || current.incidentNotice) return;
      if (e.altKey || e.ctrlKey || e.metaKey) return;
      const target=e.target as HTMLElement | null;
      // El slider de velocidad no bloquea el volante; sí los campos de texto.
      if (target && (target.isContentEditable || ['SELECT','TEXTAREA'].includes(target.tagName) || (target.tagName==='INPUT' && (target as HTMLInputElement).type!=='range'))) return;
      if (e.key==='ArrowLeft'||e.key==='ArrowRight') {
        e.preventDefault(); current.onSteer(e.key==='ArrowLeft'?-1:1);
      } else if (e.key==='ArrowUp'||e.key==='ArrowDown') {
        e.preventDefault(); current.onSpeed(Math.max(0,Math.min(120,current.speed+(e.key==='ArrowUp'?5:-5))));
      }
    };
    window.addEventListener('keydown',handleKey);
    return ()=>window.removeEventListener('keydown',handleKey);
  },[p.active]);
  const allowed = maySimulate(p.role);
  const viewInput = {active:p.active,finished:p.finished,checkpointDue:false,running:p.running,batteryPct:p.battery.level};
  const view = missionViewV17(viewInput);
  // La pantalla de selección por clic desaparece: el carril decide sin pausar.
  const paths = routePathsV17(p.scenario);
  const routeIndex = routeIndexFromLane(p.game.lane, paths.length);
  const approaching = Boolean(p.active && !p.finished && p.battery.level>0 && !p.incidentNotice && forkVisibleWhileDrivingV21(p.elapsed,p.junctionIndex,p.running));
  const gps = p.devices.find(d=>d.code==='DEV_GPS_01');
  const v2x = p.devices.find(d=>d.code==='DEV_COM_V2X');
  const latest = p.decisions.at(-1);
  const nextIn = minutesToDrivingForkV21(p.elapsed,p.junctionIndex);
  const riskStop = Boolean(latest && !(p.scenario.id === 'battery' && p.powerSaveActive) && isRiskChoiceLabel(latest.choice) && !p.finished && p.active && !p.running && p.speed === 0);
  return <section ref={stageRef} tabIndex={0} className={`v17-stage v17-stage--${view}`} aria-label="Minijuego de conducción: mueve el vehículo con flechas izquierda y derecha">
    <div className="v17-stage__world" aria-hidden="true"><RoadWorldV17 approaching={approaching} moving={p.running} weather={p.weather} count={paths.length} stopped={riskStop||Boolean(p.incidentNotice)} critical={p.risk==='CRÍTICO'} game={p.game}/></div>
    <header className="v17-stage__heading">
      <div><span className="v17-stage__eyebrow">SIMULACIÓN EN TIEMPO REAL · AUTOOS RTOS</span>
        <h2>MISIÓN <em>{p.scenario.title.toUpperCase()}</em></h2><p>{p.scenario.cause}</p></div>
      <span className={`v17-stage__risk v17-stage__risk--${p.risk==='NORMAL'?'ok':p.risk==='PRECAUCIÓN'?'warn':'critical'}`}>
        {p.risk==='NORMAL'?<ShieldCheck size={18}/>:<ShieldAlert size={18}/>} {p.risk}</span>
    </header>
    <div className="v17-stage__hud" aria-label="Telemetría compartida con el planificador">
      <div><Gauge size={18}/><span>VELOCIDAD</span><strong>{p.speed}<small> km/h</small></strong></div>
      <div><BatteryCharging size={18}/><span>BATERÍA BMS</span><strong>{p.battery.level.toFixed(1)}<small> %</small></strong></div>
      <div><Cpu size={18}/><span>DEMANDA CPU</span><strong>{Math.round(p.resources.cpuDemandPct)}<small> %</small></strong></div>
      <div><HardDrive size={18}/><span>MEMORIA RAM</span><strong>{Math.round(p.resources.ramPhysicalMb)}<small> MB</small></strong></div>
    </div>
    <div className="v17-stage__space">
      {p.active && view!=='finished' && view!=='exhausted' && <aside className="v19-steering" aria-label="Controles del minijuego">
        <p>CONDUCCIÓN ACTIVA · CARRIL {p.game.lane+1}/3</p>
        {p.powerSaveActive && <span className="v21-saving-status">AHORRO EXTREMO ACTIVO · SIGUE PROTEGIENDO LA MISIÓN</span>}
        <div><button type="button" disabled={!p.running||!allowed||p.game.lane===0} onClick={()=>p.onSteer(-1)} aria-label="Mover coche a la izquierda">←</button>
          <span>← → MOVER · ↑ ↓ VELOCIDAD</span>
          <button type="button" disabled={!p.running||!allowed||p.game.lane===2} onClick={()=>p.onSteer(1)} aria-label="Mover coche a la derecha">→</button></div>
        <small>OBJETIVO 20 MIN · {p.elapsed}/20 MIN · Esquivados {p.game.avoided} · Impactos {p.game.collisions}/3</small>
      </aside>}
      {p.incidentNotice && view!=='exhausted' && <div className="v19-incident" role="alert">
        <span><AlertTriangle size={18}/> INTERRUPCIÓN DE SEGURIDAD DEL SO</span>
        <h3>{p.game.collisions>=3?'FIN DE PARTIDA':'VEHÍCULO DETENIDO'}</h3><p>{p.incidentNotice}</p>
        <button type="button" disabled={!allowed||p.battery.level<=0||p.game.collisions>=3} onClick={p.onRecover}><Play size={16}/> REANUDAR CONDUCCIÓN A 30 KM/H</button>
      </div>}
      {view==='ready' && <div className="v17-stage__prompt v17-stage__prompt--ready">
        <span>01 / PREPARAR MISIÓN</span><h3>INICIAR RECORRIDO</h3>
        <p>Se cargará el escenario y comenzarán los ticks de CPU, batería y procesos.</p>
        <button type="button" disabled={!allowed} onClick={p.onStart}><Play size={18}/> INICIAR SIMULACIÓN <ChevronRight size={19}/></button>
        {!allowed&&<p className="v17-stage__access">Solo Mecánico o Administrador pueden iniciar el laboratorio.</p>}
      </div>}
      {(view==='driving'||view==='paused')&&<div className="v17-stage__progress" role="status">
        <span className="v17-stage__progress-icon">{view==='driving'?<Signal size={24}/>:<Pause size={24}/>}</span>
        <div><strong>{view==='driving'?'TRAYECTO EN CURSO':'SIMULACIÓN EN PAUSA'}</strong>
          <span>{view==='driving'?(nextIn===null?'Ruta definida · conduce hasta la meta evitando obstáculos':`Próximo cruce en ${nextIn} min: elige carril con ← →`):'Conducción detenida: usa REANUDAR si no hay una parada de seguridad'}</span></div>
      </div>}
      {/* AUTOOS_V21_CRUCES_LIMITADOS: solo dos cruces, sin botones ni pausas. */}
      {approaching && nextIn!==null && paths.length>0 && <aside className="v20-route-preview" role="status" aria-label="Próximo cruce, rutas según el carril del vehículo">
        <div className="v20-route-preview__header"><strong>CRUCE EN {nextIn} MIN VIRTUAL{nextIn===1?'':'ES'}</strong><span>SELECCIÓN AUTOMÁTICA POR CARRIL</span></div>
        <div className="v20-route-preview__options">
          {paths.map((option,i)=><div key={option.id} className={`v20-route-option ${i===routeIndex?'v20-route-option--active':''}`}>
            <span>{paths.length===2?(i===0?'← IZQUIERDA / CENTRO':'→ DERECHA'):i===0?'← IZQUIERDA':i===1?'↑ CENTRO':'→ DERECHA'}</span>
            <strong>{option.label}</strong>
            {i===routeIndex&&<small>RUTA ACTUAL DEL VEHÍCULO</small>}
          </div>)}
        </div>
        <p>Usa ← → para posicionarte. Al llegar al cruce, el SO ejecutará la ruta indicada sin pausar la conducción.</p>
      </aside>}
      {riskStop && <div className="v18-stage__consequence" role="status">
        <span>RIESGO SOSTENIDO</span>
        <h3>AUTOOS DETUVO EL VEHÍCULO</h3>
        <p>Ignorar el riesgo activó una parada preventiva. Reinicia la misión o genera el informe de fallas; no puedes continuar por esa ruta.</p>
      </div>}
      {(view==='exhausted'||view==='finished')&&<div className="v17-stage__prompt v17-stage__prompt--end" role="status">
        <span>{view==='exhausted'?'BMS / 0 %':'MISIÓN COMPLETADA'}</span>
        <h3>{view==='exhausted'?'VEHÍCULO DETENIDO':'FIN DEL RECORRIDO'}</h3>
        <p>{view==='exhausted'?'No queda energía virtual para continuar. Reinicia el escenario para una nueva prueba.':'Consulta el informe y los eventos registrados en Caja Negra.'}</p>
        <button type="button" disabled={!allowed} onClick={p.onRestart}><RotateCcw size={16}/> REINICIAR MISIÓN</button>
      </div>}
    </div>
    <div className="v17-stage__footinfo">
      <span><MapPin size={16}/> {p.distance.toFixed(1)} km / {p.elapsed} min virtuales</span>
      <span><Radio size={15}/> GPS {gps?.status==='operativo'?'NORMAL':gps?.status==='degradado'?'ALERTA':'FALLA'}</span>
      <span><Zap size={15}/> V2X {p.offline?'LOCAL':v2x?.status==='operativo'?'NORMAL':'ALERTA'}</span>
      {latest&&<span className="v17-stage__last"><CheckCircle2 size={15}/> {latest.choice}</span>}
    </div>
    <footer className="v17-stage__controls">
      <div><button type="button" disabled={!p.active||p.finished||!allowed||view==='exhausted'||Boolean(p.incidentNotice)||riskStop} onClick={p.onTogglePause}>
        {p.running?<Pause size={16}/>:<Play size={16}/>} {p.running?'PAUSAR':'REANUDAR'}</button>
        <button type="button" disabled={!p.active||!allowed} onClick={p.onRestart}><RotateCcw size={16}/> REINICIAR</button></div>
      <label>VELOCIDAD VIRTUAL <input type="range" min={0} max={120} step={5} value={p.speed}
        onChange={e=>p.onSpeed(Number(e.target.value))} disabled={!p.active||p.finished||!allowed}/><b>{p.speed} km/h</b></label>
      <small><AlertTriangle size={14}/> Modelo didáctico: 1 s = 1 min virtual</small>
    </footer>
  </section>;
}
