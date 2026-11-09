import React, { useState, useEffect } from 'react';
import {
  Navigation,
  Compass,
  MapPin,
  Play,
  Pause,
  RotateCcw,
  Signal,
  Gauge,
  BatteryCharging,
  Clock,
  Crosshair,
  ShieldAlert,
  Route,
  Plus,
  Trash2,
  PenLine,
  CheckCircle,
  Zap,
  Timer,
  ChevronDown,
  ChevronUp,
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

interface RouteDefinition {
  id: string;
  name: string;
  description: string;
  waypoints: Waypoint[];
}

// ─── Haversine distance (km) ────────────────────────────────────────────────
function haversineKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function totalRouteKm(waypoints: Waypoint[]): number {
  let dist = 0;
  for (let i = 0; i < waypoints.length - 1; i++) {
    dist += haversineKm(waypoints[i].lat, waypoints[i].lon, waypoints[i + 1].lat, waypoints[i + 1].lon);
  }
  return dist;
}

/** kWh consumed for a segment at given speed (km/h). ~160 Wh/km base + speed factor */
function segmentEnergyKwh(distKm: number, speedKmh: number): number {
  const efficiencyWhPerKm = 150 + speedKmh * 0.5; // higher speed → less efficient
  return (distKm * efficiencyWhPerKm) / 1000;
}

// ─── Preset routes ────────────────────────────────────────────────────────────
const PRESET_ROUTES: RouteDefinition[] = [
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
    name: 'Ruta 3: Tramo de Túneles y Montaña (Dead Reckoning)',
    description: 'Pérdida forzada de satélites para verificar la odometría inercial IMU.',
    waypoints: [
      { id: 't1', name: 'Portal Occidental', lat: 4.6400, lon: -74.1200, speedLimitKmh: 50, description: 'Entrada con cielo abierto' },
      { id: 't2', name: 'Boca Túnel de la Línea Este', lat: 4.6490, lon: -74.1350, speedLimitKmh: 60, description: 'Pérdida de señal GNSS' },
      { id: 't3', name: 'Cámara Subterránea Intermedia', lat: 4.6620, lon: -74.1480, speedLimitKmh: 55, description: 'Navegación 100% Inercial IMU' },
      { id: 't4', name: 'Salida Galería Valle Verde', lat: 4.6780, lon: -74.1620, speedLimitKmh: 45, description: 'Recuperación de señal RTK' },
    ],
  },
  {
    id: 'route_custom',
    name: '✏️ Ruta Personalizada',
    description: 'Define tus propios waypoints con coordenadas y velocidad.',
    waypoints: [
      { id: 'c1', name: 'Punto de Inicio', lat: 4.6097, lon: -74.0817, speedLimitKmh: 40, description: 'Inicio personalizado' },
      { id: 'c2', name: 'Punto de Llegada', lat: 4.6500, lon: -74.0700, speedLimitKmh: 50, description: 'Destino personalizado' },
    ],
  },
];

