/**
 * AutoOS · V5 — Vistas nativas de Conducción y Seguridad.
 *
 * POR QUÉ SE CREARON:
 * La versión antigua del Cockpit ofrece una cuadrícula técnica y tarjetas de
 * usuarios que parecen botones sin serlo. Estas vistas presentan las mismas
 * capacidades de forma guiada y usan los estados reales de App.tsx.
 *
 * LÍMITES IMPORTANTES:
 * - NO crean roles ni privilegios. RBAC sigue comprobándose en los componentes
 *   originales y en el backend que corresponda.
 * - NO reemplazan el histórico original del Cockpit. La sección «auditoría
 *   original» continúa disponible mediante el iframe heredado.
 * - Los «eventos de simulación» vienen del estado de la sesión React. No deben
 *   confundirse con auditoría persistente de Supabase.
 */
import React, { useMemo, useRef, useState } from 'react';
import {
  Activity, ArrowRight, BatteryCharging, BookOpen, Camera, Check, CircleAlert,
  ClipboardCopy, Cloud, Cpu, Gauge, Headphones, LockKeyhole, Navigation,
  Radar, ShieldCheck, UserRoundCheck, Users, Wrench,
} from 'lucide-react';
import type { UserRole, VehicleDevice, SimulationEvent } from '../types/scheduler';
import type { CockpitFeatureId } from './CockpitExplorerV4';

type OpenFeature = (feature: CockpitFeatureId) => void;

type OverviewProps = {
  role: UserRole;
  batteryLevel: number;
  devices: VehicleDevice[];
  onOpen: OpenFeature;
};

/**
 * Entrada amigable de Conducción. Las cifras salen del estado real de App.tsx.
 * Pulsar una acción abre el Cockpit original (no una imagen de demostración).
 */
export function CockpitOverviewV5({ role, batteryLevel, devices, onOpen }: OverviewProps) {
  const alerts = devices.filter((device) => device.status === 'falla' || device.status === 'desconectado');
  const operative = devices.filter((device) => device.status === 'operativo').length;
  const averageHealth = devices.length
    ? Math.round(devices.reduce((sum, device) => sum + device.health, 0) / devices.length)
    : 0;

  const [selectedId, setSelectedId] = useState<CockpitFeatureId>('gps');
  const quickActions = [
    { id: 'gps' as const, number: '01', title: 'RUTA Y GPS', sub: 'Ubicación y trayectoria', description: 'Consulta el posicionamiento GNSS, la precisión RTK, los satélites y el trayecto actual.', icon: Navigation },
    { id: 'camera' as const, number: '02', title: 'CÁMARAS', sub: 'Visión y seguridad', description: 'Observa la cámara frontal ADAS y comprueba las señales de la detección visual.', icon: Camera },
    { id: 'lidar' as const, number: '03', title: 'SENSORES', sub: 'LiDAR y radar', description: 'Revisa los sensores que ayudan a identificar obstáculos en el entorno.', icon: Radar },
    { id: 'media' as const, number: '04', title: 'MULTIMEDIA', sub: 'Música y conectividad', description: 'Abre el reproductor, las conexiones Bluetooth y el audio de cabina.', icon: Headphones },
    { id: 'security' as const, number: '05', title: 'SEGURIDAD', sub: 'Perfiles y permisos', description: 'Cambia el perfil de demostración y revisa qué acciones están permitidas.', icon: ShieldCheck },
    { id: 'network' as const, number: '06', title: 'COMUNICACIONES', sub: 'CAN-FD y 5G', description: 'Consulta buses CAN-FD, telemetría y comunicación con otros servicios.', icon: Cloud },
  ];
  const selected = quickActions.find((action) => action.id === selectedId) ?? quickActions[0];
  const SelectedIcon = selected.icon;

  return (
    <div className="autoos-v5-page" aria-label="Resumen interactivo de Conducción">
      <section className="autoos-v5-hero autoos-v5-hero--drive">
        <p className="autoos-v5-eyebrow">AUTOOS / 01 · CABINA INTELIGENTE</p>
        <h2>VEHÍCULO <em>EN CONTROL</em></h2>
        <p>Supervisa el estado del vehículo y elige una función para abrir sus controles reales.</p>
        <div className="autoos-v5-hero__status">
          {alerts.length > 0 ? <CircleAlert size={18} /> : <ShieldCheck size={18} />}
          <strong>{alerts.length ? `${alerts.length} DISPOSITIVOS CON FALLOS` : 'SISTEMA SIN FALLOS CRÍTICOS'}</strong>
          <span>·</span>
          <span>Perfil: {role === 'mecanico' ? 'Mecánico / Admin' : role === 'conductor' ? 'Conductor' : 'Pasajero'}</span>
        </div>
      </section>

      <section className="autoos-v5-metrics" aria-label="Datos actuales del vehículo">
        <div><BatteryCharging size={25} /><span>BATERÍA</span><strong>{Math.round(batteryLevel)}%</strong><small>Nivel disponible</small></div>
        <div><Activity size={25} /><span>SALUD GENERAL</span><strong>{averageHealth}%</strong><small>Promedio de dispositivos</small></div>
        <div><Gauge size={25} /><span>SUBSISTEMAS</span><strong>{operative}/{devices.length}</strong><small>Operativos</small></div>
      </section>

      <section className="autoos-v5-action-section">
        <div className="autoos-v5-section-heading">
          <div><p className="autoos-v5-eyebrow">ELIGE UNA ACCIÓN</p><h3>¿QUÉ QUIERES REVISAR?</h3></div>
          <span>Selecciona una opción y pulsa ABRIR en el panel de la derecha.</span>
        </div>
        <div className="autoos-v5-feature-layout">
          <nav className="autoos-v5-feature-nav" aria-label="Seleccionar una herramienta">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return <button className={`autoos-v5-action ${selectedId === action.id ? 'is-selected' : ''}`}
                type="button" key={action.id} aria-pressed={selectedId === action.id}
                onClick={() => setSelectedId(action.id)}>
                <span className="autoos-v5-action__number">{action.number}</span>
                <Icon size={25} aria-hidden="true" />
                <span className="autoos-v5-action__copy"><strong>{action.title}</strong><small>{action.sub}</small></span>
                <ArrowRight size={20} aria-hidden="true" />
              </button>;
            })}
          </nav>
          <article className="autoos-v5-feature-panel" key={selected.id} aria-live="polite">
            <div className="autoos-v5-feature-panel__watermark"><SelectedIcon strokeWidth={1} /></div>
            <p className="autoos-v5-eyebrow">HERRAMIENTA {selected.number} / {selected.sub.toUpperCase()}</p>
            <h4>{selected.title}</h4>
            <p>{selected.description}</p>
            <button type="button" className="autoos-v5-feature-open" onClick={() => onOpen(selected.id)}>
              ABRIR {selected.title} <ArrowRight size={22} />
            </button>
            <small>Esta acción abre el módulo funcional del vehículo.</small>
          </article>
        </div>
      </section>

      <div className="autoos-v5-note">
        <BookOpen size={22} aria-hidden="true" />
        <div><strong>¿Y el panel anterior?</strong><p>No se eliminó. Puedes consultar sus medidores y tarjetas originales cuando necesites una vista técnica completa.</p></div>
        <button type="button" onClick={() => onOpen('gps')}>ABRIR GPS / HERRAMIENTA REAL {/* AUTOOS_V6_OVERVIEW_LINK */} <ArrowRight size={17} /></button>
      </div>
    </div>
  );
}

