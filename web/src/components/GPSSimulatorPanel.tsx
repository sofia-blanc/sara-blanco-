import React, { useState, useEffect, useRef } from 'react';
import {
  Navigation,
  Compass,
  MapPin,
  Play,
  Pause,
  RotateCcw,
  Radio,
  WifiOff,
  Signal,
  Gauge,
  BatteryCharging,
  Clock,
  Crosshair,
  AlertTriangle,
  ShieldAlert,
  ChevronRight,
  Route,
} from 'lucide-react';
import { UserRole } from '../types/scheduler';

interface GPSSimulatorPanelProps {
  isDeviceFailed?: boolean;
  activeDtc?: string | null;
  userRole: UserRole;
  onRoleRestricted: (action: string) => void;
  batteryLevel: number;
}

interface Waypoint {
  id: string;
  name: string;
  lat: number;
  lon: number;
  speedLimitKmh: number;
  description: string;
}

const PRESET_ROUTES: { id: string; name: string; description: string; waypoints: Waypoint[] }[] = [
  {
    id: 'route_urbana',
    name: 'Ruta 1: Campus Universitario → Centro Tecnológico',
    description: 'Circuito urbano con cruces semafóricos y cañones de edificios.',
    waypoints: [
      { id: 'w1', name: 'Plaza Central / Origen', lat: 4.6097, lon: -74.0817, speedLimitKmh: 30, description: 'Salida de cochera vehicular' },
      { id: 'w2', name: 'Av. Caracas / Calle 34', lat: 4.6240, lon: -74.0720, speedLimitKmh: 45, description: 'Intersección troncal' },
      { id: 'w3', name: 'Campus Universitario (Cra 30)', lat: 4.6385, lon: -74.0850, speedLimitKmh: 40, description: 'Acceso a laboratorios' },
      { id: 'w4', name: 'Parque Metropolitano', lat: 4.6550, lon: -74.0930, speedLimitKmh: 50, description: 'Vía arterial despejada' },
      { id: 'w5', name: 'Complejo Tecnológico / Destino', lat: 4.6850, lon: -74.0790, speedLimitKmh: 35, description: 'Estación de carga rápida' },
    ],
  },
  {
    id: 'route_autopista',
    name: 'Ruta 2: Corredor de Alta Velocidad (Autopista Norte)',
    description: 'Prueba de crucero autónomo y fusión radar/GNSS a 80-100 km/h.',
    waypoints: [
      { id: 'a1', name: 'Intercambiador Calle 100', lat: 4.6860, lon: -74.0560, speedLimitKmh: 60, description: 'Incorporación a carril rápido' },
      { id: 'a2', name: 'Paso Elevado Calle 134', lat: 4.7180, lon: -74.0480, speedLimitKmh: 80, description: 'Tramo recto ACC activo' },
      { id: 'a3', name: 'Portal Norte Calle 170', lat: 4.7550, lon: -74.0390, speedLimitKmh: 90, description: 'Navegación por carril L3' },
      { id: 'a4', name: 'Peaje Autopista Chía', lat: 4.8200, lon: -74.0320, speedLimitKmh: 40, description: 'Desaceleración y telepeaje' },
    ],
  },
  {
    id: 'route_tunel',
    name: 'Ruta 3: Tramo de Túneles y Montaña (Prueba Dead Reckoning)',
    description: 'Pérdida forzada de satélites para verificar la odometría inercial IMU.',
    waypoints: [
      { id: 't1', name: 'Portal Occidental', lat: 4.6400, lon: -74.1200, speedLimitKmh: 50, description: 'Entrada con cielo abierto' },
      { id: 't2', name: 'Boca Túnel de la Línea Este', lat: 4.6490, lon: -74.1350, speedLimitKmh: 60, description: 'Pérdida de señal GNSS' },
      { id: 't3', name: 'Cámara Subterránea Intermedia', lat: 4.6620, lon: -74.1480, speedLimitKmh: 55, description: 'Navegación 100% Inercial IMU' },
      { id: 't4', name: 'Salida Galería Valle Verde', lat: 4.6780, lon: -74.1620, speedLimitKmh: 45, description: 'Recuperación de señal RTK' },
    ],
  },
];

