/**
 * AUTOOS V11 — Centro de operaciones, GPS, caja negra y diagnóstico Cloud.
 *
 * Estos módulos son VISTAS del estado único de App.tsx. No hay otra batería,
 * otra memoria ni otros procesos paralelos. Un GPS en fallo congela las
 * coordenadas, y el reloj continúa porque lo ejecuta el motor de CPU V9.
 *
 * El mapa SVG es un CIRCUITO DIDÁCTICO; no pretende sustituir un proveedor
 * de cartografía real. "Ubicación del navegador" pide permiso explícito.
 */
import React, {useEffect,useMemo,useState} from 'react';
import {NavigationMissionV15} from './NavigationMissionV15'; // AUTOOS_V15_APLICADO
import {canExecute} from '../simulation/accessPolicyV15';
import type {MissionDecision} from '../simulation/missionDecisionsV15';
import { Activity, ArrowRight, AlertTriangle, BatteryCharging, CheckCircle2, Cloud, CloudOff,
  Compass, Cpu, Download, ExternalLink, HardDrive, History, MapPin, Navigation, Pause,
  Play, RadioTower, RefreshCw, Route, Shield, ShieldAlert, Signal, Wifi, Zap } from 'lucide-react';
import type {BatteryState, VehicleDevice, UserRole} from '../types/scheduler';
import type {SimulationState} from '../utils/schedulerEngine';
import type {OSResourceSample,OSResourceSnapshot} from '../simulation/resources';
import type {AutoOSModule} from './CinematicMenu';
import { DEMO_ROUTES, currentRoute, etaMinutes, routeProgress, type MissionEvent, type MissionState, type RouteId } from '../simulation/navigation';
import {testSupabaseConnection,logSimulatorEvent,isSupabaseConfigured} from '../supabaseClient';
import {sendCloudRequest, getPythonKernelStatus} from '../kernelBridge';
import type {BlackboxCloudStatus} from '../cloud/blackboxSync'; // AUTOOS_V14_BLACKBOX_CLOUD

export type OperationsPage = 'HOME'|'GPS'|'BLACKBOX'|'CLOUD';

export interface OperationsProps {
  page:OperationsPage;
  resources:OSResourceSnapshot;
  resourceHistory:OSResourceSample[];
  simState:SimulationState;
  battery:BatteryState;
  devices:VehicleDevice[];
  mission:MissionState;
  missionEvents:MissionEvent[];
  role:UserRole;
  onNavigate:(tab:AutoOSModule)=>void;
  onRoute:(id:RouteId)=>void;
  onMissionStart:()=>void;
  onMissionStop:()=>void;
  onMissionTick:()=>void;
  onMissionSpeed:(speed:number)=>void;
  onInjectGpsFault:()=>void;
  onDecision:(decision:MissionDecision)=>void;
  blackboxCloud:BlackboxCloudStatus;
  onRetryBlackbox:()=>void;
}

function Kpi({label,value,unit,detail,emphasis=false}:{label:string;value:string|number;unit?:string;detail?:string;emphasis?:boolean}) {
  return <div className={`v11-kpi ${emphasis?'v11-kpi--hero':''}`}><span>{label}</span><strong>{value}<small>{unit}</small></strong>{detail&&<em>{detail}</em>}</div>;
}

function StatusLabel({ok,text}:{ok:boolean;text:string}) {
  return <span className={`v11-status ${ok?'v11-status--ok':'v11-status--warn'}`}>
    {ok?<CheckCircle2 size={15}/>:<AlertTriangle size={15}/>} {text}</span>;
}