/**
 * Catálogo visual alineado con los tres perfiles existentes en el Cockpit.
 * El cambio de perfil reutiliza el selector global de App.tsx; no concede
 * permisos nuevos por sí solo.
 */
const ROLES: ReadonlyArray<{
  id: UserRole;
  label: string;
  description: string;
  allowed: readonly string[];
  restricted: readonly string[];
}> = [
  { id: 'mecanico', label: 'MECÁNICO / ADMIN', description: 'Mantenimiento y supervisión técnica',
    allowed: ['Consultar sensores y telemetría', 'Configurar procesos y planificador', 'Calibrar dispositivos', 'Ejecutar pruebas de fallos'],
    restricted: [] },
  { id: 'conductor', label: 'CONDUCTOR', description: 'Operación habitual del vehículo',
    allowed: ['Consultar la ruta y el estado del vehículo', 'Controlar climatización', 'Utilizar multimedia y asistente'],
    restricted: ['Calibración de hardware', 'Inyección de fallos críticos'] },
  { id: 'pasajero', label: 'PASAJERO', description: 'Funciones de confort de cabina',
    allowed: ['Consultar información de cabina', 'Acceder a multimedia y chat', 'Control de confort permitido'],
    restricted: ['Planificador y procesos críticos', 'Calibración de sensores', 'Inyección de fallos'] },
];

type SecurityProps = {
  role: UserRole;
  onChangeRole: (next: UserRole) => void;
  onOpenOriginalAudit: () => void;
  events: SimulationEvent[];
};