const genId = () => `wp_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;

/** Battery pack capacity in kWh (assumed 60 kWh for the vehicle) */
const BATTERY_CAPACITY_KWH = 60;

export const GPSSimulatorPanel: React.FC<GPSSimulatorPanelProps> = ({
  isDeviceFailed = false,
  activeDtc = null,
  userRole,
  onRoleRestricted,
  batteryLevel,
}) => {
  const [selectedRouteIdx, setSelectedRouteIdx] = useState(0);
  const [routes, setRoutes] = useState<RouteDefinition[]>(PRESET_ROUTES);
  const [showRouteEditor, setShowRouteEditor] = useState(false);

  // Editing state for custom route
  const [editWaypoints, setEditWaypoints] = useState<Waypoint[]>(PRESET_ROUTES[3].waypoints);

  // Navigation sim state
  const [isNavigating, setIsNavigating] = useState(true);
  const [speedMultiplier, setSpeedMultiplier] = useState<1 | 2 | 5>(1);
  const [currentWaypointIdx, setCurrentWaypointIdx] = useState(0);
  const [segmentProgress, setSegmentProgress] = useState(0.2);
  const [signalMode, setSignalMode] = useState<'RTK' | 'DEGRADED' | 'TUNNEL'>('RTK');

  const currentRoute = routes[selectedRouteIdx];

  // Auto signal degradation for tunnel route or hardware failure
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
          setCurrentWaypointIdx((wIdx) => {
            if (wIdx < currentRoute.waypoints.length - 1) return wIdx + 1;
            return 0;
          });
          return 0;
        }
        return next;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [isNavigating, speedMultiplier, currentRoute.waypoints.length]);

  // ─── Computed telemetry ───────────────────────────────────────────────────
  const pA = currentRoute.waypoints[currentWaypointIdx];
  const pB = currentRoute.waypoints[Math.min(currentWaypointIdx + 1, currentRoute.waypoints.length - 1)];
  const isLastPoint = currentWaypointIdx >= currentRoute.waypoints.length - 1;

  const currentLat = isLastPoint ? pA.lat : pA.lat + (pB.lat - pA.lat) * segmentProgress;
  const currentLon = isLastPoint ? pA.lon : pA.lon + (pB.lon - pA.lon) * segmentProgress;

  const dLat = pB.lat - pA.lat;
  const dLon = pB.lon - pA.lon;
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

  const baseSpeed = isLastPoint ? 0 : pA.speedLimitKmh;
  const currentSpeed = isNavigating
    ? Math.max(0, Math.round(baseSpeed * (0.85 + Math.sin(segmentProgress * Math.PI) * 0.25)))
    : 0;

  // Distance & ETA using real haversine
  const totalDistKm = totalRouteKm(currentRoute.waypoints);
  const coveredDistKm = (() => {
    let d = 0;
    for (let i = 0; i < currentWaypointIdx; i++) {
      d += haversineKm(
        currentRoute.waypoints[i].lat, currentRoute.waypoints[i].lon,
        currentRoute.waypoints[i + 1].lat, currentRoute.waypoints[i + 1].lon
      );
    }
    if (!isLastPoint) {
      const segDist = haversineKm(pA.lat, pA.lon, pB.lat, pB.lon);
      d += segDist * segmentProgress;
    }
    return d;
  })();
  const distanceRemainingKm = Math.max(0, Number((totalDistKm - coveredDistKm).toFixed(2)));
  const avgSpeedKmh = currentRoute.waypoints.reduce((s, w) => s + w.speedLimitKmh, 0) / currentRoute.waypoints.length;
  const etaMinutes = currentSpeed > 0 ? Math.round((distanceRemainingKm / avgSpeedKmh) * 60) : 0;

  // Energy projection using real distances and speeds
  const totalEnergyKwh = (() => {
    let e = 0;
    for (let i = 0; i < currentRoute.waypoints.length - 1; i++) {
      const d = haversineKm(
        currentRoute.waypoints[i].lat, currentRoute.waypoints[i].lon,
        currentRoute.waypoints[i + 1].lat, currentRoute.waypoints[i + 1].lon
      );
      e += segmentEnergyKwh(d, currentRoute.waypoints[i].speedLimitKmh);
    }
    return e;
  })();

  const remainingEnergyKwh = (() => {
    let e = 0;
    for (let i = currentWaypointIdx; i < currentRoute.waypoints.length - 1; i++) {
      const d = haversineKm(
        currentRoute.waypoints[i].lat, currentRoute.waypoints[i].lon,
        currentRoute.waypoints[i + 1].lat, currentRoute.waypoints[i + 1].lon
      );
      e += segmentEnergyKwh(d, currentRoute.waypoints[i].speedLimitKmh);
    }
    // Partial segment
    if (!isLastPoint) {
      const segDist = haversineKm(pA.lat, pA.lon, pB.lat, pB.lon);
      const segE = segmentEnergyKwh(segDist * (1 - segmentProgress), pA.speedLimitKmh);
      e = e - segmentEnergyKwh(haversineKm(pA.lat, pA.lon, pB.lat, pB.lon), pA.speedLimitKmh) + segE;
    }
    return Math.max(0, Number(e.toFixed(2)));
  })();

  // Battery capacity in kWh: assume 60 kWh full pack

  const availableKwh = (batteryLevel / 100) * BATTERY_CAPACITY_KWH;
  const estimatedArrivalSoc = Math.max(
    0,
    Math.round(((availableKwh - remainingEnergyKwh) / BATTERY_CAPACITY_KWH) * 100)
  );
  const canReachDestination = availableKwh >= remainingEnergyKwh;

  // Signal metrics
  let satellites = 18;
  let hdop = 0.7;
  let signalStatusText = 'Óptimo RTK Submétrica';
  let signalColorClass = 'text-emerald-500';
  if (isDeviceFailed) { satellites = 0; hdop = 99.9; signalStatusText = 'Falla HW (DTC)'; signalColorClass = 'text-red-500'; }
  else if (signalMode === 'TUNNEL') { satellites = 0; hdop = 99.9; signalStatusText = 'Dead Reckoning IMU'; signalColorClass = 'text-amber-500'; }
  else if (signalMode === 'DEGRADED') { satellites = 7; hdop = 2.4; signalStatusText = 'Jitter Urbano (±3m)'; signalColorClass = 'text-yellow-500'; }

  // ─── Route editor handlers ────────────────────────────────────────────────
  const handleRouteChange = (idx: number) => {
    setSelectedRouteIdx(idx);
    setCurrentWaypointIdx(0);
    setSegmentProgress(0);
    setShowRouteEditor(idx === 3); // auto-open editor for custom route
  };

  const handleWaypointChange = (idx: number, field: keyof Waypoint, value: string | number) => {
    setEditWaypoints((prev) => {
      const updated = [...prev];
      updated[idx] = { ...updated[idx], [field]: value };
      return updated;
    });
  };

  const handleAddWaypoint = () => {
    const last = editWaypoints[editWaypoints.length - 1];
    setEditWaypoints((prev) => [
      ...prev,
      {
        id: genId(),
        name: `Waypoint ${prev.length + 1}`,
        lat: last.lat + 0.01,
        lon: last.lon + 0.01,
        speedLimitKmh: 50,
        description: 'Nuevo punto',
      },
    ]);
  };

  const handleRemoveWaypoint = (idx: number) => {
    if (editWaypoints.length <= 2) return;
    setEditWaypoints((prev) => prev.filter((_, i) => i !== idx));
  };

  const handleApplyCustomRoute = () => {
    setRoutes((prev) => {
      const updated = [...prev];
      updated[3] = { ...updated[3], waypoints: editWaypoints };
      return updated;
    });
    setCurrentWaypointIdx(0);
    setSegmentProgress(0);
  };

  const handleResetNavigation = () => {
    setCurrentWaypointIdx(0);
    setSegmentProgress(0);
  };

  // ─── Render ───────────────────────────────────────────────────────────────
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
              Waypoints reales, cálculo energético por tramo y proyección de SoC a destino
            </p>
          </div>
        </div>

        {/* Route Selector */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-[11px] text-[var(--text-muted)] font-semibold hidden sm:inline">Ruta:</span>
          <select
            value={selectedRouteIdx}
            onChange={(e) => handleRouteChange(Number(e.target.value))}
            className="autoos-surface border border-[var(--border-color)] text-[var(--text-primary)] px-3 py-1.5 rounded-xl font-bold text-xs focus:outline-none cursor-pointer"
          >
            {routes.map((r, i) => (
              <option key={r.id} value={i} className="text-black dark:text-white dark:bg-[#180E24]">
                {r.name}
              </option>
            ))}
          </select>
          {selectedRouteIdx === 3 && (
            <button
              onClick={() => setShowRouteEditor((v) => !v)}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl autoos-surface border border-[var(--border-color)] text-[var(--text-muted)] hover:text-[var(--text-primary)] text-xs font-mono transition"
            >
              <PenLine className="w-3.5 h-3.5" />
              {showRouteEditor ? 'Ocultar Editor' : 'Editar Ruta'}
              {showRouteEditor ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            </button>
          )}
        </div>
      </div>

      {/* ── Custom Route Editor ─────────────────────────────────────────────── */}
      {showRouteEditor && selectedRouteIdx === 3 && (
        <div className="rounded-2xl border border-[var(--accent-primary)]/30 bg-[var(--accent-primary)]/5 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold font-mono text-[var(--text-primary)] flex items-center gap-1.5">
              <PenLine className="w-3.5 h-3.5 text-[var(--accent-primary)]" />
              Editor de Ruta Personalizada
            </h4>
            <div className="flex gap-2">
              <button
                onClick={handleAddWaypoint}
                className="flex items-center gap-1 px-2.5 py-1 rounded-xl bg-[var(--accent-primary)]/15 hover:bg-[var(--accent-primary)]/30 text-[var(--accent-primary)] text-[11px] font-mono font-bold transition"
              >
                <Plus className="w-3 h-3" /> Añadir Punto
              </button>
              <button
                onClick={handleApplyCustomRoute}
                className="flex items-center gap-1 px-2.5 py-1 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-mono font-bold transition"
              >
                <CheckCircle className="w-3 h-3" /> Aplicar Ruta
              </button>
            </div>
          </div>

          {/* Route summary before applying */}
          <div className="grid grid-cols-3 gap-2 text-[11px] font-mono">
            <div className="autoos-surface rounded-xl p-2 border border-[var(--border-color)]">
              <span className="text-[var(--text-muted)] block">Distancia total</span>
              <strong className="text-[var(--text-primary)]">
                {totalRouteKm(editWaypoints).toFixed(2)} km
              </strong>
            </div>
            <div className="autoos-surface rounded-xl p-2 border border-[var(--border-color)]">
              <span className="text-[var(--text-muted)] block">Energía estimada</span>
              <strong className="text-amber-500">
                {(() => {
                  let e = 0;
                  for (let i = 0; i < editWaypoints.length - 1; i++) {
                    const d = haversineKm(editWaypoints[i].lat, editWaypoints[i].lon, editWaypoints[i+1].lat, editWaypoints[i+1].lon);
                    e += segmentEnergyKwh(d, editWaypoints[i].speedLimitKmh);
                  }
                  return e.toFixed(2);
                })()} kWh
              </strong>
            </div>
            <div className="autoos-surface rounded-xl p-2 border border-[var(--border-color)]">
              <span className="text-[var(--text-muted)] block">SoC al llegar</span>
              <strong className={availableKwh >= (() => {
                let e = 0;
                for (let i = 0; i < editWaypoints.length - 1; i++) {
                  const d = haversineKm(editWaypoints[i].lat, editWaypoints[i].lon, editWaypoints[i+1].lat, editWaypoints[i+1].lon);
                  e += segmentEnergyKwh(d, editWaypoints[i].speedLimitKmh);
                }
                return e;
              })() ? 'text-emerald-500' : 'text-red-500'}>
                {Math.max(0, Math.round(batteryLevel - (() => {
                  let e = 0;
                  for (let i = 0; i < editWaypoints.length - 1; i++) {
                    const d = haversineKm(editWaypoints[i].lat, editWaypoints[i].lon, editWaypoints[i+1].lat, editWaypoints[i+1].lon);
                    e += segmentEnergyKwh(d, editWaypoints[i].speedLimitKmh);
                  }
                  return e;
                })() / BATTERY_CAPACITY_KWH * 100))}%
              </strong>
            </div>
          </div>

          {/* Waypoint list */}
          <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
            {editWaypoints.map((wp, idx) => (
              <div key={wp.id} className="autoos-surface rounded-xl p-3 border border-[var(--border-color)] space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold text-[var(--accent-primary)]">
                    PUNTO {idx + 1} {idx === 0 ? '(Inicio)' : idx === editWaypoints.length - 1 ? '(Destino)' : ''}
                  </span>
                  {editWaypoints.length > 2 && (
                    <button onClick={() => handleRemoveWaypoint(idx)} className="text-red-400 hover:text-red-300 transition">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                  <div>
                    <label className="text-[var(--text-muted)] block mb-0.5">Nombre</label>
                    <input
                      type="text"
                      value={wp.name}
                      onChange={(e) => handleWaypointChange(idx, 'name', e.target.value)}
                      className="w-full autoos-surface border border-[var(--border-color)] rounded-lg px-2 py-1 text-[var(--text-primary)] text-[11px] focus:outline-none focus:border-[var(--accent-primary)]"
                    />
                  </div>
                  <div>
                    <label className="text-[var(--text-muted)] block mb-0.5">Vel. máx (km/h)</label>
                    <input
                      type="number"
                      min={10} max={130}
                      value={wp.speedLimitKmh}
                      onChange={(e) => handleWaypointChange(idx, 'speedLimitKmh', Number(e.target.value))}
                      className="w-full autoos-surface border border-[var(--border-color)] rounded-lg px-2 py-1 text-[var(--text-primary)] text-[11px] focus:outline-none focus:border-[var(--accent-primary)]"
                    />
                  </div>
                  <div>
                    <label className="text-[var(--text-muted)] block mb-0.5">Latitud (WGS84)</label>
                    <input
                      type="number"
                      step="0.0001"
                      value={wp.lat}
                      onChange={(e) => handleWaypointChange(idx, 'lat', Number(e.target.value))}
                      className="w-full autoos-surface border border-[var(--border-color)] rounded-lg px-2 py-1 text-[var(--text-primary)] text-[11px] focus:outline-none focus:border-[var(--accent-primary)]"
                    />
                  </div>
                  <div>
                    <label className="text-[var(--text-muted)] block mb-0.5">Longitud (WGS84)</label>
                    <input
                      type="number"
                      step="0.0001"
                      value={wp.lon}
                      onChange={(e) => handleWaypointChange(idx, 'lon', Number(e.target.value))}
                      className="w-full autoos-surface border border-[var(--border-color)] rounded-lg px-2 py-1 text-[var(--text-primary)] text-[11px] focus:outline-none focus:border-[var(--accent-primary)]"
                    />
                  </div>
                </div>
                {/* Segment energy preview */}
                {idx < editWaypoints.length - 1 && (
                  <div className="flex items-center gap-2 text-[10px] font-mono text-[var(--text-muted)]">
                    <Zap className="w-3 h-3 text-amber-400" />
                    Tramo {idx + 1}→{idx + 2}:&nbsp;
                    <strong className="text-amber-400">
                      {haversineKm(wp.lat, wp.lon, editWaypoints[idx + 1].lat, editWaypoints[idx + 1].lon).toFixed(2)} km
                    </strong>
                    &nbsp;·&nbsp;
                    <strong className="text-amber-400">
                      {segmentEnergyKwh(haversineKm(wp.lat, wp.lon, editWaypoints[idx + 1].lat, editWaypoints[idx + 1].lon), wp.speedLimitKmh).toFixed(3)} kWh
                    </strong>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Device Failure Alert */}
      {isDeviceFailed && (
        <div className="p-3 rounded-xl bg-red-500/15 border border-red-500/30 text-red-600 dark:text-red-400 text-xs font-mono flex items-center justify-between gap-3 animate-pulse">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 shrink-0 text-red-500" />
            <span>
              <strong>FALLA EN RECEPTOR GNSS (DEV_GPS_01):</strong> Pérdida total de trama NMEA. Conmutando a estimación inercial Dead Reckoning.
            </span>
          </div>
          <span className="px-2 py-0.5 rounded bg-red-500 text-white font-bold text-[10px] shrink-0">ASIL-D FALLBACK</span>
        </div>
      )}

      {/* ── Route Energy Summary Panel ──────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
        <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)] space-y-0.5">
          <span className="text-[10px] text-[var(--text-muted)] uppercase flex items-center gap-1 font-bold">
            <Route className="w-3 h-3 text-[var(--accent-primary)]" /> Distancia Total
          </span>
          <strong className="text-sm text-[var(--text-primary)] block">{totalDistKm.toFixed(2)} km</strong>
          <span className="text-[10px] text-[var(--text-muted)]">Restante: {distanceRemainingKm} km</span>
        </div>
        <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)] space-y-0.5">
          <span className="text-[10px] text-[var(--text-muted)] uppercase flex items-center gap-1 font-bold">
            <Timer className="w-3 h-3 text-cyan-400" /> Tiempo Estimado
          </span>
          <strong className="text-sm text-cyan-600 dark:text-cyan-400 block">~{etaMinutes} min</strong>
          <span className="text-[10px] text-[var(--text-muted)]">{currentSpeed} km/h actual</span>
        </div>
        <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)] space-y-0.5">
          <span className="text-[10px] text-[var(--text-muted)] uppercase flex items-center gap-1 font-bold">
            <Zap className="w-3 h-3 text-amber-400" /> Energía Ruta
          </span>
          <strong className="text-sm text-amber-500 block">{totalEnergyKwh.toFixed(2)} kWh</strong>
          <span className="text-[10px] text-[var(--text-muted)]">Restante: {remainingEnergyKwh} kWh</span>
        </div>
        <div className={`autoos-surface p-3 rounded-xl border space-y-0.5 ${canReachDestination ? 'border-[var(--border-color)]' : 'border-red-500/50 bg-red-500/10'}`}>
          <span className="text-[10px] text-[var(--text-muted)] uppercase flex items-center gap-1 font-bold">
            <BatteryCharging className={`w-3 h-3 ${canReachDestination ? 'text-emerald-500' : 'text-red-500'}`} /> SoC al Destino
          </span>
          <strong className={`text-sm block ${canReachDestination ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500'}`}>
            {estimatedArrivalSoc}%
          </strong>
          <span className={`text-[10px] font-semibold ${canReachDestination ? 'text-[var(--text-muted)]' : 'text-red-400'}`}>
            {canReachDestination ? '✓ Alcanzable' : '⚠ Batería Insuficiente'}
          </span>
        </div>
      </div>

      {/* ── Live Telemetry Grid ───────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 font-mono text-xs">
        <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
          <span className="text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold">
            <Crosshair className="w-3 h-3 text-[var(--accent-primary)]" /> Coordenadas
          </span>
          <strong className="text-xs text-[var(--text-primary)] block font-bold">{currentLat.toFixed(4)}° N</strong>
          <strong className="text-xs text-[var(--text-primary)] block font-bold">{currentLon.toFixed(4)}° O</strong>
        </div>
        <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
          <span className="text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold">
            <Gauge className="w-3 h-3 text-emerald-500" /> Velocidad
          </span>
          <strong className="text-lg text-emerald-600 dark:text-emerald-400 font-bold">
            {currentSpeed} <span className="text-xs font-normal">km/h</span>
          </strong>
          <span className="text-[10px] text-[var(--text-muted)] block">Límite: {isLastPoint ? 0 : pA.speedLimitKmh} km/h</span>
        </div>
        <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
          <span className="text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold">
            <Compass className="w-3 h-3 text-cyan-500" /> Rumbo
          </span>
          <strong className="text-base text-cyan-600 dark:text-cyan-400 font-bold">
            {headingDeg}° {getHeadingLabel(headingDeg).split(' ')[0]}
          </strong>
          <span className="text-[10px] text-[var(--text-muted)] block truncate">{getHeadingLabel(headingDeg)}</span>
        </div>
        <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
          <span className="text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold">
            <Signal className="w-3 h-3 text-amber-500" /> Satélites GNSS
          </span>
          <strong className={`text-base font-bold ${signalColorClass}`}>{satellites} sat / HDOP {hdop}</strong>
          <span className="text-[10px] text-[var(--text-muted)] block truncate">{signalStatusText}</span>
        </div>
        <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
          <span className="text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold">
            <Clock className="w-3 h-3 text-[var(--accent-primary)]" /> ETA
          </span>
          <strong className="text-base text-[var(--text-primary)] font-bold">{distanceRemainingKm} km</strong>
          <span className="text-[10px] text-emerald-600 dark:text-emerald-400 block font-semibold">~{etaMinutes} min</span>
        </div>
        <div className="autoos-surface p-3 rounded-xl border border-[var(--border-color)]">
          <span className="text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold">
            <BatteryCharging className="w-3 h-3 text-emerald-500" /> SoC Proyectado
          </span>
          <strong className={`text-base font-bold ${canReachDestination ? 'text-[var(--text-primary)]' : 'text-red-500 animate-pulse'}`}>
            {estimatedArrivalSoc}% <span className="text-[10px] font-normal text-[var(--text-muted)]">llegada</span>
          </strong>
          <span className="text-[10px] text-[var(--text-muted)] block">Gasto: ~{remainingEnergyKwh} kWh</span>
        </div>
      </div>

      {/* ── SVG Route Map ─────────────────────────────────────────────────────── */}
      <div className="relative autoos-surface rounded-2xl border border-[var(--border-color)] overflow-hidden p-4">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2 text-xs font-mono">
            <Route className="w-4 h-4 text-[var(--accent-primary)]" />
            <span className="font-bold text-[var(--text-primary)]">{currentRoute.name}</span>
            <span className="text-[11px] text-[var(--text-muted)]">({currentRoute.waypoints.length} waypoints · {totalDistKm.toFixed(1)} km)</span>
          </div>
          {/* Signal mode toggle */}
          <div className="flex items-center gap-1 autoos-card p-0.5 rounded-lg border text-[10px] font-mono">
            {(['RTK', 'DEGRADED', 'TUNNEL'] as const).map((mode) => (
              <button
                key={mode}
                onClick={() => setSignalMode(mode)}
                disabled={isDeviceFailed}
                className={`px-2 py-0.5 rounded transition ${
                  signalMode === mode && !isDeviceFailed
                    ? mode === 'RTK' ? 'bg-emerald-600 text-white font-bold'
                      : mode === 'DEGRADED' ? 'bg-yellow-600 text-white font-bold'
                      : 'bg-red-600 text-white font-bold'
                    : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                }`}
              >
                {mode === 'RTK' ? '🛰️ RTK' : mode === 'DEGRADED' ? '🏢 Jitter' : '🚇 Túnel'}
              </button>
            ))}
          </div>
        </div>

        {/* SVG Canvas */}
        <div className="relative w-full h-56 rounded-xl bg-slate-900 border border-slate-800 overflow-hidden shadow-inner">
          <div className="absolute inset-0 opacity-15 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]" />
          <svg className="w-full h-full" viewBox="0 0 800 240" preserveAspectRatio="none">
            <defs>
              <linearGradient id="routeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#8b5cf6" />
                <stop offset="50%" stopColor="#06b6d4" />
                <stop offset="100%" stopColor="#10b981" />
              </linearGradient>
              <filter id="gpsglow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="glow" />
                <feComposite in="SourceGraphic" in2="glow" operator="over" />
              </filter>
            </defs>
            {(() => {
              const wps = currentRoute.waypoints;
              const n = wps.length;
              const pts = wps.map((wp, idx) => ({
                x: 60 + (idx / (n - 1)) * 680,
                y: 120 + Math.sin(idx * 1.5) * 50,
                wp,
              }));
              let path = `M ${pts[0].x} ${pts[0].y}`;
              for (let i = 1; i < pts.length; i++) {
                const mx = (pts[i - 1].x + pts[i].x) / 2;
                path += ` C ${mx} ${pts[i - 1].y}, ${mx} ${pts[i].y}, ${pts[i].x} ${pts[i].y}`;
              }
              const ci = currentWaypointIdx;
              const ni = Math.min(ci + 1, n - 1);
              const carX = pts[ci].x + (pts[ni].x - pts[ci].x) * segmentProgress;
              const carY = pts[ci].y + (pts[ni].y - pts[ci].y) * segmentProgress;
              return (
                <>
                  <path d={path} fill="none" stroke="#1e293b" strokeWidth="18" strokeLinecap="round" />
                  <path d={path} fill="none" stroke="#475569" strokeWidth="2" strokeDasharray="6 6" />
                  <path d={path} fill="none" stroke="url(#routeGrad)" strokeWidth="4" strokeLinecap="round" filter="url(#gpsglow)" />
                  {pts.map((p, idx) => {
                    const passed = idx < currentWaypointIdx;
                    const curr = idx === currentWaypointIdx;
                    return (
                      <g key={p.wp.id}>
                        <circle cx={p.x} cy={p.y} r={curr ? 12 : 7}
                          fill={passed ? '#10b981' : curr ? '#06b6d4' : '#334155'}
                          fillOpacity={curr ? 0.3 : 0.8}
                          stroke={curr ? '#06b6d4' : '#64748b'} strokeWidth="2" />
                        <circle cx={p.x} cy={p.y} r={curr ? 6 : 4}
                          fill={passed ? '#10b981' : curr ? '#ffffff' : '#94a3b8'} />
                        <text x={p.x} y={p.y - 18} textAnchor="middle" fill="#e2e8f0"
                          fontSize="10" fontWeight="bold" fontFamily="monospace">
                          {p.wp.name.split('/')[0].substring(0, 16)}
                        </text>
                        {/* Distance label on segments */}
                        {idx < n - 1 && (
                          <text
                            x={(p.x + pts[idx + 1].x) / 2}
                            y={(p.y + pts[idx + 1].y) / 2 - 10}
                            textAnchor="middle" fill="#94a3b8" fontSize="9" fontFamily="monospace">
                            {haversineKm(p.wp.lat, p.wp.lon, pts[idx + 1].wp.lat, pts[idx + 1].wp.lon).toFixed(1)}km
                          </text>
                        )}
                      </g>
                    );
                  })}
                  {/* Vehicle indicator */}
                  <g transform={`translate(${carX}, ${carY})`}>
                    <circle r="22" fill={isDeviceFailed ? '#ef4444' : '#06b6d4'} fillOpacity="0.25" className="animate-ping" />
                    <circle r="12" fill={isDeviceFailed ? '#ef4444' : '#06b6d4'} stroke="#ffffff" strokeWidth="2.5" filter="url(#gpsglow)" />
                    <polygon points="0,-8 6,6 -6,6" fill="#ffffff" transform={`rotate(${headingDeg})`} />
                  </g>
                </>
              );
            })()}
          </svg>
          {/* HUD overlay */}
          <div className="absolute bottom-2 left-3 right-3 flex items-center justify-between text-[11px] font-mono text-slate-300 bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700">
            <span className="flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-cyan-400" />
              <span>Siguiente: <strong>{pB.name}</strong></span>
            </span>
            <span className="text-cyan-400 font-bold">{Math.round(segmentProgress * 100)}% tramo · {haversineKm(pA.lat, pA.lon, pB.lat, pB.lon).toFixed(2)} km</span>
          </div>
        </div>

        {/* Waypoint progress bar */}
        <div className="mt-3 flex items-center justify-between gap-1 overflow-x-auto py-1">
          {currentRoute.waypoints.map((wp, idx) => {
            const done = idx < currentWaypointIdx;
            const curr = idx === currentWaypointIdx;
            return (
              <div key={wp.id} className={`flex-1 min-w-[120px] p-2 rounded-xl border text-xs font-mono transition ${
                curr ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/10 ring-1 ring-[var(--accent-primary)]/30 text-[var(--text-primary)]'
                : done ? 'border-emerald-500/30 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400'
                : 'autoos-card opacity-60 text-[var(--text-muted)]'
              }`}>
                <div className="flex items-center justify-between text-[10px] font-bold">
                  <span>Punto {idx + 1}</span>
                  {done ? <span className="text-emerald-500">✓</span> : curr ? <span className="text-[var(--accent-primary)] animate-pulse">● En Ruta</span> : <span>Pendiente</span>}
                </div>
                <div className="font-bold text-[11px] truncate mt-0.5">{wp.name}</div>
                <div className="text-[9px] text-[var(--text-muted)]">{wp.speedLimitKmh} km/h · {
                  idx < currentRoute.waypoints.length - 1
                    ? `${haversineKm(wp.lat, wp.lon, currentRoute.waypoints[idx+1].lat, currentRoute.waypoints[idx+1].lon).toFixed(1)} km tramo`
                    : 'Destino final'
                }</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-[var(--border-color)]">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsNavigating((v) => !v)}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold font-mono flex items-center gap-1.5 transition shadow-sm ${
              isNavigating ? 'bg-amber-500 hover:bg-amber-400 text-white' : 'bg-emerald-600 hover:bg-emerald-500 text-white'
            }`}
          >
            {isNavigating ? <Pause className="w-3.5 h-3.5 fill-current" /> : <Play className="w-3.5 h-3.5 fill-current" />}
            {isNavigating ? 'Pausar GPS' : 'Reanudar GPS'}
          </button>
          <button
            onClick={handleResetNavigation}
            className="px-3 py-2 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-muted)] hover:text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold flex items-center gap-1.5 transition font-mono"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Reiniciar
          </button>
        </div>
        <div className="flex items-center gap-1.5 autoos-surface p-1 rounded-xl text-xs font-mono">
          <span className="text-[10px] text-[var(--text-muted)] px-1 font-bold">Velocidad sim:</span>
          {([1, 2, 5] as const).map((m) => (
            <button key={m} onClick={() => setSpeedMultiplier(m)}
              className={`px-2.5 py-1 rounded-lg font-bold transition ${
                speedMultiplier === m ? 'bg-[var(--accent-primary)] text-white shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'
              }`}>{m}x</button>
          ))}
        </div>
      </div>
    </div>
  );
};
