/**
 * AUTOOS V4 · Explorador de subsistemas de Conducción.
 *
 * PROBLEMA QUE RESUELVE:
 * El cockpit heredado ofrece ocho tarjetas casi iguales y no explica su función.
 * Esta pantalla utiliza una lista de selección + un solo panel protagonista.
 *
 * ARQUITECTURA:
 * - Este componente NO toca el kernel, Supabase ni los sensores.
 * - onOpen(id) entrega a App.tsx qué herramienta quiere abrir el usuario.
 * - App.tsx dirige la petición al cockpit original mediante postMessage.
 * - El cockpit mantiene sus validaciones de rol y su lógica de negocio.
 *
 * DOCUMENTACIÓN PARA EXPONER:
 * "Primero elegimos QUÉ revisar, luego entramos en su herramienta real.
 *  El estado seleccionado es de presentación, no de telemetría".
 */
import React, { useState } from 'react';
import {
  ArrowRight, Activity, Camera, CarFront, ChevronRight, Cloud,
  Fan, Headphones, MessageSquare, Navigation, Radar, ShieldCheck,
} from 'lucide-react';
import type { UserRole } from '../types/scheduler';

export type CockpitFeatureId =
  | 'gps' | 'camera' | 'lidar' | 'network' | 'climate'
  | 'media' | 'chat' | 'security' | 'overview' | 'overview-original' | 'security-original';

type Feature = {
  id: Exclude<CockpitFeatureId, 'overview'>;
  number: string;
  title: string;
  tag: string;
  summary: string;
  expected: string;
  action: string;
  icon: typeof Navigation;
};

/** Datos de interfaz: textos educativos, no métricas simuladas. */
const FEATURES: readonly Feature[] = [
  {
    id: 'gps', number: '01', title: 'NAVEGACIÓN', tag: 'GPS Y RUTA',
    summary: 'Conoce la ubicación del vehículo, su recorrido, la precisión RTK y los satélites disponibles.',
    expected: 'Un mapa con trayectoria y datos de posición, velocidad y tiempo estimado.',
    action: 'ABRIR GPS', icon: Navigation,
  },
  {
    id: 'camera', number: '02', title: 'VISIÓN ADAS', tag: 'CÁMARAS',
    summary: 'Supervisa el entorno con la cámara frontal y comprueba los sistemas de asistencia.',
    expected: 'Vista de la cámara y avisos de la detección visual.',
    action: 'ABRIR CÁMARAS', icon: Camera,
  },
  {
    id: 'lidar', number: '03', title: 'SENSORES', tag: 'LiDAR Y RADAR',
    summary: 'Consulta cómo el vehículo detecta obstáculos y analiza objetos a su alrededor.',
    expected: 'Lecturas y diagnósticos de sensores de proximidad.',
    action: 'ABRIR SENSORES', icon: Radar,
  },
  {
    id: 'network', number: '04', title: 'CONEXIONES', tag: 'CAN-FD Y 5G',
    summary: 'Revisa la comunicación entre unidades electrónicas y la conectividad del vehículo.',
    expected: 'Estado de las comunicaciones, latencia y buses del sistema.',
    action: 'ABRIR CONEXIONES', icon: Cloud,
  },
  {
    id: 'climate', number: '05', title: 'CLIMATIZACIÓN', tag: 'HVAC',
    summary: 'Consulta y ajusta los parámetros de climatización de la cabina cuando tu rol lo permita.',
    expected: 'Temperaturas, zonas de cabina y controles de confort.',
    action: 'ABRIR CLIMA', icon: Fan,
  },
  {
    id: 'media', number: '06', title: 'MULTIMEDIA', tag: 'AUDIO Y SPOTIFY',
    summary: 'Accede al reproductor de la cabina y a las conexiones de audio disponibles.',
    expected: 'Controles multimedia y reproductor integrado.',
    action: 'ABRIR MULTIMEDIA', icon: Headphones,
  },
  {
    id: 'chat', number: '07', title: 'ASISTENTE', tag: 'CHAT DE CABINA',
    summary: 'Consulta las herramientas del asistente y sus funciones de apoyo al conductor.',
    expected: 'Panel de conversación y comandos disponibles.',
    action: 'ABRIR ASISTENTE', icon: MessageSquare,
  },
  {
    id: 'security', number: '08', title: 'SEGURIDAD', tag: 'PERFILES Y AUDITORÍA',
    summary: 'Comprende quién puede controlar el vehículo y cómo quedan registradas las acciones.',
    expected: 'Roles, permisos y registros de auditoría.',
    action: 'ABRIR SEGURIDAD', icon: ShieldCheck,
  },
];

