/**
 * AutoOS V6 — Lienzo contextual para herramientas reales del Cockpit.
 *
 * POR QUÉ EXISTE
 * El Cockpit antiguo es una página completa dentro de un iframe. Abrirlo sin
 * contexto devolvía al usuario un dashboard con pestañas diminutas.
 *
 * QUÉ HACE
 * 1. Mantiene siempre a la vista el nombre, objetivo y pasos de la herramienta.
 * 2. Permite cambiar de herramienta con un menú propio, legible y animado.
 * 3. Presenta debajo el iframe REAL, sin duplicar ni inventar sus funciones.
 *
 * QUÉ NO HACE
 * No crea métricas ni permisos; App.tsx conserva el estado, y el Cockpit
 * heredado sigue validando las operaciones sensibles.
 */
import React from 'react';
import {
  ArrowLeft, ArrowRight, Camera, Cloud, Fan, Headphones, LockKeyhole,
  MessageSquare, Navigation, Radar, ShieldCheck,
} from 'lucide-react';
import type { UserRole } from '../types/scheduler';
import type { CockpitFeatureId } from './CockpitExplorerV4';

const TOOLS = [
  { id: 'gps', number: '01', name: 'GPS Y RUTA', subtitle: 'Navegación satelital',
    purpose: 'Consulta la posición, la ruta y la calidad de señal GNSS/RTK.',
    instruction: 'Comprueba satélites y coordenadas; después explora el trazado de la ruta.', icon: Navigation },
  { id: 'camera', number: '02', name: 'CÁMARA ADAS', subtitle: 'Visión y asistencia',
    purpose: 'Observa cómo la cámara frontal contribuye a detectar el entorno.',
    instruction: 'Revisa la imagen y las alertas de visión antes de interpretar su estado.', icon: Camera },
  { id: 'lidar', number: '03', name: 'LIDAR Y RADAR', subtitle: 'Percepción del entorno',
    purpose: 'Consulta la lectura de los sensores de proximidad del vehículo.',
    instruction: 'Selecciona el sensor y compara distancia, objetos y alertas.', icon: Radar },
  { id: 'network', number: '04', name: 'COMUNICACIONES', subtitle: 'Bus CAN-FD y 5G',
    purpose: 'Supervisa el intercambio de información entre subsistemas.',
    instruction: 'Verifica el estado del enlace y la latencia de los dispositivos.', icon: Cloud },
  { id: 'climate', number: '05', name: 'CLIMATIZACIÓN', subtitle: 'Confort de cabina',
    purpose: 'Revisa la temperatura y las opciones de climatización.',
    instruction: 'Consulta las zonas y ajusta el clima si tu perfil lo permite.', icon: Fan },
  { id: 'media', number: '06', name: 'MULTIMEDIA', subtitle: 'Audio y conexiones',
    purpose: 'Controla las opciones del reproductor integrado y la conectividad.',
    instruction: 'Abre el reproductor; recuerda que Spotify tiene su propio control de reproducción.', icon: Headphones },
  { id: 'chat', number: '07', name: 'ASISTENTE', subtitle: 'Chat de cabina',
    purpose: 'Utiliza el asistente de información del vehículo.',
    instruction: 'Introduce una consulta y revisa la respuesta del asistente.', icon: MessageSquare },
  { id: 'security-original', number: '08', name: 'AUDITORÍA ORIGINAL', subtitle: 'Seguridad del Cockpit',
    purpose: 'Consulta los registros propios del Cockpit original.',
    instruction: 'Revisa los eventos del sistema respetando el perfil activo.', icon: LockKeyhole },
] as const;

type ToolId = typeof TOOLS[number]['id'];
type Props = {
  feature: CockpitFeatureId;
  role: UserRole;
  onFeature: (next: CockpitFeatureId) => void;
  onBack: () => void;
  children: React.ReactNode;
};

export function CockpitToolSceneV6({ feature, role, onFeature, onBack, children }: Props) {
  const selected = TOOLS.find((tool) => tool.id === feature) ?? TOOLS[0];
  const Icon = selected.icon;
  const isRestricted = (id: ToolId) => (id === 'security-original' && role !== 'admin') || (role === 'pasajero' && !['media','chat','climate'].includes(id));

  return (
    <section className="autoos-v6-tool" aria-label={`Herramienta ${selected.name}`}>
      <div className="autoos-v6-tool__top">
        <div>
          <p className="autoos-v6-tool__eyebrow">AUTOOS · CABINA Y TELEMETRÍA · HERRAMIENTA {selected.number}</p>
          <h2>{selected.name}<span aria-hidden="true">/</span></h2>
          <p className="autoos-v6-tool__subtitle">{selected.subtitle} — {selected.purpose}</p>
        </div>
        <button className="autoos-v6-tool__back" type="button" onClick={onBack}>
          <ArrowLeft size={18}/> EXPLORAR OTRO SISTEMA
        </button>
      </div>
      <div className="autoos-v6-tool__body">
        <nav className="autoos-v6-tool__nav" aria-label="Herramientas del vehículo">
          <p>SELECCIONA UNA FUNCIÓN</p>
          {TOOLS.filter((tool) => !isRestricted(tool.id)).map((tool) => {
            const active = feature === tool.id;
            const NavIcon = tool.icon;
            return <button type="button" key={tool.id}
              className={active ? 'is-active' : ''}
              aria-current={active ? 'page' : undefined}
              onClick={() => onFeature(tool.id)}>
              <span>{tool.number}</span><NavIcon size={18} aria-hidden="true"/>
              <strong>{tool.name}</strong><ArrowRight size={16} aria-hidden="true"/>
            </button>;
          })}
          <button type="button" className="autoos-v6-tool__to-overview" onClick={() => onFeature('overview')}>
            <ShieldCheck size={18}/> VOLVER AL RESUMEN
          </button>
        </nav>
        <div className="autoos-v6-tool__main">
          <div className="autoos-v6-tool__instruction">
            <div className="autoos-v6-tool__illustration"><Icon size={32} strokeWidth={1.6}/></div>
            <div>
              <b>¿QUÉ DEBES HACER AQUÍ?</b>
              <p>{selected.instruction}</p>
              <small>Instrumento técnico integrado. Sus métricas propias pueden diferir de la simulación educativa de recursos React.</small>
            </div>
          </div>
          <div className="autoos-v6-tool__instrument">
            <div className="autoos-v6-tool__instrument-title">
              <span className="autoos-v6-tool__pulse" aria-hidden="true"/>
              INSTRUMENTO ACTIVO · {selected.name} {/* AUTOOS_V12_APLICADO */}
              <span className="autoos-v6-tool__engine">MOTOR ORIGINAL</span>
            </div>
            {children}
          </div>
        </div>
      </div>
    </section>
  );
}

// AUTOOS_V15_APLICADO — Administrador tiene acceso técnico; backend independiente.
