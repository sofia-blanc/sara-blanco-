/**
 * AUTOOS V11 — Cabecera integrada con navegación a siete módulos.
 * El tema claro conserva el encabezado AZUL oscuro para asegurar contraste.
 * Su estado proviene exclusivamente de App.tsx (sin duplicar indicadores).
 */
import React from 'react';
import {ArrowLeft,BatteryCharging,CarFront,ChevronRight,Home,Moon,Shield,Sun,Volume2,VolumeX} from 'lucide-react';
import type {UserRole} from '../types/scheduler';
import {V11_MENU_ITEMS,type AutoOSModule} from './CinematicMenu';

export interface ModuleSceneProps {
  active:AutoOSModule;role:UserRole;batteryLevel:number;theme:'dark'|'light';
  status:'normal'|'warning'|'failure';supabaseConfigured:boolean;audioMuted:boolean;
  onToggleAudio:()=>void;onHome:()=>void;onSelect:(tab:AutoOSModule)=>void;
  onRoleChange:(role:UserRole)=>void;onThemeChange:()=>void;onRestricted:(action:string)=>void;
}
// AUTOOS_V12_APLICADO: título descriptivo para el módulo técnico.
export function ModuleScene(p:ModuleSceneProps){
  const current=V11_MENU_ITEMS.find(i=>i.key===p.active)||V11_MENU_ITEMS[0];const Icon=current.icon;
  const select=(module:AutoOSModule)=>{if(module==='SCHEDULER'&&p.role!=='mecanico'){p.onRestricted('Abrir el planificador RTOS');return;}p.onSelect(module);};
  return <header className={`v11-stage ${p.active==='COCKPIT'?'v12-stage--cabina':''}`} data-autoos-theme={p.theme}>
    <div className="v11-stage__texture" aria-hidden="true"/>
    <div className="v11-stage__bar"><span><CarFront size={20}/> AUTOOS <b>/ BLUE SHIFT</b></span>
      <button onClick={p.onHome}><ArrowLeft size={18}/> MENÚ PRINCIPAL</button></div>
    <div className="v11-stage__core"><div className="v11-stage__title"><p>MÓDULO {current.number} // {current.sub}</p>
      <h1>{p.active==='COCKPIT'?'CABINA Y TELEMETRÍA':current.name}<span aria-hidden="true">{current.number}</span></h1>
      <div className="v11-stage__details"><span>● {p.status==='normal'?'SISTEMA ACTIVO':p.status==='warning'?'PRECAUCIÓN':'FALLA DETECTADA'}</span>
      <span><BatteryCharging size={14}/> {p.batteryLevel.toFixed(1)}% BMS</span>
      <span>{p.supabaseConfigured?'SUPABASE: CREDENCIALES WEB':'NUBE: VERIFICAR EN DIAGNÓSTICO'}</span></div>
    </div><div className="v11-stage__mark"><Icon size={114} strokeWidth={.7}/></div></div>
    <div className="v11-stage__dock"><nav aria-label="Secciones de AutoOS">{V11_MENU_ITEMS.map(item=><button key={item.key}
      onClick={()=>select(item.key)} className={p.active===item.key?'is-active':''} aria-current={p.active===item.key?'page':undefined}>
      <span>{item.number}</span>{item.name}<ChevronRight size={13}/></button>)}</nav>
      <div className="v11-stage__tools"><select aria-label="Perfil" value={p.role} onChange={e=>p.onRoleChange(e.target.value as UserRole)}>
        <option value="mecanico">MECÁNICO</option><option value="conductor">CONDUCTOR</option><option value="pasajero">PASAJERO</option></select>
        <button aria-label="Activar o silenciar sonido" onClick={p.onToggleAudio}>{p.audioMuted?<VolumeX size={19}/>:<Volume2 size={19}/>}</button>
        <button aria-label="Cambiar tema" onClick={p.onThemeChange}>{p.theme==='dark'?<Sun size={19}/>:<Moon size={19}/>}</button>
      </div></div>
  </header>;
}