function Trend({points}:{points:number[]}) {
  const vals = points.slice(-36);
  if (vals.length < 2) return <span className="v11-muted">La tendencia aparecerá al avanzar los ticks.</span>;
  const min=Math.min(...vals), max=Math.max(...vals), range=Math.max(1,max-min);
  const path=vals.map((v,i)=>`${i?'L':'M'}${i/(vals.length-1)*500},${112-(v-min)/range*90}`).join(' ');
  return <svg viewBox="0 0 500 140" className="v11-trend" role="img" aria-label="Evolución de recursos por tick">
    <path d="M0 115H500 M0 70H500 M0 25H500" stroke="currentColor" strokeOpacity=".14" fill="none"/>
    <path d={path} stroke="var(--v11-cyan)" strokeWidth="4" fill="none" strokeLinecap="round"/>
  </svg>;
}

function Home({p}:{p:OperationsProps}) {
  const failed=p.devices.filter(d=>d.status!=='operativo');
  const healthy=p.battery.level>20&&failed.length===0;
  return <div className="v11-wrap v11-home">
    <div className="v11-home__hero">
      <div className="v11-home__copy"><p className="v11-eyebrow">01 // ESTADO GENERAL DEL SISTEMA</p>
      <h2>EL VEHÍCULO <span>ESTÁ {healthy?'LISTO':'EN ALERTA'}</span></h2>
      <p>AutoOS coordina procesos, CPU, memoria, energía, navegación y sensores. Cada escenario modifica el mismo estado del laboratorio.</p>
      <div className="v11-inline"><StatusLabel ok={healthy} text={healthy?'Sistema en condiciones de simulación nominales':`${failed.length} subsistemas requieren atención`}/>
      <StatusLabel ok={p.resources.swapRequestedMb===0} text={p.resources.swapRequestedMb?'Memoria bajo presión':'RAM disponible'}/></div>
      <div className="v11-actions">
        <button className="v11-primary" onClick={()=>p.onNavigate('GPS')}><Navigation size={18}/> INICIAR NAVEGACIÓN <ArrowRight size={17}/></button>
        <button className="v11-secondary" onClick={()=>p.onNavigate('SIMULATOR')}><Zap size={17}/> LABORATORIO DE FALLAS</button>
      </div></div>
      <div className="v11-home__instrument"><div className="v11-target"><span>RTOS</span><Cpu size={112} strokeWidth={.8}/><b>{Math.min(100,Math.round(p.resources.cpuBusyPct))}%</b><small>CPU UTILIZADA</small></div></div>
    </div>
    <div className="v11-kpis">
      <Kpi label="CPU · DEMANDA" value={Math.round(p.resources.cpuDemandPct)} unit="%" detail="Carga solicitada por procesos"/>
      <Kpi label="RAM · FIRST-FIT EST." value={Math.round(p.resources.ramPhysicalMb)} unit="/ 2048 MB" detail={`SWAP estimada: ${Math.round(p.resources.swapRequestedMb)} MB`}/>
      <Kpi label="BATERÍA BMS" value={p.battery.level.toFixed(1)} unit="%" detail={`${Math.round(p.resources.totalPowerW)} W modelo virtual`}/>
      <Kpi label="PROCESOS ADMITIDOS" value={p.resources.admittedCount} detail={`Tick #${p.resources.tick} · ${p.resources.suspendedCount} suspendidos`}/>
    </div>
    <div className="v11-home__bottom"><section className="v11-section v11-home__timeline">
      <p className="v11-eyebrow">HISTORIA DEL VEHÍCULO</p><h3>Lo que ocurrió <span>en los últimos ticks</span></h3>
      <Trend points={p.resourceHistory.map(v=>v.ramPhysicalMb)}/>
      <p className="v11-muted">RAM física estimada por proceso, en MB. Consulta el Panel RTOS para las reservas reales del kernel Python.</p>
    </section><section className="v11-section v11-home__links"><p className="v11-eyebrow">ACCESO DIRECTO</p>
      {([['GPS','GPS y ruta'],['COCKPIT','Instrumentos de cabina'],['SCHEDULER','Planificador RTOS'],['BLACKBOX','Caja negra y auditoría']] as const).map(([tab,label],i)=>
        <button key={tab} onClick={()=>p.onNavigate(tab)}><span>0{i+1}</span><strong>{label}</strong><ArrowRight size={18}/></button>)}
    </section></div>
  </div>;
}

