/**
 * AUTOOS V15 — Navegación operativa, juego de decisiones y salud periférica.
 *
 * Este componente NO crea una segunda simulación: consume el mismo estado
 * BatteryState, VehicleDevice, MissionState, SimulationState y OSResourceSnapshot
 * administrado por App.tsx. Cada decisión se envía a App para que modifique
 * dispositivos/energía/planificador y produzca eventos para Caja Negra/Supabase.
 *
 * IMPORTANTE: carretera, coordenadas y vehículo son DIDÁCTICOS; no son un
 * mapa de carreteras ni telemetría de un automóvil físico.
 */
import React,{useState} from 'react';
import {AlertTriangle,ArrowRight,BatteryCharging,CheckCircle2,Clock3,Cpu,Gauge,
  HardDrive,MapPin,Navigation,Pause,Play,Route,ShieldCheck,Signal,Wifi,Zap} from 'lucide-react';
import type {OperationsProps} from './AutoOSModulesV11';
import {VehicleArtworkV15} from './VehicleArtworkV15';
import {canExecute} from '../simulation/accessPolicyV15';
import {MISSION_OPTIONS,type MissionDecision} from '../simulation/missionDecisionsV15';
import {DEMO_ROUTES,currentRoute,etaMinutes,routeProgress,type RouteId} from '../simulation/navigation';

const DIAGNOSTICS = [
  {code:'DEV_GPS_01',name:'GNSS / GPS',pos:'gps'},
  {code:'DEV_CAM_FRONT',name:'Cámara ADAS',pos:'camera'},
  {code:'DEV_LIDAR_01',name:'LiDAR',pos:'lidar'},
  {code:'DEV_RADAR_01',name:'Radar',pos:'radar'},
  {code:'DEV_GATEWAY_CAN',name:'Bus CAN-FD',pos:'can'},
  {code:'DEV_COM_V2X',name:'Red V2X',pos:'network'},
  {code:'DEV_BATTERY_BMS',name:'BMS',pos:'bms'},
] as const;
const statusText = (s:string) => s==='operativo'?'OPERATIVO':s==='degradado'?'DEGRADADO':s==='falla'?'FALLA':'DESCONECTADO';
const statusStyle = (s:string) => s==='operativo'?'ok':s==='degradado'?'warn':'fail';