export function CockpitSecurityV5({ role, onChangeRole, onOpenOriginalAudit, events }: SecurityProps) {
  const [query, setQuery] = useState('');
  const [showExport, setShowExport] = useState(false);
  const [copied, setCopied] = useState(false);
  const exportArea = useRef<HTMLTextAreaElement>(null);
  const active = ROLES.find((r) => r.id === role) ?? ROLES[0];

  const filtered = useMemo(() => {
    const search = query.trim().toLocaleLowerCase('es');
    return events.filter((event) => !search ||
      `${event.type} ${event.message} ${event.severity} ${event.timestamp}`.toLocaleLowerCase('es').includes(search))
      .slice().reverse().slice(0, 35);
  }, [events, query]);

  const json = useMemo(() => JSON.stringify({
    origen: 'autoos-simulacion-react',
    descripcion: 'Eventos de la sesión del simulador. No son la auditoría persistente del servidor.',
    eventos: filtered,
  }, null, 2), [filtered]);

  const copyJson = async () => {
    try {
      await navigator.clipboard.writeText(json);
      setCopied(true);
    } catch {
      // Fallback visible: el usuario puede seleccionar y copiar el textarea.
      exportArea.current?.select();
      setCopied(false);
    }
  };

  return (
    <div className="autoos-v5-page autoos-v5-security" aria-label="Seguridad y perfiles interactivos">
      <section className="autoos-v5-hero autoos-v5-hero--security">
        <p className="autoos-v5-eyebrow">AUTOOS / SEGURIDAD · RBAC</p>
        <h2>CONTROLA <em>EL ACCESO</em></h2>
        <p>Selecciona un perfil de demostración, entiende sus permisos y consulta los eventos registrados.</p>
        <div className="autoos-v5-hero__status"><LockKeyhole size={18}/><strong>PERFIL ACTIVO: {active.label}</strong></div>
      </section>
      <section className="autoos-v5-security__roles" aria-label="Cambiar perfil de la demostración">
        <div className="autoos-v5-section-heading"><div><p className="autoos-v5-eyebrow">01 · IDENTIDAD</p><h3>ELIGE UN PERFIL</h3></div>
          <span>Los tres botones cambian el perfil activo de la simulación.</span></div>
        <div className="autoos-v5-security__choices">
          {ROLES.map((item) => (
            <button key={item.id} type="button" aria-pressed={role === item.id}
              className={`autoos-v5-role ${role === item.id ? 'is-current' : ''}`}
              onClick={() => onChangeRole(item.id)}>
              <UserRoundCheck size={26}/><span><strong>{item.label}</strong><small>{item.description}</small></span>
              {role === item.id ? <Check size={20}/> : <ArrowRight size={20}/>}
            </button>
          ))}
        </div>
        <p className="autoos-v5-footnote">Cambio de perfil para la exposición, no inicio de sesión autenticado. Las restricciones funcionales continúan aplicándose en los módulos originales.</p>
      </section>
      <section className="autoos-v5-security__permissions">
        <div className="autoos-v5-section-heading"><div><p className="autoos-v5-eyebrow">02 · AUTORIZACIÓN</p><h3>¿QUÉ PUEDE HACER?</h3></div><span>{active.label}</span></div>
        <div className="autoos-v5-security__columns">
          <div><h4><ShieldCheck size={20}/> ACCIONES DISPONIBLES</h4><ul>{active.allowed.map((permission) => <li key={permission}><Check size={16}/>{permission}</li>)}</ul></div>
          <div><h4><LockKeyhole size={20}/> LÍMITES DEL PERFIL</h4>{active.restricted.length ? <ul>{active.restricted.map((permission) => <li key={permission}><LockKeyhole size={16}/>{permission}</li>)}</ul>
            : <p>El perfil técnico puede acceder a las operaciones de demostración disponibles.</p>}</div>
        </div>
      </section>
      <section className="autoos-v5-security__events">
        <div className="autoos-v5-section-heading"><div><p className="autoos-v5-eyebrow">03 · TRAZABILIDAD</p><h3>EVENTOS DE SIMULACIÓN</h3></div>
          <button type="button" className="autoos-v5-link" onClick={onOpenOriginalAudit}
            disabled={role !== 'mecanico'}
            title={role === 'mecanico' ? 'Abrir registros originales del Cockpit' : 'Solo el perfil Mecánico / Admin puede acceder a esta auditoría'}>
            {role === 'mecanico' ? 'VER AUDITORÍA DEL COCKPIT' : 'AUDITORÍA RESTRINGIDA AL ADMIN'} <ArrowRight size={18}/>
          </button></div>
        <p className="autoos-v5-footnote">Esta lista refleja los eventos de la sesión React. La auditoría de seguridad del Cockpit original se abre con el botón de arriba.</p>
        <label className="autoos-v5-search">BUSCAR EVENTOS
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Proceso, mensaje, prioridad..." aria-label="Filtrar eventos de simulación"/>
        </label>
        <div className="autoos-v5-eventlist" aria-live="polite">
          {filtered.length ? filtered.slice(0, 10).map((event) => <div key={event.id}>
            <span className={`autoos-v5-eventdot autoos-v5-eventdot--${event.severity}`}/>
            <strong>{event.type}</strong><span>{event.message}</span><small>{event.timestamp}</small>
          </div>) : <p>Sin eventos que coincidan. Inicia una simulación para generar registros.</p>}
        </div>
        <button className="autoos-v5-secondary" type="button" onClick={() => setShowExport((prev)=>!prev)}>
          <ClipboardCopy size={18}/>{showExport ? 'OCULTAR JSON' : 'VER / COPIAR JSON DE EVENTOS'}
        </button>
        {showExport && <div className="autoos-v5-export">
          <p>El JSON contiene solo los eventos visibles del simulador.</p>
          <textarea ref={exportArea} readOnly value={json} rows={7} aria-label="JSON exportable de los eventos"/>
          <button type="button" className="autoos-v5-secondary" onClick={()=>{ void copyJson(); }}>{copied ? <Check size={18}/> : <ClipboardCopy size={18}/>}{copied ? 'COPIADO' : 'COPIAR JSON'}</button>
        </div>}
      </section>
    </div>
  );
}
