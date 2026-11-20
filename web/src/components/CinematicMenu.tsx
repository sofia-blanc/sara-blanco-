/**
 * AUTOOS V11 — Inicio cinematográfico inspirado en la gramática visual de P3R.
 *
 * Botones oblicuos con selector blanco/rosa, fondo oceánico animado, tipografía
 * inclinada y desplazamiento entre opciones. Ilustración y efectos originales.
 * Las transiciones no alteran el simulador: App.tsx es la única autoridad para
 * seleccionar módulo, rol, batería y estado. Teclado y movimiento reducido.
 */
import React,{useCallback,useEffect,useRef,useState} from 'react';
import {ArrowDown,ArrowUp,BatteryCharging,CarFront,ChevronRight,Cpu,FlaskConical, Gauge,
  History,Home,MapPin,Moon,Shield,Sun,Volume2,VolumeX,Wifi} from 'lucide-react';
import type {UserRole} from '../types/scheduler';

export type AutoOSModule='HOME'|'GPS'|'COCKPIT'|'SIMULATOR'|'SCHEDULER'|'BLACKBOX'|'CLOUD';
type Item={key:AutoOSModule;number:string;name:string;sub:string;icon:typeof Home;restricted?:boolean};
export const V11_MENU_ITEMS:Item[]=[
  {key:'HOME',number:'01',name:'INICIO',sub:'Estado general del sistema operativo',icon:Home},
  {key:'GPS',number:'02',name:'NAVEGACIÓN',sub:'Ruta virtual y GPS del navegador',icon:MapPin},
  {key:'COCKPIT',number:'03',name:'CABINA',sub:'Cabina y telemetría: sensores, comunicaciones y confort',icon:Gauge},
  {key:'SIMULATOR',number:'04',name:'SIMULACIÓN',sub:'Fallas y respuesta de los recursos del SO',icon:FlaskConical},
  {key:'SCHEDULER',number:'05',name:'PLANIFICADOR',sub:'CPU, RAM, prioridades y Gantt',icon:Cpu,restricted:true},
  {key:'BLACKBOX',number:'06',name:'CAJA NEGRA',sub:'Historial, decisiones y auditoría',icon:History},
  {key:'CLOUD',number:'07',name:'SUPABASE',sub:'Nube, persistencia y diagnóstico real',icon:Wifi},
];

// AUTOOS_V12_APLICADO — Vista previa funcional; datos descriptivos, no telemetría ficticia.
const V12_MODULE_INFO: Record<AutoOSModule,{title:string;summary:string;steps:[string,string,string]}> = {
  HOME: {title:'CENTRO DE CONTROL',summary:'Consulta el estado global del sistema operativo.',steps:['CPU, RAM y batería en una sola sesión','Procesos y dispositivos activos','Accesos a las operaciones principales']},
  GPS: {title:'NAVEGACIÓN',summary:'Sigue una ruta virtual y supervisa su impacto sobre el SO.',steps:['Selecciona un destino y comienza la ruta','Observa la posición, señal GNSS y autonomía','Revisa las incidencias en Caja Negra']},
  COCKPIT: {title:'CABINA Y TELEMETRÍA',summary:'Supervisa los subsistemas del vehículo desde sus controles técnicos.',steps:['Elige GPS, cámara, LiDAR o comunicaciones','Inspecciona lecturas y ejecuta controles permitidos','Consulta alertas, multimedia y auditoría']},
  SIMULATOR: {title:'LABORATORIO',summary:'Inyecta eventos y observa cómo responde el sistema operativo.',steps:['Selecciona un escenario de prueba','Compara CPU, RAM, batería y procesos','Genera eventos y examina el historial']},
  SCHEDULER: {title:'PLANIFICADOR RTOS',summary:'Analiza la asignación de CPU y el ciclo de vida de los procesos.',steps:['Consulta las colas y el diagrama Gantt','Observa prioridades, estados y consumo','Compara recursos con los escenarios de simulación']},
  BLACKBOX: {title:'CAJA NEGRA',summary:'Investiga la trazabilidad de la sesión actual.',steps:['Revisa eventos de navegación y simulación','Filtra incidencias y acciones del usuario','Exporta evidencias para el informe']},
  CLOUD: {title:'DATOS Y SUPABASE',summary:'Comprueba la conexión real con el almacenamiento del servidor.',steps:['Verifica credenciales desde el backend','Prueba consultas según permisos','Distingue persistencia local de la nube']},
};