export const GPSSimulatorPanel: React.FC<GPSSimulatorPanelProps> = ({
  isDeviceFailed = false,
  activeDtc = null,
  userRole,
  onRoleRestricted,
  batteryLevel,
}) => {
  const [selectedRouteIdx, setSelectedRouteIdx] = useState(0);
  const currentRoute = PRESET_ROUTES[selectedRouteIdx];

  // Navigation simulation state
  const [isNavigating, setIsNavigating] = useState(true);
  const [speedMultiplier, setSpeedMultiplier] = useState<1 | 2 | 5>(1);
  const [currentWaypointIdx, setCurrentWaypointIdx] = useState(0);
  const [segmentProgress, setSegmentProgress] = useState(0.2); // 0 to 1 between waypoints
  const [signalMode, setSignalMode] = useState<'RTK' | 'DEGRADED' | 'TUNNEL'>('RTK');

  // Automatic signal degradation if in tunnel route or if hardware failure
  useEffect(() => {
    if (isDeviceFailed) {
      setSignalMode('TUNNEL');
    } else if (currentRoute.id === 'route_tunel' && currentWaypointIdx >= 1 && currentWaypointIdx <= 2) {
      setSignalMode('TUNNEL');
    } else if (signalMode === 'TUNNEL' && !isDeviceFailed && currentRoute.id !== 'route_tunel') {
      setSignalMode('RTK');
    }
  }, [isDeviceFailed, currentRoute.id, currentWaypointIdx]);

  // Simulation tick loop
  useEffect(() => {
    if (!isNavigating) return;

    const interval = setInterval(() => {
      setSegmentProgress((prev) => {
        const step = 0.08 * speedMultiplier;
        const next = prev + step;
        if (next >= 1) {
          // Advance to next waypoint
          setCurrentWaypointIdx((wIdx) => {
            if (wIdx < currentRoute.waypoints.length - 1) {
              return wIdx + 1;
            } else {
              // Loop back to start for continuous demonstration
              return 0;
            }
          });
          return 0;
        }
        return next;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isNavigating, speedMultiplier, currentRoute.waypoints.length]);

  // Calculate interpolated coordinates
  const pA = currentRoute.waypoints[currentWaypointIdx];
  const pB = currentRoute.waypoints[Math.min(currentWaypointIdx + 1, currentRoute.waypoints.length - 1)];
  const isLastPoint = currentWaypointIdx >= currentRoute.waypoints.length - 1;

  const currentLat = isLastPoint ? pA.lat : pA.lat + (pB.lat - pA.lat) * segmentProgress;
  const currentLon = isLastPoint ? pA.lon : pA.lon + (pB.lon - pA.lon) * segmentProgress;

  // Bearing / Heading angle calculation
  const dLat = (pB.lat - pA.lat);
  const dLon = (pB.lon - pA.lon);
  const headingRad = Math.atan2(dLon, dLat);
  let headingDeg = Math.round((headingRad * 180) / Math.PI);
  if (headingDeg < 0) headingDeg += 360;

  const getHeadingLabel = (deg: number) => {
    if (deg >= 337.5 || deg < 22.5) return 'N (Norte)';
    if (deg >= 22.5 && deg < 67.5) return 'NE (Noreste)';
    if (deg >= 67.5 && deg < 112.5) return 'E (Este)';
    if (deg >= 112.5 && deg < 157.5) return 'SE (Sureste)';
    if (deg >= 157.5 && deg < 202.5) return 'S (Sur)';
    if (deg >= 202.5 && deg < 247.5) return 'SO (Suroeste)';
    if (deg >= 247.5 && deg < 292.5) return 'O (Oeste)';
    return 'NO (Noroeste)';
  };

  // Speed calculation with jitter/realistic variation
  const baseSpeed = isLastPoint ? 0 : pA.speedLimitKmh;
  const currentSpeed = isNavigating ? Math.max(0, Math.round(baseSpeed * (0.85 + Math.sin(segmentProgress * Math.PI) * 0.25))) : 0;

  // Distance remaining
  const waypointsRemaining = currentRoute.waypoints.length - 1 - currentWaypointIdx;
  const distanceRemainingKm = Math.max(0.4, Number((waypointsRemaining * 2.8 + (1 - segmentProgress) * 2.8).toFixed(1)));
  const etaMinutes = currentSpeed > 0 ? Math.round((distanceRemainingKm / currentSpeed) * 60) : 0;

  // Satellite and HDOP metrics based on signal mode & failure
  let satellites = 18;
  let hdop = 0.7;
  let signalStatusText = 'Óptimo RTK Submétrica';
  let signalColorClass = 'text-emerald-500';

  if (isDeviceFailed) {
    satellites = 0;
    hdop = 99.9;
    signalStatusText = 'Falla de Hardware (DTC)';
    signalColorClass = 'text-red-500';
  } else if (signalMode === 'TUNNEL') {
    satellites = 0;
    hdop = 99.9;
    signalStatusText = 'Sin Señal (Dead Reckoning IMU)';
    signalColorClass = 'text-amber-500';
  } else if (signalMode === 'DEGRADED') {
    satellites = 7;
    hdop = 2.4;
    signalStatusText = 'Jitter Urbano (Deriva ±3m)';
    signalColorClass = 'text-yellow-500';
  }

  // Energy projection
  const estimatedKwhToArrival = Number((distanceRemainingKm * 0.16).toFixed(2));
  const estimatedArrivalSoc = Math.max(2, Math.round(batteryLevel - (estimatedKwhToArrival / 60) * 100));

  // Handle route change
  const handleRouteChange = (idx: number) => {
    setSelectedRouteIdx(idx);
    setCurrentWaypointIdx(0);
    setSegmentProgress(0);
  };

  const handleResetNavigation = () => {
    setCurrentWaypointIdx(0);
    setSegmentProgress(0);
  };

  return (
    <div className="autoos-card rounded-2xl p-5 shadow-xl space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[var(--border-color)]">
        <div className="flex items-center gap-2.5">
          <div className={`p-2 rounded-xl border ${
            isDeviceFailed
              ? 'bg-red-500/15 text-red-500 border-red-500/30 animate-pulse'
              : 'bg-[var(--accent-primary)]/15 text-[var(--accent-primary)] border-[var(--accent-primary)]/30'
          }`}>
            <Navigation className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-serif font-bold text-[var(--text-primary)] flex items-center gap-2">
              Simulador GNSS / GPS Dinámico en Tiempo Real
              {isDeviceFailed && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-red-600 text-white font-bold uppercase animate-pulse">
                  DTC: {activeDtc || 'U0100-87'}
                </span>
              )}
            </h3>
            <p className="text-[11px] text-[var(--text-muted)]">
              Cálculo cinemático de waypoints, odometría satelital, rumbo inercial y consumo energético proyectado
            </p>
          </div>
        </div>

        {/* Route Selector Dropdown */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-[11px] text-[var(--text-muted)] font-semibold hidden sm:inline">Ruta:</span>
          <select
            value={selectedRouteIdx}
            onChange={(e) => handleRouteChange(Number(e.target.value))}
            className="autoos-surface border border-[var(--border-color)] text-[var(--text-primary)] px-3 py-1.5 rounded-xl font-bold text-xs focus:outline-none cursor-pointer"
          >
            {PRESET_ROUTES.map((r, i) => (
              <option key={r.id} value={i} className="text-black dark:text-white dark:bg-[#180E24]">
                {r.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Device Failure Alert Banner */}
      {isDeviceFailed && (
        <div className="p-3 rounded-xl bg-red-500/15 border border-red-500/30 text-red-600 dark:text-red-400 text-xs font-mono flex items-center justify-between gap-3 animate-pulse">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 shrink-0 text-red-500" />
            <span>
              <strong>FALLA EN RECEPTOR GNSS (DEV_GPS_01):</strong> Pérdida total de trama NMEA. Conmutando automáticamente a estimación inercial por Giroscopio IMU y Odometría (Dead Reckoning).
            </span>
          </div>
          <span className="px-2 py-0.5 rounded bg-red-500 text-white font-bold text-[10px] shrink-0">
            ASIL-D FALLBACK
          </span>
        </div>
      )}

      {/* Live Telemetry Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 font-mono text-xs">
        {/* Coordinates */}
        <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
          <span className="text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold">
            <Crosshair className="w-3 h-3 text-[var(--accent-primary)]" /> Coordenadas WGS84
          </span>
          <strong className="text-xs text-[var(--text-primary)] block font-bold truncate">
            {currentLat.toFixed(4)}° N
          </strong>
          <strong className="text-xs text-[var(--text-primary)] block font-bold truncate">
            {currentLon.toFixed(4)}° O
          </strong>
        </div>

        {/* Speed */}
        <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
          <span className="text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold">
            <Gauge className="w-3 h-3 text-emerald-500" /> Velocidad Real
          </span>
          <strong className="text-lg text-emerald-600 dark:text-emerald-400 font-bold">
            {currentSpeed} <span className="text-xs font-normal">km/h</span>
          </strong>
          <span className="text-[10px] text-[var(--text-muted)] block">
            Límite: {isLastPoint ? 0 : pA.speedLimitKmh} km/h
          </span>
        </div>

        {/* Compass / Heading */}
        <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
          <span className="text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold">
            <Compass className="w-3 h-3 text-cyan-500" /> Rumbo / Brújula
          </span>
          <strong className="text-base text-cyan-600 dark:text-cyan-400 font-bold">
            {headingDeg}° {getHeadingLabel(headingDeg).split(' ')[0]}
          </strong>
          <span className="text-[10px] text-[var(--text-muted)] block truncate">
            {getHeadingLabel(headingDeg)}
          </span>
        </div>

        {/* Signal & Satellites */}
        <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
          <span className="text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold">
            <Signal className="w-3 h-3 text-amber-500" /> Satélites GNSS
          </span>
          <strong className={`text-base font-bold ${signalColorClass}`}>
            {satellites} sat / HDOP {hdop}
          </strong>
          <span className="text-[10px] text-[var(--text-muted)] block truncate">
            {signalStatusText}
          </span>
        </div>

        {/* Distance Remaining & ETA */}
        <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
          <span className="text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold">
            <Clock className="w-3 h-3 text-[var(--accent-primary)]" /> Distancia & ETA
          </span>
          <strong className="text-base text-[var(--text-primary)] font-bold">
            {distanceRemainingKm} km
          </strong>
          <span className="text-[10px] text-emerald-600 dark:text-emerald-400 block font-semibold">
            ETA: ~{etaMinutes} min
          </span>
        </div>

        {/* Projected Energy Consumption */}
        <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
          <span className="text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold">
            <BatteryCharging className="w-3 h-3 text-emerald-500" /> Proyección SoC
          </span>
          <strong className="text-base text-[var(--text-primary)] font-bold">
            {estimatedArrivalSoc}% <span className="text-[10px] font-normal text-[var(--text-muted)]">llegada</span>
          </strong>
          <span className="text-[10px] text-[var(--text-muted)] block">
            Gasto: ~{estimatedKwhToArrival} kWh
          </span>
        </div>
      </div>

      {/* Interactive Vector Map and Route Trajectory Canvas */}
      <div className="relative autoos-surface rounded-2xl border border-[var(--border-color)] overflow-hidden p-4">
        {/* Top Overlay Badge */}
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2 text-xs font-mono">
            <Route className="w-4 h-4 text-[var(--accent-primary)]" />
            <span className="font-bold text-[var(--text-primary)]">
              {currentRoute.name}
            </span>
            <span className="text-[11px] text-[var(--text-muted)]">
              ({currentRoute.waypoints.length} waypoints)
            </span>
          </div>

          <div className="flex items-center gap-2 text-xs font-mono">
            <span className="text-[11px] text-[var(--text-muted)]">Simulación de Señal:</span>
            <div className="flex items-center gap-1 autoos-card p-0.5 rounded-lg border text-[10px]">
              <button
                onClick={() => setSignalMode('RTK')}
                disabled={isDeviceFailed}
                className={`px-2 py-0.5 rounded transition ${
                  signalMode === 'RTK' && !isDeviceFailed
                    ? 'bg-emerald-600 text-white font-bold'
                    : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                }`}
              >
                🛰️ RTK Óptima
              </button>
              <button
                onClick={() => setSignalMode('DEGRADED')}
                disabled={isDeviceFailed}
                className={`px-2 py-0.5 rounded transition ${
                  signalMode === 'DEGRADED' && !isDeviceFailed
                    ? 'bg-yellow-600 text-white font-bold'
                    : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                }`}
              >
                🏢 Jitter Urbano
              </button>
              <button
                onClick={() => setSignalMode('TUNNEL')}
                className={`px-2 py-0.5 rounded transition ${
                  signalMode === 'TUNNEL' || isDeviceFailed
                    ? 'bg-red-600 text-white font-bold'
                    : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                }`}
              >
                🚇 Túnel (IMU)
              </button>
            </div>
          </div>
        </div>

        {/* Vector SVG Visualizer */}
        <div className="relative w-full h-56 rounded-xl bg-slate-900 border border-slate-800 overflow-hidden shadow-inner flex items-center justify-center">
          {/* Subtle Grid Lines */}
          <div className="absolute inset-0 opacity-15 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>

          <svg className="w-full h-full" viewBox="0 0 800 240" preserveAspectRatio="none">
            <defs>
              <linearGradient id="routeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#8b5cf6" />
                <stop offset="50%" stopColor="#06b6d4" />
                <stop offset="100%" stopColor="#10b981" />
              </linearGradient>
              <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="glow" />
                <feComposite in="SourceGraphic" in2="glow" operator="over" />
              </filter>
            </defs>

            {/* Base Route Path (dashed road) */}
            {(() => {
              const numPoints = currentRoute.waypoints.length;
              const points = currentRoute.waypoints.map((wp, idx) => {
                const x = 70 + (idx / (numPoints - 1)) * 660;
                // Add natural curve variations
                const y = 120 + Math.sin(idx * 1.5) * 45;
                return { x, y, wp };
              });

              // Generate path string
              let pathStr = `M ${points[0].x} ${points[0].y}`;
              for (let i = 1; i < points.length; i++) {
                const prev = points[i - 1];
                const curr = points[i];
                const midX = (prev.x + curr.x) / 2;
                pathStr += ` C ${midX} ${prev.y}, ${midX} ${curr.y}, ${curr.x} ${curr.y}`;
              }

              // Calculate current vehicle position on SVG path
              const currSegIdx = currentWaypointIdx;
              const nextSegIdx = Math.min(currentWaypointIdx + 1, numPoints - 1);
              const pCurrent = points[currSegIdx];
              const pNext = points[nextSegIdx];
              const carX = pCurrent.x + (pNext.x - pCurrent.x) * segmentProgress;
              const carY = pCurrent.y + (pNext.y - pCurrent.y) * segmentProgress;

              return (
                <>
                  {/* Road Asphalt Layer */}
                  <path
                    d={pathStr}
                    fill="none"
                    stroke="#1e293b"
                    strokeWidth="18"
                    strokeLinecap="round"
                  />
                  {/* Road Center Line */}
                  <path
                    d={pathStr}
                    fill="none"
                    stroke="#475569"
                    strokeWidth="2"
                    strokeDasharray="6 6"
                  />
                  {/* Active Illuminated Route */}
                  <path
                    d={pathStr}
                    fill="none"
                    stroke="url(#routeGradient)"
                    strokeWidth="4"
                    strokeLinecap="round"
                    filter="url(#glow)"
                  />

                  {/* Waypoint Markers */}
                  {points.map((p, idx) => {
                    const isPassed = idx < currentWaypointIdx;
                    const isCurrent = idx === currentWaypointIdx;

                    return (
                      <g key={p.wp.id} className="transition-all duration-300">
                        {/* Outer Ring */}
                        <circle
                          cx={p.x}
                          cy={p.y}
                          r={isCurrent ? 12 : 7}
                          fill={isPassed ? '#10b981' : isCurrent ? '#06b6d4' : '#334155'}
                          fillOpacity={isCurrent ? 0.3 : 0.8}
                          stroke={isCurrent ? '#06b6d4' : '#64748b'}
                          strokeWidth="2"
                        />
                        {/* Center Dot */}
                        <circle
                          cx={p.x}
                          cy={p.y}
                          r={isCurrent ? 6 : 4}
                          fill={isPassed ? '#10b981' : isCurrent ? '#ffffff' : '#94a3b8'}
                        />
                        {/* Waypoint Label */}
                        <text
                          x={p.x}
                          y={p.y - 18}
                          textAnchor="middle"
                          fill="#e2e8f0"
                          fontSize="10"
                          fontWeight="bold"
                          fontFamily="monospace"
                        >
                          {p.wp.name.split('/')[0]}
                        </text>
                      </g>
                    );
                  })}

                  {/* Moving Vehicle Indicator with Direction Triangle */}
                  <g transform={`translate(${carX}, ${carY})`} className="transition-transform duration-100">
                    {/* Pulse wave */}
                    <circle
                      r="22"
                      fill={isDeviceFailed ? '#ef4444' : '#06b6d4'}
                      fillOpacity="0.25"
                      className="animate-ping"
                    />
                    {/* Vehicle Base Bubble */}
                    <circle
                      r="12"
                      fill={isDeviceFailed ? '#ef4444' : '#06b6d4'}
                      stroke="#ffffff"
                      strokeWidth="2.5"
                      filter="url(#glow)"
                    />
                    {/* Direction arrow */}
                    <polygon
                      points="0,-8 6,6 -6,6"
                      fill="#ffffff"
                      transform={`rotate(${headingDeg})`}
                    />
                  </g>
                </>
              );
            })()}
          </svg>

          {/* Real-time Overlay HUD inside map */}
          <div className="absolute bottom-2 left-3 right-3 flex items-center justify-between text-[11px] font-mono text-slate-300 bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700">
            <span className="flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-cyan-400" />
              <span>Siguiente: <strong>{pB.name}</strong> ({pB.description})</span>
            </span>
            <span className="text-cyan-400 font-bold">
              {Math.round(segmentProgress * 100)}% tramo completado
            </span>
          </div>
        </div>

        {/* Waypoint Sequence Progress Bar */}
        <div className="mt-3 flex items-center justify-between gap-1 overflow-x-auto py-1">
          {currentRoute.waypoints.map((wp, idx) => {
            const isDone = idx < currentWaypointIdx;
            const isCurrent = idx === currentWaypointIdx;

            return (
              <div
                key={wp.id}
                className={`flex-1 min-w-[130px] p-2 rounded-xl border text-xs font-mono transition ${
                  isCurrent
                    ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/10 text-[var(--text-primary)] ring-1 ring-[var(--accent-primary)]/30'
                    : isDone
                    ? 'border-emerald-500/30 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400'
                    : 'autoos-card opacity-60 text-[var(--text-muted)]'
                }`}
              >
                <div className="flex items-center justify-between text-[10px] font-bold">
                  <span>Punto {idx + 1}</span>
                  {isDone ? (
                    <span className="text-emerald-500">✓ Pasado</span>
                  ) : isCurrent ? (
                    <span className="text-[var(--accent-primary)] animate-pulse">● En Ruta</span>
                  ) : (
                    <span>Pendiente</span>
                  )}
                </div>
                <div className="font-bold text-[11px] truncate mt-0.5">{wp.name}</div>
                <div className="text-[9px] text-[var(--text-muted)] truncate">{wp.speedLimitKmh} km/h máx</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Control Action Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-[var(--border-color)]">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsNavigating(!isNavigating)}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold font-mono flex items-center gap-1.5 transition shadow-sm ${
              isNavigating
                ? 'bg-amber-500 hover:bg-amber-400 text-white'
                : 'bg-emerald-600 hover:bg-emerald-500 text-white'
            }`}
          >
            {isNavigating ? <Pause className="w-3.5 h-3.5 fill-current" /> : <Play className="w-3.5 h-3.5 fill-current" />}
            <span>{isNavigating ? 'Pausar Simulación GPS' : 'Reanudar Navegación'}</span>
          </button>

          <button
            onClick={handleResetNavigation}
            className="px-3 py-2 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-muted)] hover:text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold flex items-center gap-1.5 transition font-mono"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reiniciar al Origen</span>
          </button>
        </div>

        {/* Speed Multipliers */}
        <div className="flex items-center gap-1.5 autoos-surface p-1 rounded-xl text-xs font-mono">
          <span className="text-[10px] text-[var(--text-muted)] px-1 font-bold">Velocidad:</span>
          {([1, 2, 5] as const).map((m) => (
            <button
              key={m}
              onClick={() => setSpeedMultiplier(m)}
              className={`px-2.5 py-1 rounded-lg font-bold transition ${
                speedMultiplier === m
                  ? 'bg-[var(--accent-primary)] text-white shadow-sm'
                  : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
              }`}
            >
              {m}x
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