// V15: sustituimos SOLO la vista GPS; el estado y callbacks siguen en App.tsx.
function GPS({p}:{p:OperationsProps}) {return <NavigationMissionV15 p={p}/>;}

function BlackBox({p}:{p:OperationsProps}) {
  const entries=useMemo(()=>[
    ...p.missionEvents.map(e=>({id:e.id,time:e.timestamp,text:e.message,kind:e.kind,severity:e.severity,tick:e.tick})),
    ...p.simState.events.map(e=>({id:e.id,time:e.timestamp,text:e.message,kind:e.type,severity:e.severity,tick:e.time}))
  ].sort((a,b)=>b.tick-a.tick || b.time.localeCompare(a.time)).slice(0,120),[p.missionEvents,p.simState.events]);
  const [filter,setFilter]=useState<'all'|'warning'>('all');
  const displayed=filter==='all'?entries:entries.filter(e=>e.severity==='warning'||e.severity==='critical');
  const exportJSON=()=>{
    const payload={title:'AutoOS — Caja negra del laboratorio',generatedAt:new Date().toISOString(),
      note:'Registro didáctico; se separan métricas React y kernel Python.',
      resources:p.resources,mission:p.mission,entries};
    const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});
    const url=URL.createObjectURL(blob); const link=document.createElement('a');link.href=url;link.download='AutoOS_caja_negra.json';link.click();
    window.setTimeout(()=>URL.revokeObjectURL(url),1500);
  };
  return <div className="v11-wrap v11-blackbox"><div className="v11-section-heading"><div><p className="v11-eyebrow">TRAZABILIDAD OPERACIONAL</p><h2>CAJA <em>NEGRA</em></h2><p>Historial unido de ruta, simulación, CPU y decisiones del usuario.</p></div>
  <button className="v11-primary" disabled={!canExecute(p.role,'audit.read')} onClick={exportJSON}><Download size={17}/> EXPORTAR JSON</button></div>
  <div className="v14-cloud-sync" role="status" aria-live="polite">
    <div><strong>Sincronización automática · Supabase</strong>
      <span>Confirmados: {p.blackboxCloud.confirmed} · Pendientes: {p.blackboxCloud.pending}</span>
      <small>{p.blackboxCloud.message}</small>
    </div>
    <button type="button" className="v11-secondary" disabled={!canExecute(p.role,'audit.read')} onClick={p.onRetryBlackbox}>
      <RefreshCw size={16}/> REINTENTAR PENDIENTES
    </button>
  </div>
  <div className="v11-kpis"><Kpi label="EVENTOS" value={entries.length}/><Kpi label="TICKS DEL SO" value={p.resources.tick}/><Kpi label="SWAP ESTIMADA" value={p.resources.swapRequestedMb} unit="MB"/><Kpi label="FALLAS DE DISPOSITIVOS" value={p.resources.faultsCount}/></div>
  <div className="v11-blackbox__body"><section className="v11-section"><div className="v11-section-heading"><h3>Registro de acontecimientos</h3><div className="v11-switch"><button className={filter==='all'?'is-active':''} onClick={()=>setFilter('all')}>TODOS</button><button className={filter==='warning'?'is-active':''} onClick={()=>setFilter('warning')}>ALERTAS</button></div></div>
  <div className="v11-events">{displayed.length?displayed.map(e=><div className="v11-event" key={`${e.kind}-${e.id}`}><small>TICK {e.tick}</small><div><b>{e.kind}</b><p>{e.text}</p></div><span className={`v11-event__${e.severity}`}>{e.severity.toUpperCase()}</span></div>):<p className="v11-muted">Aún no hay eventos. Inicia una ruta o un escenario de simulación.</p>}</div></section>
  <section className="v11-section"><p className="v11-eyebrow">HISTORIAL GRÁFICO</p><h3>Consumo de CPU y batería</h3><Trend points={p.resourceHistory.map(v=>v.cpuDemandPct)}/><p className="v11-muted">Demanda de CPU (%) por ciclo de la simulación React.</p><Trend points={p.resourceHistory.map(v=>v.batteryPct)}/><p className="v11-muted">Carga de batería simulada (%) por ciclo.</p>
  <button className="v11-secondary" disabled={!canExecute(p.role,'kernel.configure')} onClick={()=>p.onNavigate('SCHEDULER')}><Cpu size={18}/> VER PROCESOS Y GANTT</button></section></div></div>;
}