interface CockpitExplorerProps {
  role: UserRole;
  onOpen: (feature: CockpitFeatureId) => void;
}

export function CockpitExplorerV4({ role, onOpen }: CockpitExplorerProps) {
  const [selectedId, setSelectedId] = useState<Feature['id']>('gps');
  const selected = FEATURES.find((feature) => feature.id === selectedId) ?? FEATURES[0];
  const SelectedIcon = selected.icon;

  return (
    <section className="autoos-explorer-v4" aria-label="Explorador de herramientas de conducción">
      {/* AUTOOS_V12_APLICADO: cabina técnica explicada sin alterar las lecturas. */}
      <header className="autoos-explorer-v4__heading">
        <div>
          <p className="autoos-explorer-v4__eyebrow">03 / CABINA Y TELEMETRÍA</p>
          <h2>CABINA Y <em>TELEMETRÍA</em></h2>
          <p>Controla y supervisa los subsistemas del vehículo inteligente. Selecciona una herramienta y consulta su funcionamiento técnico.</p>
        </div>
        <div className="autoos-explorer-v4__progress" aria-label="Ocho herramientas disponibles">
          <span>8 SISTEMAS</span><Activity size={22} aria-hidden="true" />
        </div>
      </header>

      <div className="autoos-v12-guide" aria-label="Función del módulo Cabina y Telemetría">
        <div><b>OBJETIVO</b><p>Monitorizar navegación, sensores, conectividad y confort de cabina.</p></div>
        <div><b>ENTRADAS</b><p>GPS, cámaras ADAS, LiDAR, CAN-FD, climatización y audio.</p></div>
        <div><b>SALIDAS</b><p>Diagnósticos, cambios autorizados y registros para auditoría.</p></div>
      </div>
      <div className="autoos-v12-howto"><strong>¿CÓMO SE USA?</strong><span>01 Selecciona</span><span>02 Consulta</span><span>03 Interactúa</span><span>04 Verifica recursos y eventos</span></div>
      <div className="autoos-explorer-v4__layout">
        <nav className="autoos-explorer-v4__navigation" aria-label="Seleccionar sistema del vehículo">
          {FEATURES.map((feature) => {
            const Icon = feature.icon;
            const current = selectedId === feature.id;
            return (
              <button key={feature.id} type="button"
                className={`autoos-explorer-v4__choice ${current ? 'is-active' : ''}`}
                aria-pressed={current}
                onClick={() => setSelectedId(feature.id)}>
                <span className="autoos-explorer-v4__number">{feature.number}</span>
                <Icon size={21} aria-hidden="true" />
                <span className="autoos-explorer-v4__choice-text">{feature.title}</span>
                <ChevronRight size={19} aria-hidden="true" />
              </button>
            );
          })}
        </nav>

        <article key={selected.id} className="autoos-explorer-v4__featured" aria-live="polite">
          <div className="autoos-explorer-v4__orbit" aria-hidden="true" />
          <div className="autoos-explorer-v4__heroicon" aria-hidden="true"><SelectedIcon strokeWidth={1} /></div>
          <p className="autoos-explorer-v4__numberline">SISTEMA {selected.number} <span>—</span> {selected.tag}</p>
          <h3>{selected.title}</h3>
          <div className="autoos-explorer-v4__description">
            <strong>¿PARA QUÉ SIRVE?</strong>
            <p>{selected.summary}</p>
          </div>
          <div className="autoos-explorer-v4__description">
            <strong>¿QUÉ VERÁS?</strong>
            <p>{selected.expected}</p>
          </div>
          <button type="button" className="autoos-explorer-v4__primary"
            onClick={() => onOpen(selected.id)}>
            {selected.action} <ArrowRight size={21} aria-hidden="true" />
          </button>
          <p className="autoos-explorer-v4__role">
            <ShieldCheck size={15} aria-hidden="true" />
            Perfil actual: {role === 'mecanico' ? 'Mecánico / Administrador' : role === 'conductor' ? 'Conductor' : 'Pasajero'}.
            Las herramientas conservan los permisos del sistema.
          </p>
        </article>
      </div>
      <footer className="autoos-explorer-v4__bottom">
        <div><CarFront size={19} aria-hidden="true" /> <span>EXPLORA SIN MODIFICAR EL VEHÍCULO</span></div>
        <button type="button" onClick={() => onOpen('overview')}>
          VER RESUMEN DE CONDUCCIÓN {/* AUTOOS_OVERVIEW_V5 */} <ArrowRight size={18} aria-hidden="true" />
        </button>
      </footer>
    </section>
  );
}