export function NavigationMissionV15({p}:{p:OperationsProps}) {
  const route=currentRoute(p.mission.routeId);
  const pct=Math.round(routeProgress(p.mission)*100);
  const alerts=p.devices.filter(d=>d.status!=='operativo');
  const gps=p.devices.find(d=>d.code==='DEV_GPS_01');
  const [notice,setNotice]=useState('');
  const [realPos,setRealPos]=useState<{lat:number,lon:number}|null>(null);
  const [locationInfo,setLocationInfo]=useState('Solo se solicita ubicación cuando pulses este botón.');
  const [showAdvanced,setShowAdvanced]=useState(false);
  const score=p.battery.level<=15 || alerts.some(d=>d.criticalLevel==='critico'&&d.status==='falla')?'ALTO RIESGO':
    alerts.length||p.resources.cpuDemandPct>90?'PRECAUCIÓN':'OPERACIÓN ESTABLE';
  const choices=MISSION_OPTIONS.filter(option=>canExecute(p.role,option.permission))
    .filter(option=>{
      if(option.id==='start')return !p.mission.active;
      if(option.id==='continue')return p.mission.active;
      if(option.id==='recover')return gps?.status!=='operativo';
      if(option.id==='inject')return gps?.status==='operativo';
      return true;
    });
  const decide=(id:MissionDecision)=>{
    p.onDecision(id);
    setNotice(`Decisión solicitada: ${MISSION_OPTIONS.find(v=>v.id===id)?.label||id}. Revisa los efectos en Caja Negra.`);
  };
  const checkLocation=()=>{
    if(!navigator.geolocation){setLocationInfo('Este navegador no ofrece Geolocation.');return;}
    setLocationInfo('Solicitando permiso explícito…');
    navigator.geolocation.getCurrentPosition(
      pos=>{setRealPos({lat:pos.coords.latitude,lon:pos.coords.longitude});setLocationInfo('Ubicación obtenida; no se envía a Supabase.');},
      err=>setLocationInfo(`No se pudo obtener ubicación: ${err.message}`),
      {enableHighAccuracy:false,timeout:9500,maximumAge:15000});
  };
  return <main className="v15-mission" aria-label="Misión de navegación y estado integral del SO">
    <header className="v15-mission__head"><div><span className="v15-eyebrow">02 // MISIÓN DE RUTA — DEMOSTRACIÓN</span>
      <h2>NAVEGACIÓN <em>OPERATIVA</em></h2>
      <p>Conduce el vehículo virtual y decide cómo responde AutoOS ante fallas, carga de CPU y consumo energético.</p>
    </div><div className={`v15-risk v15-risk--${score==='OPERACIÓN ESTABLE'?'ok':score==='PRECAUCIÓN'?'warn':'fail'}`}><ShieldCheck size={19}/>{score}</div></header>

    <section className="v15-mission__grid">
      <div className="v15-mission__visual"><div className="v15-mission__visual-head"><span>VISUALIZACIÓN DEL VEHÍCULO</span><strong>{p.mission.active?'EN RUTA':p.mission.completed?'RUTA COMPLETADA':'EN ESPERA'}</strong></div>
        <div className="v15-mission__car">
          <VehicleArtworkV15 compact/>
          <span className="v15-mission__pin v15-mission__pin--gps">GNSS <b className={`v15-led v15-led--${statusStyle(gps?.status??'desconectado')}`}/></span>
          <span className="v15-mission__pin v15-mission__pin--bms">BATERÍA {p.battery.level.toFixed(0)}%</span>
          <span className="v15-mission__pin v15-mission__pin--radar">PERIFÉRICOS {DIAGNOSTICS.length-alerts.filter(d=>DIAGNOSTICS.some(s=>s.code===d.code)).length}/{DIAGNOSTICS.length}</span>
        </div>
        <div className="v15-mission__progresshead"><span>{route.name} · {route.destination}</span><b>{pct}%</b></div>
        <div className="v15-mission__progress" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={pct} aria-label="Progreso de la ruta"><span style={{width:`${pct}%`}}/></div>
        <div className="v15-mission__route-meta"><span><Navigation size={16}/> {p.mission.distanceKm.toFixed(2)} de {route.km} km</span><span><Clock3 size={16}/> ETA {etaMinutes(p.mission)??'—'} min</span>
        <span><Signal size={16}/> {p.mission.signal}</span></div>
      </div>
      <div className="v15-mission__choices"><div className="v15-mission__choices-head"><span className="v15-eyebrow">DECISIONES DEL CONDUCTOR</span><h3>¿QUÉ HARÁ AUTOOS?</h3></div>
        <div className="v15-mission__decision-list">{choices.map((option,i)=><button type="button" key={option.id} onClick={()=>decide(option.id)}
          className={`v15-mission__decision ${option.id==='inject'||option.id==='ignore'?'v15-mission__decision--danger':''}`}>
          <span>0{i+1}</span><span><strong>{option.label}</strong><small>{option.detail}</small></span><ArrowRight size={19}/></button>)}</div>
        <p role="status" className="v15-mission__feedback">{notice||'Selecciona una acción. El efecto quedará registrado como evento de misión.'}</p>
        <p className="v15-mission__disclaimer">Las decisiones son simuladas. No controlan un vehículo real. Los permisos de servidor se comprueban en Python.</p>
      </div>
    </section>

    <section className="v15-mission__telemetry" aria-label="Recursos compartidos con el sistema operativo">
      <div><Cpu size={20}/><span>CPU SOLICITADA</span><strong>{Math.round(p.resources.cpuDemandPct)}<small>%</small></strong></div>
      <div><HardDrive size={20}/><span>RAM FIRST-FIT EST.</span><strong>{Math.round(p.resources.ramPhysicalMb)}<small> MB</small></strong></div>
      <div><BatteryCharging size={20}/><span>CARGA BMS</span><strong>{p.battery.level.toFixed(1)}<small>%</small></strong></div>
      <div><Gauge size={20}/><span>VELOCIDAD</span><strong>{p.mission.speedKmh}<small> km/h</small></strong></div>
      <div><Zap size={20}/><span>PROCESOS ACTIVOS</span><strong>{p.resources.admittedCount}</strong></div>
    </section>

    <section className="v15-mission__bottom"><div className="v15-mission__sensors"><div className="v15-mission__section-title"><h3>SALUD DE PERIFÉRICOS</h3><span>VERDE operativo · AMARILLO degradado · ROJO falla/desconectado</span></div>
      <div className="v15-mission__sensor-grid">{DIAGNOSTICS.map(item=>{
        const device=p.devices.find(d=>d.code===item.code);
        const status=device?.status??'desconectado';
        return <div key={item.code} className={`v15-mission__sensor v15-mission__sensor--${statusStyle(status)}`}>
          <div className="v15-mission__sensor-title"><span className={`v15-led v15-led--${statusStyle(status)}`} /><b>{item.name}</b></div>
          <small>{statusText(status)}</small><div className="v15-mission__health"><span style={{width:`${Math.min(100,Math.max(0,device?.health??0))}%`}}/></div>
          <span className="v15-mission__health-value">{device?.health??0}% salud</span>
        </div>;})}</div></div>
      <aside className="v15-mission__configuration"><div className="v15-mission__section-title"><h3>CONFIGURACIÓN DE RUTA</h3></div>
        <label>DESTINO VIRTUAL<select value={p.mission.routeId} disabled={p.mission.active||!canExecute(p.role,'mission.reroute')} onChange={e=>p.onRoute(e.target.value as RouteId)}>
          {DEMO_ROUTES.map(r=><option key={r.id} value={r.id}>{r.name} — {r.km} km</option>)}
        </select></label><label>VELOCIDAD INICIAL / km/h<select value={p.mission.speedKmh} disabled={!canExecute(p.role,'mission.slow')} onChange={e=>p.onMissionSpeed(Number(e.target.value))}>
          {[0,25,45,65,85].map(v=><option key={v} value={v}>{v} km/h</option>)}</select></label>
        <button type="button" className="v15-mission__advanced" onClick={()=>setShowAdvanced(v=>!v)} aria-expanded={showAdvanced}>
          {showAdvanced?'OCULTAR':'MOSTRAR'} UBICACIÓN DEL NAVEGADOR <MapPin size={16}/></button>
        {showAdvanced&&<div className="v15-mission__geo"><p>La ruta es virtual; la posición real es opcional y no se usa para mover el vehículo.</p>
          <button type="button" onClick={checkLocation}><MapPin size={16}/> SOLICITAR PERMISO</button>
          <small>{locationInfo}</small>{realPos&&<p>Lat {realPos.lat.toFixed(5)} / Lon {realPos.lon.toFixed(5)}</p>}</div>}
        <button type="button" className="v15-mission__lab" onClick={()=>p.onNavigate('SIMULATOR')} disabled={!canExecute(p.role,'simulation.inject')}><AlertTriangle size={18}/> LABORATORIO AVANZADO</button>
        <button type="button" className="v15-mission__lab" onClick={()=>p.onNavigate('BLACKBOX')} disabled={!canExecute(p.role,'mission.start')}><CheckCircle2 size={17}/> VER CAJA NEGRA</button>
      </aside></section>
  </main>;
}