function CloudStatus({p}:{p:OperationsProps}) {
  // AUTOOS_EVENT_ACK_FIX_V12_1: los acuses se enlazan por requestId.
  // Una consulta correcta NO implica que el INSERT del evento haya funcionado.
  type CloudResult = {ok:boolean;message:string;ack?:string};
  type Pending = {id:string;type:'test'|'event';message?:string};
  const [direct,setDirect]=useState<{ok:boolean;message:string}|null>(null);
  const [busy,setBusy]=useState(false);
  const [feedback,setFeedback]=useState('');
  const [server,setServer]=useState<CloudResult|null>(getPythonKernelStatus()?.cloud??null);
  const pendingRef=React.useRef<Pending|null>(null);
  const timeoutRef=React.useRef<number|null>(null);

  useEffect(()=>{
    const handler=(ev:Event)=>{
      const obj=(ev as CustomEvent).detail?.cloud as CloudResult|undefined;
      if(!obj)return;
      setServer(obj);
      // Ignorar respuestas anteriores: solo la solicitud actual modifica su resultado.
      const pending=pendingRef.current;
      if(!pending || obj.ack!==pending.id)return;
      pendingRef.current=null;
      if(timeoutRef.current!==null)window.clearTimeout(timeoutRef.current);
      timeoutRef.current=null;
      setBusy(false);
      if(obj.ok){
        setFeedback(pending.type==='event'
          ? `CONFIRMADO por Streamlit: ${obj.message} Busca el texto exacto "${pending.message}" en public.eventos.`
          : `CONSULTA CONFIRMADA: ${obj.message}`);
      }else{
        setFeedback(`OPERACIÓN RECHAZADA: ${obj.message}`);
      }
    };
    window.addEventListener('autoos:kernel-update',handler);
    return()=>{
      window.removeEventListener('autoos:kernel-update',handler);
      if(timeoutRef.current!==null)window.clearTimeout(timeoutRef.current);
    };
  },[]);

  const waitForServer=(request:Pending)=>{
    pendingRef.current=request;
    setBusy(true);
    setFeedback('Solicitud enviada. Esperando confirmación de Streamlit…');
    if(timeoutRef.current!==null)window.clearTimeout(timeoutRef.current);
    timeoutRef.current=window.setTimeout(()=>{
      // Un timeout NO confirma que la BD haya fallado; solo falta acuse del puente.
      if(pendingRef.current?.id===request.id){
        pendingRef.current=null;
        setBusy(false);
        setFeedback('SIN CONFIRMACIÓN: el servidor no respondió en 12 segundos. Comprueba Streamlit y vuelve a consultar la tabla antes de repetir el envío.');
      }
    },12000);
  };

  const check=async()=>{
    setBusy(true);setFeedback('');
    const id=`cloud_${Date.now().toString(36)}_${Math.random().toString(36).slice(2,8)}`;
    const serverSent=sendCloudRequest({type:'autoos:cloud-test',requestId:id});
    if(serverSent)waitForServer({id,type:'test'});
    const result=await testSupabaseConnection();
    setDirect(result);
    if(!serverSent){
      setBusy(false);
      setFeedback(result.ok
        ? `Consulta directa desde navegador confirmada: ${result.message}`
        : 'Puente Streamlit no disponible. Abre AutoOS mediante streamlit run app.py; el cliente React no tiene credenciales frontend.');
    }
  };

  const pushEvent=async()=>{
    setBusy(true);setFeedback('');
    // ID buscable en Table Editor; el servidor no confunde este evento con el diagnóstico CLI.
    const id=`event_${Date.now().toString(36)}_${Math.random().toString(36).slice(2,8)}`;
    const message=`Informe manual AutoOS [${id}]: tick=${p.resources.tick}, batería=${p.battery.level.toFixed(1)}%, RAM estimada=${p.resources.ramPhysicalMb} MB, fallas=${p.resources.faultsCount}`;
    const serverSent=sendCloudRequest({type:'autoos:cloud-event',requestId:id,message,severity:'info'});
    if(serverSent){waitForServer({id,type:'event',message});return;}
    // Solo para Vite local; no implica que el servidor de Streamlit esté conectado.
    const saved=await logSimulatorEvent('simulacion','info',message,{tick:p.resources.tick,batteryPct:p.battery.level});
    setBusy(false);
    setFeedback(saved
      ? `CONFIRMADO por cliente web: busca "${message}" en public.eventos.`
      : 'NO ENVIADO: no hay puente Streamlit ni credenciales públicas configuradas para el cliente web.');
  };
  const verified=Boolean(direct?.ok||server?.ok);
  return <div className="v11-wrap v11-cloud"><div className="v11-cloud__hero"><Cloud size={67} strokeWidth={1}/><p className="v11-eyebrow">PERSISTENCIA Y CONECTIVIDAD</p><h2>NUBE / <em>SUPABASE</em></h2>
  <p>No confundimos “credenciales presentes” con “conexión comprobada”. El indicador solo cambia a ONLINE tras una consulta real.</p>
  <StatusLabel ok={verified} text={verified?'CONSULTA A SUPABASE CONFIRMADA':'CONEXIÓN NO VERIFICADA'}/>
  <div className="v11-actions"><button className="v11-primary" disabled={busy} onClick={check}><RefreshCw size={17}/> {busy?'VERIFICANDO…':'VERIFICAR CONEXIÓN REAL'}</button>
  <button className="v11-secondary" disabled={busy} onClick={pushEvent}><Cloud size={17}/> REGISTRAR EVENTO DE PRUEBA</button></div></div>
  <div className="v11-cloud__details"><section className="v11-section"><h3>Servidor Streamlit</h3><p>Utiliza <code>st.secrets</code> del despliegue; no envía claves secretas al navegador.</p><StatusLabel ok={!!server?.ok} text={server?.ok?'Verificado':'No verificado'}/><p className="v11-muted">{server?.message||'Para verificar, abre AutoOS desde Streamlit y pulsa el botón.'}</p></section>
  <section className="v11-section"><h3>Cliente React</h3><p>Requiere una clave pública (anon/publishable) y las reglas RLS de Supabase.</p><StatusLabel ok={!!direct?.ok} text={direct?.ok?'Verificado':isSupabaseConfigured()?'Configurado, pendiente de prueba':'Sin credenciales frontend'}/><p className="v11-muted">{direct?.message||'No se ha realizado una consulta directa.'}</p></section></div>
  {feedback&&<p role="status" className="v11-cloud__feedback">{feedback}</p>}
  <p className="v11-muted">Las mediciones de RAM/CPU se originan en la simulación React. Para comparar reservas reales de memoria First-Fit abre el monitor de Kernel Python en el Planificador.</p>
  </div>;
}

export function AutoOSModulesV11(p:OperationsProps) {
  switch(p.page){case 'HOME':return <Home p={p}/>;case 'GPS':return <GPS p={p}/>;case 'BLACKBOX':return <BlackBox p={p}/>;case 'CLOUD':return <CloudStatus p={p}/>;}
}
