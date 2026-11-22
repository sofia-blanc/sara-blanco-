/**
 * AUTOOS V18 · escena jugable refinada.
 *
 * Corrige dos puntos visuales de V17:
 * 1) el vehículo deja de ser un PNG suelto y vuelve a dibujarse dentro del SVG,
 * 2) la elección riesgosa se traduce en una consecuencia visible: el vehículo se detiene.
 *
 * La lógica de CPU, RAM, batería, permisos y Caja Negra permanece en React/App.
 */
import React from 'react';
import { AlertTriangle, BatteryCharging, CheckCircle2, ChevronRight, Cpu,
  Gauge, HardDrive, MapPin, Pause, Play, RotateCcw, Radio, ShieldAlert,
  ShieldCheck, Signal, Zap } from 'lucide-react';
import type { MissionStageV16Props } from './MissionStageV16';
import { canChoosePathV17, minutesUntilForkV17, missionViewV17, routePathsV17 } from '../simulation/missionGameV17';
import { maySimulate } from '../simulation/missionGameV16';

function isRiskChoiceLabel(label?: string) {
  return /sin cambios|sin gps|mantener|ignorar/i.test(label ?? '');
}

function VehicleVector({ stopped, critical, compact }: { stopped: boolean; critical: boolean; compact: boolean }) {
  const scale = compact ? 0.78 : 1;
  const y = compact ? 640 : 645;
  return <g transform={`translate(720 ${y}) scale(${scale})`}>
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
function RoadWorldV17({fork, moving, weather, count, stopped, critical}:{fork:boolean; moving:boolean; weather:string; count:number; stopped:boolean; critical:boolean}) {
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
    {fork ? <>
      {paths.map((x)=><path key={`road-${x}`} d={`M720 820 Q${720+(x-720)*.13} 615 ${x} 375`}
        stroke="#08172f" strokeWidth="148" fill="none"/>) }
      {paths.map((x,i)=><g key={x}>
        <path d={`M720 810 Q${720+(x-720)*.13} 615 ${x} 375`} fill="none" stroke="#9fe7fb" strokeWidth="5" opacity=".9" strokeDasharray="17 22"/>
        <circle cx={x} cy="360" r="22" fill="#071b46" stroke={i===1?'#ff5da6':'#66e9ff'} strokeWidth="6"/>
      </g>)}
    </> : <>
      <path d="M630 420H800L1440 810H0Z" fill="url(#v18Road)"/>
      <path d="M630 420 0 810M800 420 1440 810" stroke="#8bcce0" strokeWidth="6"/>
      <path className={moving?'v17-world__lane--active':''} d="M718 433V900" stroke="#d5f3ff" strokeWidth="9" strokeDasharray="28 45" opacity=".8"/>
    </>}
    {weather==='lluvia'&&Array.from({length:14},(_,i)=><path key={i} d={`M${i*107} ${110+(i*51)%380}l-13 37`} stroke="#e7f7ff" opacity=".4" strokeWidth="3"/>)}
    {weather==='niebla'&&<rect width="1440" height="810" fill="#e1f1ff" opacity=".21"/>}
    <VehicleVector stopped={stopped} critical={critical} compact={fork}/>
  </svg>;
}

export function MissionStageV17(p: MissionStageV16Props) {
  const allowed = maySimulate(p.role);
  const viewInput = {active:p.active,finished:p.finished,checkpointDue:p.checkpointDue,running:p.running,batteryPct:p.battery.level};
  const view = missionViewV17(viewInput);
  const fork = view === 'fork';
  const paths = routePathsV17(p.scenario);
  const gps = p.devices.find(d=>d.code==='DEV_GPS_01');
  const v2x = p.devices.find(d=>d.code==='DEV_COM_V2X');
  const latest = p.decisions.at(-1);
  const nextIn = minutesUntilForkV17(p.elapsed,p.decisions.length);
  const riskStop = Boolean(latest && isRiskChoiceLabel(latest.choice) && !fork && !p.finished && p.active && !p.running && p.speed === 0);
  return <section className={`v17-stage v17-stage--${view}`} aria-label="Simulación jugable con decisiones de ruta">
    <div className="v17-stage__world" aria-hidden="true"><RoadWorldV17 fork={fork} moving={p.running} weather={p.weather} count={paths.length} stopped={riskStop} critical={p.risk==='CRÍTICO'}/></div>
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
      {view==='ready' && <div className="v17-stage__prompt v17-stage__prompt--ready">
        <span>01 / PREPARAR MISIÓN</span><h3>INICIAR RECORRIDO</h3>
        <p>Se cargará el escenario y comenzarán los ticks de CPU, batería y procesos.</p>
        <button type="button" disabled={!allowed} onClick={p.onStart}><Play size={18}/> INICIAR SIMULACIÓN <ChevronRight size={19}/></button>
        {!allowed&&<p className="v17-stage__access">Solo Mecánico o Administrador pueden iniciar el laboratorio.</p>}
      </div>}
      {(view==='driving'||view==='paused')&&<div className="v17-stage__progress" role="status">
        <span className="v17-stage__progress-icon">{view==='driving'?<Signal size={24}/>:<Pause size={24}/>}</span>
        <div><strong>{view==='driving'?'TRAYECTO EN CURSO':'SIMULACIÓN EN PAUSA'}</strong>
          <span>{view==='driving'?`Próxima bifurcación en ${nextIn} min virtual${nextIn===1?'':'es'}`:'Reanuda para llegar al siguiente punto de decisión'}</span></div>
      </div>}
      {fork&&<div className="v17-stage__fork" role="group" aria-label="Bifurcación, elige una ruta">
        <div className="v17-stage__fork-title"><span>CHECKPOINT · {p.elapsed} MIN</span><h3>¿QUÉ CAMINO TOMAS?</h3>
          <p>La conducción está pausada. Elige una vía; AutoOS aplicará las consecuencias sobre los recursos y continuará.</p></div>
        <div className={`v17-stage__paths v17-stage__paths--${paths.length}`}>
          {paths.map((option,i)=><button type="button" key={option.id}
            className="v17-stage__path" disabled={!canChoosePathV17(viewInput,allowed)}
            onClick={()=>p.onSelect(option.id)} aria-label={`Camino ${i+1}: ${option.label}. ${option.detail}`}>
            <span className="v17-stage__path-number">RUTA 0{i+1}</span>
            <strong>{option.label}</strong><small>{option.detail}</small><span className="v17-stage__path-go">ELEGIR <ChevronRight size={15}/></span>
          </button>)}
        </div>
        {!allowed&&<p className="v17-stage__access">El perfil actual no tiene autorización para tomar decisiones técnicas.</p>}
      </div>}
      {riskStop && <div className="v18-stage__consequence" role="status">
        <span>RIESGO SOSTENIDO</span>
        <h3>AUTOOS DETUVO EL VEHÍCULO</h3>
        <p>La elección de continuar sin corregir la anomalía produjo una detención preventiva. Debes reanudar manualmente o reiniciar el escenario.</p>
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
      <div><button type="button" disabled={!p.active||p.finished||!allowed||fork||view==='exhausted'} onClick={p.onTogglePause}>
        {p.running?<Pause size={16}/>:<Play size={16}/>} {p.running?'PAUSAR':'REANUDAR'}</button>
        <button type="button" disabled={!p.active||!allowed} onClick={p.onRestart}><RotateCcw size={16}/> REINICIAR</button></div>
      <label>VELOCIDAD VIRTUAL <input type="range" min={0} max={120} step={5} value={p.speed}
        onChange={e=>p.onSpeed(Number(e.target.value))} disabled={!p.active||p.finished||!allowed||fork}/><b>{p.speed} km/h</b></label>
      <small><AlertTriangle size={14}/> Modelo didáctico: 1 s = 1 min virtual</small>
    </footer>
  </section>;
}
