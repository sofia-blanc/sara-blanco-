import React from 'react';
import { Activity, BatteryCharging, Cpu, HardDrive, Layers, MemoryStick, Zap } from 'lucide-react';
import { SIM_RAM_MB, type OSResourceSample, type OSResourceSnapshot } from '../simulation/resources';

/**
 * Instrumento compartido entre Simulación, Planificador y Conducción.
 * Recibe únicamente datos del motor de App.tsx: NO crea contadores ficticios.
 * La prop compact permite una lectura rápida sin duplicar una fuente de estado.
 */
export function OSResourceMonitor({ snapshot, history, compact = false, onOpenScheduler }: {
  snapshot: OSResourceSnapshot;
  history: OSResourceSample[];
  compact?: boolean;
  onOpenScheduler?: () => void;
}) {
  const num = (n: number) => Math.round(n).toLocaleString('es-CO');
  const cards = [
    { icon: <Cpu size={19} />, label: 'Demanda de CPU', value: `${num(snapshot.cpuDemandPct)} %`, detail: `CPU ejecutada ${num(snapshot.cpuBusyPct)} % · PID ${snapshot.cpuExecutingPid ?? '—'}`, pct: Math.min(100, snapshot.cpuDemandPct), tone: 'cyan' },
    { icon: <MemoryStick size={19} />, label: 'RAM física', value: `${num(snapshot.ramPhysicalMb)} / ${num(SIM_RAM_MB)} MB`, detail: `Libres ${num(snapshot.ramFreeMb)} MB · SWAP ${num(snapshot.swapRequestedMb)} MB`, pct: snapshot.memoryPressurePct, tone: snapshot.swapRequestedMb ? 'orange' : 'cyan' },
    { icon: <BatteryCharging size={19} />, label: 'Batería del vehículo', value: `${snapshot.batteryPct.toFixed(2)} %`, detail: `Descarga ${snapshot.drainPctPerTick.toFixed(2)} puntos/min virtual`, pct: snapshot.batteryPct, tone: snapshot.batteryPct < 20 ? 'orange' : 'green' },
    { icon: <Zap size={19} />, label: 'Potencia estimada', value: `${(snapshot.totalPowerW / 1000).toFixed(2)} kW`, detail: `Energía del viaje ${num(snapshot.consumedWh)} Wh`, pct: Math.min(100, snapshot.totalPowerW / 160), tone: 'pink' },
  ];

  return (
    <section className={`autoos-osmon ${compact ? 'autoos-osmon--compact' : ''}`} aria-label="Monitor de recursos de AutoOS">
      <div className="autoos-osmon__head">
        <div>
          <span className="autoos-osmon__eyebrow"><Activity size={14} /> NÚCLEO DE LA SIMULACIÓN · DATOS COMPARTIDOS</span>
          <h3>{compact ? 'RECURSOS DEL SO' : 'QUÉ ESTÁ CONSUMIENDO AUTOOS'}</h3>
          {!compact && <p>Una sola sesión controla Planificador, Conducción y Simulación. Los valores pertenecen al motor didáctico React.</p>}
        </div>
        {onOpenScheduler && <button className="autoos-osmon__link" onClick={onOpenScheduler} type="button">VER PLANIFICADOR ↗</button>}
      </div>
      <div className="autoos-osmon__metrics">
        {cards.map(card => (
          <article key={card.label} className={`autoos-osmon__metric autoos-osmon__metric--${card.tone}`}>
            <div className="autoos-osmon__metriclabel">{card.icon}<span>{card.label}</span></div>
            <div className="autoos-osmon__value">{card.value}</div>
            <div className="autoos-osmon__bar" role="progressbar" aria-label={card.label} aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round(card.pct)}>
              <span style={{ width: `${card.pct}%` }}/>
            </div>
            <p>{card.detail}</p>
          </article>
        ))}
      </div>
      {!compact && <div className="autoos-osmon__details">
        <div className="autoos-osmon__processes">
          <h4><Layers size={15}/> PROCESOS Y MEMORIA</h4>
          <div className="autoos-osmon__counts"><span>{snapshot.admittedCount} admitidos</span><span>{snapshot.readyCount} listos</span><span>{snapshot.suspendedCount} suspendidos</span><span>{snapshot.completedCount} terminados</span></div>
          <div className="autoos-osmon__processlist">
            {snapshot.processes.length === 0 ? <p>Sin procesos admitidos. Inicia un escenario para ver las reservas.</p> :
              snapshot.processes.slice(0, 9).map(proc => (
                <div className="autoos-osmon__process" key={proc.pid}>
                  <b>#{proc.pid}</b>
                  <span title={proc.name}>{proc.name}</span>
                  <small>{proc.state}</small>
                  <strong>{num(proc.memoryMb)} MB</strong>
                  <small>{proc.powerW} W</small>
                </div>
              ))}
          </div>
          <div className="autoos-osmon__power">
            <span><Zap size={14}/> Tracción: {num(snapshot.tractionPowerW)} W</span>
            <span><Cpu size={14}/> SO: {num(snapshot.osPowerW)} W</span>
            <span><HardDrive size={14}/> Dispositivos: {num(snapshot.devicePowerW)} W</span>
          </div>
        </div>
        <div className="autoos-osmon__timeline">
          <h4><Activity size={15}/> EVOLUCIÓN POR TICK</h4>
          <ResourceTrend history={history} />
          <p>Gráfico de RAM (azul), demanda CPU (rosa) y batería (verde). Cada tick de conducción representa 1 minuto virtual.</p>
          <p>RAM/SWAP: estimación del laboratorio; el asignador First-Fit del kernel Python permanece independiente.</p>
        </div>
      </div>}
    </section>
  );
}

function ResourceTrend({ history }: {history: OSResourceSample[]}) {
  // Un solo gráfico con tres series normalizadas a porcentaje. Sin dependencias externas.
  const samples = history.slice(-50);
  const points = (fn: (s: OSResourceSample) => number) => samples.map((s, i) => {
    const x = samples.length <= 1 ? 10 : 10 + 380 * i / (samples.length - 1);
    const y = 112 - Math.max(0, Math.min(100, fn(s))) * .95;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');
  return <svg className="autoos-osmon__chart" viewBox="0 0 400 125" role="img" aria-label="Tendencias de RAM, demanda CPU y batería por tick">
    {[17, 64, 112].map(y => <line key={y} x1="10" x2="390" y1={y} y2={y} stroke="currentColor" opacity=".17" strokeDasharray="4 6" />)}
    <polyline points={points(s=> s.ramPhysicalMb / SIM_RAM_MB * 100)} fill="none" stroke="#42d8ff" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
    <polyline points={points(s=> s.cpuDemandPct)} fill="none" stroke="#ff5aab" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
    <polyline points={points(s=> s.batteryPct)} fill="none" stroke="#1fcb92" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
    <text x="10" y="10" fontSize="10" fill="currentColor" opacity=".7">100%</text>
    <text x="10" y="123" fontSize="10" fill="currentColor" opacity=".7">0</text>
    <text x="365" y="123" fontSize="10" fill="currentColor" opacity=".7">{samples.length ? `t${samples[samples.length-1].tick}` : 't0'}</text>
  </svg>;
}