export interface CinematicMenuProps {
  role:UserRole;batteryLevel:number;health:number;onNavigate:(module:AutoOSModule)=>void;
  audioMuted:boolean;onToggleAudio:()=>void;onRoleChange:(role:UserRole)=>void;
  theme:'dark'|'light';onToggleTheme:()=>void;
}

function playFeedback(kind:'change'|'open'|'locked',muted:boolean) {
  if(muted||!window.AudioContext)return;
  try{
    const context=new AudioContext();const o=context.createOscillator(),g=context.createGain(),t=context.currentTime;
    o.type=kind==='locked'?'triangle':'sine';o.frequency.setValueAtTime(kind==='open'?440:kind==='locked'?210:680,t);
    o.frequency.exponentialRampToValueAtTime(kind==='open'?920:kind==='locked'?150:820,t+.14);
    g.gain.setValueAtTime(.001,t);g.gain.exponentialRampToValueAtTime(.04,t+.016);g.gain.exponentialRampToValueAtTime(.001,t+.16);
    o.connect(g);g.connect(context.destination);o.start(t);o.stop(t+.18);o.onended=()=>{void context.close();};
  }catch{ /* Autoplay bloqueado: menú usable sin sonido. */ }
}

export function CinematicMenu({role,batteryLevel,health,onNavigate,audioMuted,onToggleAudio,onRoleChange,theme,onToggleTheme}:CinematicMenuProps){
  const [selected,setSelected]=useState(0),[leaving,setLeaving]=useState(false),[warning,setWarning]=useState('');
  const t=useRef<ReturnType<typeof setTimeout>|null>(null);
  const select=useCallback((i:number)=>{if(leaving)return;setSelected(i);setWarning('');playFeedback('change',audioMuted);},[audioMuted,leaving]);
  const open=useCallback((i:number)=>{
    const item=V11_MENU_ITEMS[i];if(!item||leaving)return;
    if(item.restricted&&role!=='mecanico'){playFeedback('locked',audioMuted);setWarning('Planificador RTOS: se necesita el rol Mecánico / Admin.');return;}
    playFeedback('open',audioMuted);setLeaving(true);
    t.current=setTimeout(()=>onNavigate(item.key),window.matchMedia('(prefers-reduced-motion: reduce)').matches?0:280);
  },[audioMuted,leaving,onNavigate,role]);
  useEffect(()=>{
    const key=(e:KeyboardEvent)=>{
      if(['INPUT','TEXTAREA','SELECT'].includes((e.target as HTMLElement)?.tagName))return;
      if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();select((selected+(e.key==='ArrowDown'?1:-1)+V11_MENU_ITEMS.length)%V11_MENU_ITEMS.length);}
      if(e.key==='Enter'){e.preventDefault();open(selected);}
      if(/^[1-7]$/.test(e.key)){e.preventDefault();select(Number(e.key)-1);}
    };
    window.addEventListener('keydown',key);return()=>window.removeEventListener('keydown',key);
  },[selected,select,open]);
  useEffect(()=>()=>{if(t.current)clearTimeout(t.current);},[]);
  const current=V11_MENU_ITEMS[selected];const CurrentIcon=current.icon;
  return <section className={`v11-menu ${leaving?'v11-menu--leaving':''}`} data-autoos-theme={theme} aria-label="Menú de inicio AutoOS">
    <div className="v11-menu__ocean" aria-hidden="true"/><div className="v11-menu__ripple" aria-hidden="true"/>
    <div className="v11-menu__particles" aria-hidden="true"/>
    <header className="v11-menu__top"><div className="v11-menu__brand"><CarFront size={27}/><b>AUTOOS</b><span> // RELOAD</span></div>
      <div className="v11-menu__options"><span className="v11-menu__online">● SISTEMA VEHICULAR · SIMULACIÓN RTOS</span>
        <button onClick={onToggleTheme} aria-label={`Cambiar a modo ${theme==='dark'?'claro':'oscuro'}`}>{theme==='dark'?<Sun size={19}/>:<Moon size={19}/>} {theme==='dark'?'CLARO':'OSCURO'}</button>
        <button onClick={onToggleAudio} aria-pressed={!audioMuted}>{audioMuted?<VolumeX size={19}/>:<Volume2 size={19}/>} {audioMuted?'OFF':'ON'}</button>
      </div></header>
    {/* Vista previa estática: reemplaza SVG vertical pesado y partículas animadas. */}
    <aside className="v12-menu__preview" aria-label={`Vista previa de ${current.name}`}>
      <div className="v12-menu__preview-top"><span>VISTA PREVIA / {current.number}</span><span>SISTEMA OPERATIVO</span></div>
      <div className="v12-menu__preview-icon"><CurrentIcon size={46} strokeWidth={1.5}/><span className="v12-menu__preview-index">{current.number} / 07</span></div>
      <p className="v12-menu__preview-eyebrow">MÓDULO SELECCIONADO</p>
      <h2>{V12_MODULE_INFO[current.key].title}</h2>
      <p className="v12-menu__preview-summary">{V12_MODULE_INFO[current.key].summary}</p>
      <div className="v12-menu__preview-steps">{V12_MODULE_INFO[current.key].steps.map((step,i)=><div key={step}><span>0{i+1}</span><p>{step}</p></div>)}</div>
      <div className="v12-menu__preview-metrics"><span><BatteryCharging size={16}/> BMS <b>{batteryLevel.toFixed(0)}%</b></span><span><Shield size={16}/> SALUD <b>{health}%</b></span></div>
      <button type="button" className="v12-menu__preview-open" onClick={()=>open(selected)}>
        ABRIR {current.name} <ChevronRight size={20}/>
      </button>
    </aside>
    <div className="v11-menu__content"><span className="v11-menu__pretitle">SISTEMA OPERATIVO PARA VEHÍCULO INTELIGENTE</span>
      <h1 className="v11-menu__logo"><span>AUTO</span><i>OS</i><sup>11</sup></h1>
      <div className="v11-menu__command"><span>SELECCIONA UN MÓDULO</span><i>///</i></div>
      <nav className="v11-menu__nav" aria-label="Módulos de AutoOS">
        {V11_MENU_ITEMS.map((item,i)=>{const Icon=item.icon;const locked=item.restricted&&role!=='mecanico';return <button
          key={item.key} type="button" className={`v11-menu__choice ${selected===i?'is-active':''}`}
          style={{'--row-indent':`${i*11}px`} as React.CSSProperties} aria-current={selected===i?'page':undefined}
          aria-label={item.name+(locked?' restringido':'')}
          onMouseEnter={()=>{if(selected!==i)select(i)}} onFocus={()=>{if(selected!==i)setSelected(i)}} onClick={()=>open(i)}>
            <span>{item.number}</span><Icon size={19}/><strong>{item.name}</strong>{locked?<Shield size={17}/>:<ChevronRight size={21}/>}</button>})}
      </nav>
      <div className="v11-menu__warning" aria-live="polite">{warning||'\u00a0'}</div>
      <div className="v11-menu__selected"><div className="v11-menu__selectedicon"><CurrentIcon size={27}/></div><span>SELECCIÓN {current.number} / 07<strong>{current.sub}</strong></span></div>
    </div>
    <footer className="v11-menu__footer"><div><ArrowUp size={18}/><ArrowDown size={18}/> MOVER <b>ENTER</b> CONFIRMAR <span>1—7 ACCESO DIRECTO</span></div>
      <div className="v11-menu__metrics"><BatteryCharging size={16}/> {batteryLevel.toFixed(0)}% BMS · SALUD {health}%</div>
      <label>PERFIL <select value={role} onChange={e=>onRoleChange(e.target.value as UserRole)} aria-label="Perfil de demostración">
        <option value="mecanico">MECÁNICO / ADMIN</option><option value="conductor">CONDUCTOR</option><option value="pasajero">PASAJERO</option></select></label></footer>
  </section>;
}
