import os
import base64

# 1. Read build_unified_bundle.py
with open('C:/Users/Usuario/Desktop/mio/universidad/autoos/build_unified_bundle.py', 'r', encoding='utf-8') as f:
    build_script = f.read()

# ==============================================================================
# ENHANCEMENT 1: Add IconPlus, IconTrash2, IconPenLine, IconTimer, IconZap, IconChevronDown, IconChevronUp
# ==============================================================================
additional_icons = """
var IconPlus = x(`plus`, [[`line`, {x1: `12`, y1: `5`, x2: `12`, y2: `19`, key: `pl1`}], [`line`, {x1: `5`, y1: `12`, x2: `19`, y2: `12`, key: `pl2`}]] );
var IconTrash2 = x(`trash-2`, [[`path`, {d: `M3 6h18`, key: `tr1`}], [`path`, {d: `M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6`, key: `tr2`}], [`path`, {d: `M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2`, key: `tr3`}]] );
var IconPenLine = x(`pen-line`, [[`path`, {d: `M12 20h9`, key: `pn1`}], [`path`, {d: `M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z`, key: `pn2`}]] );
var IconTimer = x(`timer`, [[`line`, {x1: `10`, x2: `14`, y1: `2`, y2: `2`, key: `tm1`}], [`line`, {x1: `12`, x2: `15`, y1: `14`, y2: `11`, key: `tm2`}], [`circle`, {cx: `12`, cy: `14`, r: `8`, key: `tm3`}]] );
var IconZap = x(`zap`, [[`polygon`, {points: `13 2 3 14 12 14 11 22 21 10 12 10 13 2`, key: `zp1`}]] );
var IconChevronDown = x(`chevron-down`, [[`path`, {d: `m6 9 6 6 6-6`, key: `cd1`}]] );
var IconChevronUp = x(`chevron-up`, [[`path`, {d: `m18 15-6-6-6 6`, key: `cu1`}]] );
"""

if 'var IconPlus =' not in build_script:
    icon_marker = 'var IconNavigation = x('
    build_script = build_script.replace(icon_marker, additional_icons + '\n' + icon_marker, 1)
    print("Added additional Lucide icons to build script.")

# ==============================================================================
# ENHANCEMENT 2: Dynamic GPS Component (rt_gps) with Editable Route & Energy/Time Calculator
# ==============================================================================
new_rt_gps_code = r"""
// ==========================================
// COMPONENT: GPS REAL-TIME SIMULATOR (rt_gps)
// Total Custom Route + Waypoint Editing + Energy & ETA Calculator
// ==========================================
function haversineDistKm(lat1, lon1, lat2, lon2) {
  var R = 6371;
  var dLat = ((lat2 - lat1) * Math.PI) / 180;
  var dLon = ((lon2 - lon1) * Math.PI) / 180;
  var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function calcTotalRouteKm(waypoints) {
  var dist = 0;
  for (var i = 0; i < waypoints.length - 1; i++) {
    dist += haversineDistKm(waypoints[i].lat, waypoints[i].lon, waypoints[i + 1].lat, waypoints[i + 1].lon);
  }
  return dist;
}

function calcSegmentEnergyKwh(distKm, speedKmh) {
  var efficiencyWhPerKm = 150 + speedKmh * 0.45;
  return (distKm * efficiencyWhPerKm) / 1000;
}

var DEFAULT_GPS_ROUTES = [
  {
    id: 'route_urbana',
    name: 'Ruta 1: Campus Universitario → Centro Tecnológico',
    description: 'Circuito urbano con cruces semafóricos y cañones de edificios.',
    waypoints: [
      { id: 'w1', name: 'Plaza Central / Origen', lat: 4.6097, lon: -74.0817, speedLimitKmh: 30, description: 'Salida de cochera vehicular' },
      { id: 'w2', name: 'Av. Caracas / Calle 34', lat: 4.6240, lon: -74.0720, speedLimitKmh: 45, description: 'Intersección troncal' },
      { id: 'w3', name: 'Campus Universitario (Cra 30)', lat: 4.6385, lon: -74.0850, speedLimitKmh: 40, description: 'Acceso a laboratorios' },
      { id: 'w4', name: 'Parque Metropolitano', lat: 4.6550, lon: -74.0930, speedLimitKmh: 50, description: 'Vía arterial despejada' },
      { id: 'w5', name: 'Complejo Tecnológico / Destino', lat: 4.6850, lon: -74.0790, speedLimitKmh: 35, description: 'Estación de carga rápida' }
    ]
  },
  {
    id: 'route_autopista',
    name: 'Ruta 2: Corredor de Alta Velocidad (Autopista Norte)',
    description: 'Prueba de crucero autónomo y fusión radar/GNSS a 80-100 km/h.',
    waypoints: [
      { id: 'a1', name: 'Intercambiador Calle 100', lat: 4.6860, lon: -74.0560, speedLimitKmh: 60, description: 'Incorporación a carril rápido' },
      { id: 'a2', name: 'Paso Elevado Calle 134', lat: 4.7180, lon: -74.0480, speedLimitKmh: 80, description: 'Tramo recto ACC activo' },
      { id: 'a3', name: 'Portal Norte Calle 170', lat: 4.7550, lon: -74.0390, speedLimitKmh: 90, description: 'Navegación por carril L3' },
      { id: 'a4', name: 'Peaje Autopista Chía', lat: 4.8200, lon: -74.0320, speedLimitKmh: 40, description: 'Desaceleración y telepeaje' }
    ]
  },
  {
    id: 'route_tunel',
    name: 'Ruta 3: Tramo de Túneles y Montaña (Dead Reckoning)',
    description: 'Pérdida forzada de satélites para verificar la odometría inercial IMU.',
    waypoints: [
      { id: 't1', name: 'Portal Occidental', lat: 4.6400, lon: -74.1200, speedLimitKmh: 50, description: 'Entrada con cielo abierto' },
      { id: 't2', name: 'Boca Túnel de la Línea Este', lat: 4.6490, lon: -74.1350, speedLimitKmh: 60, description: 'Pérdida de señal GNSS' },
      { id: 't3', name: 'Cámara Subterránea Intermedia', lat: 4.6620, lon: -74.1480, speedLimitKmh: 55, description: 'Navegación 100% Inercial IMU' },
      { id: 't4', name: 'Salida Galería Valle Verde', lat: 4.6780, lon: -74.1620, speedLimitKmh: 45, description: 'Recuperación de señal RTK' }
    ]
  },
  {
    id: 'route_custom',
    name: '✏️ Ruta Personalizada (Configurable)',
    description: 'Configura tus propios waypoints, coordenadas y límites de velocidad.',
    waypoints: [
      { id: 'c1', name: 'Punto de Inicio', lat: 4.6097, lon: -74.0817, speedLimitKmh: 35, description: 'Origen personalizado' },
      { id: 'c2', name: 'Punto Intermedio', lat: 4.6450, lon: -74.0650, speedLimitKmh: 50, description: 'Vía intermedia' },
      { id: 'c3', name: 'Destino Final', lat: 4.6920, lon: -74.0480, speedLimitKmh: 40, description: 'Destino de llegada' }
    ]
  }
];

var rt_gps = function({ isDeviceFailed, activeDtc, userRole, onRoleRestricted, batteryLevel }) {
  var bLevel = (batteryLevel !== undefined) ? batteryLevel : 85;
  var [routes, setRoutes] = (0, _.useState)(DEFAULT_GPS_ROUTES);
  var [selectedRouteIdx, setSelectedRouteIdx] = (0, _.useState)(0);
  var currentRoute = routes[selectedRouteIdx] || routes[0];

  var [showRouteEditor, setShowRouteEditor] = (0, _.useState)(false);
  var [editWaypoints, setEditWaypoints] = (0, _.useState)(routes[3].waypoints);

  var [isNavigating, setIsNavigating] = (0, _.useState)(true);
  var [speedMultiplier, setSpeedMultiplier] = (0, _.useState)(1);
  var [currentWaypointIdx, setCurrentWaypointIdx] = (0, _.useState)(0);
  var [segmentProgress, setSegmentProgress] = (0, _.useState)(0.2);
  var [signalMode, setSignalMode] = (0, _.useState)('RTK');

  (0, _.useEffect)(function() {
    if (isDeviceFailed) {
      setSignalMode('TUNNEL');
    } else if (currentRoute.id === 'route_tunel' && currentWaypointIdx >= 1 && currentWaypointIdx <= 2) {
      setSignalMode('TUNNEL');
    } else if (signalMode === 'TUNNEL' && !isDeviceFailed && currentRoute.id !== 'route_tunel') {
      setSignalMode('RTK');
    }
  }, [isDeviceFailed, currentRoute.id, currentWaypointIdx]);

  (0, _.useEffect)(function() {
    if (!isNavigating) return;
    var interval = setInterval(function() {
      setSegmentProgress(function(prev) {
        var step = 0.08 * speedMultiplier;
        var next = prev + step;
        if (next >= 1) {
          setCurrentWaypointIdx(function(wIdx) {
            return (wIdx < currentRoute.waypoints.length - 1) ? (wIdx + 1) : 0;
          });
          return 0;
        }
        return next;
      });
    }, 1000);
    return function() { clearInterval(interval); };
  }, [isNavigating, speedMultiplier, currentRoute.waypoints.length]);

  var pA = currentRoute.waypoints[currentWaypointIdx] || currentRoute.waypoints[0];
  var pB = currentRoute.waypoints[Math.min(currentWaypointIdx + 1, currentRoute.waypoints.length - 1)];
  var isLastPoint = currentWaypointIdx >= currentRoute.waypoints.length - 1;

  var currentLat = isLastPoint ? pA.lat : (pA.lat + (pB.lat - pA.lat) * segmentProgress);
  var currentLon = isLastPoint ? pA.lon : (pA.lon + (pB.lon - pA.lon) * segmentProgress);

  var dLat = (pB.lat - pA.lat);
  var dLon = (pB.lon - pA.lon);
  var headingRad = Math.atan2(dLon, dLat);
  var headingDeg = Math.round((headingRad * 180) / Math.PI);
  if (headingDeg < 0) headingDeg += 360;

  var getHeadingLabel = function(deg) {
    if (deg >= 337.5 || deg < 22.5) return 'N (Norte)';
    if (deg >= 22.5 && deg < 67.5) return 'NE (Noreste)';
    if (deg >= 67.5 && deg < 112.5) return 'E (Este)';
    if (deg >= 112.5 && deg < 157.5) return 'SE (Sureste)';
    if (deg >= 157.5 && deg < 202.5) return 'S (Sur)';
    if (deg >= 202.5 && deg < 247.5) return 'SO (Suroeste)';
    if (deg >= 247.5 && deg < 292.5) return 'O (Oeste)';
    return 'NO (Noroeste)';
  };

  var baseSpeed = isLastPoint ? 0 : pA.speedLimitKmh;
  var currentSpeed = isNavigating ? Math.max(0, Math.round(baseSpeed * (0.85 + Math.sin(segmentProgress * Math.PI) * 0.25))) : 0;

  // Real distance calculations with Haversine
  var totalDistKm = calcTotalRouteKm(currentRoute.waypoints);
  var coveredDistKm = 0;
  for (var iCover = 0; iCover < currentWaypointIdx; iCover++) {
    coveredDistKm += haversineDistKm(currentRoute.waypoints[iCover].lat, currentRoute.waypoints[iCover].lon, currentRoute.waypoints[iCover + 1].lat, currentRoute.waypoints[iCover + 1].lon);
  }
  if (!isLastPoint) {
    coveredDistKm += haversineDistKm(pA.lat, pA.lon, pB.lat, pB.lon) * segmentProgress;
  }
  var distanceRemainingKm = Math.max(0, Number((totalDistKm - coveredDistKm).toFixed(2)));

  var avgSpeedKmh = currentRoute.waypoints.reduce(function(acc, w) { return acc + w.speedLimitKmh; }, 0) / currentRoute.waypoints.length;
  var etaMinutes = currentSpeed > 0 ? Math.round((distanceRemainingKm / avgSpeedKmh) * 60) : 0;

  // Real Energy Calculations (kWh)
  var totalEnergyKwh = 0;
  for (var iE = 0; iE < currentRoute.waypoints.length - 1; iE++) {
    var segD = haversineDistKm(currentRoute.waypoints[iE].lat, currentRoute.waypoints[iE].lon, currentRoute.waypoints[iE + 1].lat, currentRoute.waypoints[iE + 1].lon);
    totalEnergyKwh += calcSegmentEnergyKwh(segD, currentRoute.waypoints[iE].speedLimitKmh);
  }
  var remainingEnergyKwh = 0;
  for (var iR = currentWaypointIdx; iR < currentRoute.waypoints.length - 1; iR++) {
    var segR = haversineDistKm(currentRoute.waypoints[iR].lat, currentRoute.waypoints[iR].lon, currentRoute.waypoints[iR + 1].lat, currentRoute.waypoints[iR + 1].lon);
    remainingEnergyKwh += calcSegmentEnergyKwh(segR, currentRoute.waypoints[iR].speedLimitKmh);
  }
  if (!isLastPoint) {
    var segCur = haversineDistKm(pA.lat, pA.lon, pB.lat, pB.lon);
    remainingEnergyKwh = Math.max(0, remainingEnergyKwh - calcSegmentEnergyKwh(segCur * segmentProgress, pA.speedLimitKmh));
  }
  remainingEnergyKwh = Number(remainingEnergyKwh.toFixed(2));
  totalEnergyKwh = Number(totalEnergyKwh.toFixed(2));

  var BATTERY_CAP_KWH = 60;
  var availableKwh = (bLevel / 100) * BATTERY_CAP_KWH;
  var estimatedArrivalSoc = Math.max(0, Math.round(((availableKwh - remainingEnergyKwh) / BATTERY_CAP_KWH) * 100));
  var isBatterySufficient = availableKwh >= remainingEnergyKwh;

  var satellites = 18;
  var hdop = 0.7;
  var signalStatusText = 'Óptimo RTK Centimétrico';
  var signalColorClass = 'text-emerald-500';

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

  // Handlers for Custom Route Editor
  var handleRouteChange = function(idx) {
    setSelectedRouteIdx(idx);
    setCurrentWaypointIdx(0);
    setSegmentProgress(0);
    if (idx === 3) setShowRouteEditor(true);
  };

  var handleAddWaypoint = function() {
    var last = editWaypoints[editWaypoints.length - 1];
    var nextWp = {
      id: 'wp_' + Date.now(),
      name: 'Punto ' + (editWaypoints.length + 1),
      lat: Number((last.lat + 0.015).toFixed(4)),
      lon: Number((last.lon + 0.015).toFixed(4)),
      speedLimitKmh: 45,
      description: 'Waypoint intermedio'
    };
    setEditWaypoints(function(prev) { return [...prev, nextWp]; });
  };

  var handleRemoveWaypoint = function(idx) {
    if (editWaypoints.length <= 2) return;
    setEditWaypoints(function(prev) { return prev.filter(function(_, i) { return i !== idx; }); });
  };

  var handleWaypointField = function(idx, field, val) {
    setEditWaypoints(function(prev) {
      return prev.map(function(wp, i) {
        if (i === idx) return { ...wp, [field]: val };
        return wp;
      });
    });
  };

  var handleApplyCustomRoute = function() {
    setRoutes(function(prev) {
      var updated = [...prev];
      updated[3] = { ...updated[3], waypoints: editWaypoints };
      return updated;
    });
    setCurrentWaypointIdx(0);
    setSegmentProgress(0);
    setShowRouteEditor(false);
  };

  return (0, E.jsxDEV)('div', {
    className: 'autoos-card rounded-2xl p-5 shadow-xl space-y-4',
    children: [
      (0, E.jsxDEV)('div', {
        className: 'flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[var(--border-color)]',
        children: [
          (0, E.jsxDEV)('div', {
            className: 'flex items-center gap-2.5',
            children: [
              (0, E.jsxDEV)('div', {
                className: `p-2 rounded-xl border ${isDeviceFailed ? 'bg-red-500/15 text-red-500 border-red-500/30 animate-pulse' : 'bg-[var(--accent-primary)]/15 text-[var(--accent-primary)] border-[var(--accent-primary)]/30'}`,
                children: (0, E.jsxDEV)(IconNavigation, { className: 'w-5 h-5' }, void 0, false)
              }, void 0, false),
              (0, E.jsxDEV)('div', {
                children: [
                  (0, E.jsxDEV)('h3', {
                    className: 'text-sm font-serif font-bold text-[var(--text-primary)] flex items-center gap-2',
                    children: [
                      'Navegación Satelital GNSS & Planificador Dinámico de Rutas',
                      isDeviceFailed ? (0, E.jsxDEV)('span', { className: 'text-[10px] font-mono px-2 py-0.5 rounded-full bg-red-600 text-white font-bold uppercase animate-pulse', children: `DTC: ${activeDtc || 'U0100-87'}` }, void 0, false) : null
                    ]
                  }, void 0, true),
                  (0, E.jsxDEV)('p', { className: 'text-[11px] text-[var(--text-muted)]', children: 'Waypoints reales WGS84, cálculo dinámico de gasto energético y tiempo estimado de llegada' }, void 0, false)
                ]
              }, void 0, true)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'flex items-center gap-2 text-xs font-mono',
            children: [
              (0, E.jsxDEV)('span', { className: 'text-[11px] text-[var(--text-muted)] font-semibold hidden sm:inline', children: 'Ruta:' }, void 0, false),
              (0, E.jsxDEV)('select', {
                value: selectedRouteIdx,
                onChange: function(e) { handleRouteChange(Number(e.target.value)); },
                className: 'autoos-surface border border-[var(--border-color)] text-[var(--text-primary)] px-3 py-1.5 rounded-xl font-bold text-xs focus:outline-none cursor-pointer',
                children: routes.map(function(r, i) {
                  return (0, E.jsxDEV)('option', { value: i, className: 'text-black dark:text-white dark:bg-[#180E24]', children: r.name }, r.id, false);
                })
              }, void 0, false),
              selectedRouteIdx === 3 ? (0, E.jsxDEV)('button', {
                onClick: function() { setShowRouteEditor(function(v) { return !v; }); },
                className: 'flex items-center gap-1 px-2.5 py-1.5 rounded-xl autoos-surface border border-[var(--border-color)] text-[var(--text-primary)] hover:border-[var(--accent-primary)] text-xs font-mono transition',
                children: [
                  (0, E.jsxDEV)(IconPenLine, { className: 'w-3.5 h-3.5' }, void 0, false),
                  showRouteEditor ? 'Ocultar Editor' : 'Editar Waypoints',
                  showRouteEditor ? (0, E.jsxDEV)(IconChevronUp, { className: 'w-3 h-3' }, void 0, false) : (0, E.jsxDEV)(IconChevronDown, { className: 'w-3 h-3' }, void 0, false)
                ]
              }, void 0, true) : null
            ]
          }, void 0, true)
        ]
      }, void 0, true),

      // Route Waypoint Editor (Visible when Custom Route is selected)
      showRouteEditor && selectedRouteIdx === 3 ? (0, E.jsxDEV)('div', {
        className: 'rounded-2xl border border-[var(--accent-primary)]/30 bg-[var(--accent-primary)]/5 p-4 space-y-3 font-mono text-xs',
        children: [
          (0, E.jsxDEV)('div', {
            className: 'flex items-center justify-between',
            children: [
              (0, E.jsxDEV)('span', { className: 'font-bold text-[var(--text-primary)] flex items-center gap-1.5', children: [(0, E.jsxDEV)(IconPenLine, { className: 'w-4 h-4 text-[var(--accent-primary)]' }, void 0, false), 'Configurador de Ruta Personalizada'] }, void 0, true),
              (0, E.jsxDEV)('div', {
                className: 'flex gap-2',
                children: [
                  (0, E.jsxDEV)('button', {
                    onClick: handleAddWaypoint,
                    className: 'flex items-center gap-1 px-3 py-1 rounded-xl bg-[var(--accent-primary)]/20 hover:bg-[var(--accent-primary)]/30 text-[var(--text-primary)] font-bold transition',
                    children: [(0, E.jsxDEV)(IconPlus, { className: 'w-3 h-3' }, void 0, false), 'Añadir Waypoint']
                  }, void 0, true),
                  (0, E.jsxDEV)('button', {
                    onClick: handleApplyCustomRoute,
                    className: 'flex items-center gap-1 px-3 py-1 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold transition',
                    children: 'Aplicar y Recalcular Ruta'
                  }, void 0, false)
                ]
              }, void 0, true)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'space-y-2 max-h-56 overflow-y-auto pr-1',
            children: editWaypoints.map(function(wp, idx) {
              return (0, E.jsxDEV)('div', {
                className: 'autoos-surface rounded-xl p-2.5 border border-[var(--border-color)] grid grid-cols-1 sm:grid-cols-5 gap-2 items-center',
                children: [
                  (0, E.jsxDEV)('div', {
                    className: 'sm:col-span-2',
                    children: [
                      (0, E.jsxDEV)('label', { className: 'text-[9px] text-[var(--text-muted)] block uppercase font-bold', children: `Punto ${idx + 1} (${idx === 0 ? 'Inicio' : idx === editWaypoints.length - 1 ? 'Destino' : 'Vía'})` }, void 0, false),
                      (0, E.jsxDEV)('input', {
                        type: 'text', value: wp.name,
                        onChange: function(e) { handleWaypointField(idx, 'name', e.target.value); },
                        className: 'w-full autoos-surface border border-[var(--border-color)] rounded-lg px-2 py-1 text-[var(--text-primary)] text-xs focus:outline-none focus:border-[var(--accent-primary)]'
                      }, void 0, false)
                    ]
                  }, void 0, true),
                  (0, E.jsxDEV)('div', {
                    children: [
                      (0, E.jsxDEV)('label', { className: 'text-[9px] text-[var(--text-muted)] block uppercase font-bold', children: 'Latitud' }, void 0, false),
                      (0, E.jsxDEV)('input', {
                        type: 'number', step: '0.001', value: wp.lat,
                        onChange: function(e) { handleWaypointField(idx, 'lat', Number(e.target.value)); },
                        className: 'w-full autoos-surface border border-[var(--border-color)] rounded-lg px-2 py-1 text-[var(--text-primary)] text-xs focus:outline-none focus:border-[var(--accent-primary)]'
                      }, void 0, false)
                    ]
                  }, void 0, true),
                  (0, E.jsxDEV)('div', {
                    children: [
                      (0, E.jsxDEV)('label', { className: 'text-[9px] text-[var(--text-muted)] block uppercase font-bold', children: 'Longitud' }, void 0, false),
                      (0, E.jsxDEV)('input', {
                        type: 'number', step: '0.001', value: wp.lon,
                        onChange: function(e) { handleWaypointField(idx, 'lon', Number(e.target.value)); },
                        className: 'w-full autoos-surface border border-[var(--border-color)] rounded-lg px-2 py-1 text-[var(--text-primary)] text-xs focus:outline-none focus:border-[var(--accent-primary)]'
                      }, void 0, false)
                    ]
                  }, void 0, true),
                  (0, E.jsxDEV)('div', {
                    className: 'flex items-center gap-2 justify-between',
                    children: [
                      (0, E.jsxDEV)('div', {
                        className: 'flex-1',
                        children: [
                          (0, E.jsxDEV)('label', { className: 'text-[9px] text-[var(--text-muted)] block uppercase font-bold', children: 'Vel. (km/h)' }, void 0, false),
                          (0, E.jsxDEV)('input', {
                            type: 'number', min: '20', max: '120', value: wp.speedLimitKmh,
                            onChange: function(e) { handleWaypointField(idx, 'speedLimitKmh', Number(e.target.value)); },
                            className: 'w-full autoos-surface border border-[var(--border-color)] rounded-lg px-2 py-1 text-[var(--text-primary)] text-xs focus:outline-none focus:border-[var(--accent-primary)]'
                          }, void 0, false)
                        ]
                      }, void 0, true),
                      editWaypoints.length > 2 ? (0, E.jsxDEV)('button', {
                        onClick: function() { handleRemoveWaypoint(idx); },
                        className: 'p-1.5 rounded-lg text-red-500 hover:bg-red-500/10 transition mt-3',
                        title: 'Eliminar punto',
                        children: (0, E.jsxDEV)(IconTrash2, { className: 'w-4 h-4' }, void 0, false)
                      }, void 0, false) : null
                    ]
                  }, void 0, true)
                ]
              }, wp.id, true);
            })
          }, void 0, false)
        ]
      }, void 0, true) : null,

      // Failure Alert Banner
      isDeviceFailed ? (0, E.jsxDEV)('div', {
        className: 'p-3 rounded-xl bg-red-500/15 border border-red-500/30 text-red-600 dark:text-red-400 text-xs font-mono flex items-center justify-between gap-3 animate-pulse',
        children: [
          (0, E.jsxDEV)('div', {
            className: 'flex items-center gap-2',
            children: [
              (0, E.jsxDEV)(Fe, { className: 'w-4 h-4 shrink-0 text-red-500' }, void 0, false),
              (0, E.jsxDEV)('span', {
                children: [(0, E.jsxDEV)('strong', { children: 'FALLA EN RECEPTOR GNSS (DEV_GPS_01): ' }, void 0, false), 'Pérdida de señal satelital RTK. Conmutando a estimación inercial Dead Reckoning IMU.']
              }, void 0, true)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('span', { className: 'px-2 py-0.5 rounded bg-red-500 text-white font-bold text-[10px] shrink-0', children: 'ASIL-D FALLBACK' }, void 0, false)
        ]
      }, void 0, true) : null,

      // Energy & Journey Planning Dashboard
      (0, E.jsxDEV)('div', {
        className: 'grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs',
        children: [
          (0, E.jsxDEV)('div', {
            className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)] space-y-0.5',
            children: [
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase flex items-center gap-1 font-bold', children: [(0, E.jsxDEV)(IconRoute, { className: 'w-3 h-3 text-[var(--accent-primary)]' }, void 0, false), 'Distancia Total'] }, void 0, true),
              (0, E.jsxDEV)('strong', { className: 'text-sm text-[var(--text-primary)] block', children: `${totalDistKm.toFixed(2)} km` }, void 0, false),
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)]', children: `Restante: ${distanceRemainingKm} km` }, void 0, false)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)] space-y-0.5',
            children: [
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase flex items-center gap-1 font-bold', children: [(0, E.jsxDEV)(IconTimer, { className: 'w-3 h-3 text-cyan-400' }, void 0, false), 'Tiempo Estimado'] }, void 0, true),
              (0, E.jsxDEV)('strong', { className: 'text-sm text-cyan-600 dark:text-cyan-400 block', children: `~${etaMinutes} min` }, void 0, false),
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)]', children: `Vel. Promedio: ${Math.round(avgSpeedKmh)} km/h` }, void 0, false)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)] space-y-0.5',
            children: [
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase flex items-center gap-1 font-bold', children: [(0, E.jsxDEV)(IconZap, { className: 'w-3 h-3 text-amber-500' }, void 0, false), 'Gasto Energético'] }, void 0, true),
              (0, E.jsxDEV)('strong', { className: 'text-sm text-amber-500 block', children: `${totalEnergyKwh} kWh` }, void 0, false),
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)]', children: `Por consumir: ${remainingEnergyKwh} kWh` }, void 0, false)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: `autoos-surface p-3 rounded-xl border space-y-0.5 ${isBatterySufficient ? 'border-[var(--border-color)]' : 'border-red-500/50 bg-red-500/10'}`,
            children: [
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase flex items-center gap-1 font-bold', children: [(0, E.jsxDEV)(me, { className: `w-3 h-3 ${isBatterySufficient ? 'text-emerald-500' : 'text-red-500'}` }, void 0, false), 'SoC al Destino'] }, void 0, true),
              (0, E.jsxDEV)('strong', { className: `text-sm block ${isBatterySufficient ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500 animate-pulse'}`, children: `${estimatedArrivalSoc}%` }, void 0, false),
              (0, E.jsxDEV)('span', { className: `text-[10px] font-semibold ${isBatterySufficient ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500'}`, children: isBatterySufficient ? '✓ Autonomía OK' : '⚠ Batería Insuficiente' }, void 0, false)
            ]
          }, void 0, true)
        ]
      }, void 0, true),

      // Telemetry Grid
      (0, E.jsxDEV)('div', {
        className: 'grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 font-mono text-xs',
        children: [
          (0, E.jsxDEV)('div', {
            className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)]',
            children: [
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold', children: [(0, E.jsxDEV)(IconCrosshair, { className: 'w-3 h-3 text-[var(--accent-primary)]' }, void 0, false), ' WGS84 Coords'] }, void 0, true),
              (0, E.jsxDEV)('strong', { className: 'text-xs text-[var(--text-primary)] block font-bold truncate', children: `${currentLat.toFixed(4)}° N` }, void 0, false),
              (0, E.jsxDEV)('strong', { className: 'text-xs text-[var(--text-primary)] block font-bold truncate', children: `${currentLon.toFixed(4)}° O` }, void 0, false)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)]',
            children: [
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold', children: [(0, E.jsxDEV)(De, { className: 'w-3 h-3 text-emerald-500' }, void 0, false), ' Velocidad'] }, void 0, true),
              (0, E.jsxDEV)('strong', { className: 'text-lg text-emerald-600 dark:text-emerald-400 font-bold', children: [`${currentSpeed} `, (0, E.jsxDEV)('span', { className: 'text-xs font-normal', children: 'km/h' }, void 0, false)] }, void 0, true),
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] block', children: `Límite: ${isLastPoint ? 0 : pA.speedLimitKmh} km/h` }, void 0, false)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)]',
            children: [
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold', children: [(0, E.jsxDEV)(IconCompass, { className: 'w-3 h-3 text-cyan-500' }, void 0, false), ' Rumbo / IMU'] }, void 0, true),
              (0, E.jsxDEV)('strong', { className: 'text-base text-cyan-600 dark:text-cyan-400 font-bold', children: `${headingDeg}° ${getHeadingLabel(headingDeg).split(' ')[0]}` }, void 0, false),
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] block truncate', children: getHeadingLabel(headingDeg) }, void 0, false)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)]',
            children: [
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold', children: [(0, E.jsxDEV)(IconSignal, { className: 'w-3 h-3 text-amber-500' }, void 0, false), ' Satélites'] }, void 0, true),
              (0, E.jsxDEV)('strong', { className: `text-base font-bold ${signalColorClass}`, children: `${satellites} sat / HDOP ${hdop}` }, void 0, false),
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] block truncate', children: signalStatusText }, void 0, false)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)]',
            children: [
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold', children: [(0, E.jsxDEV)(Se, { className: 'w-3 h-3 text-[var(--accent-primary)]' }, void 0, false), ' Distancia & ETA'] }, void 0, true),
              (0, E.jsxDEV)('strong', { className: 'text-base text-[var(--text-primary)] font-bold', children: `${distanceRemainingKm} km` }, void 0, false),
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-emerald-600 dark:text-emerald-400 block font-semibold', children: `ETA: ~${etaMinutes} min` }, void 0, false)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)]',
            children: [
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold', children: [(0, E.jsxDEV)(me, { className: 'w-3 h-3 text-emerald-500' }, void 0, false), ' SoC Llegada'] }, void 0, true),
              (0, E.jsxDEV)('strong', { className: `text-base font-bold ${isBatterySufficient ? 'text-[var(--text-primary)]' : 'text-red-500 animate-pulse'}`, children: [`${estimatedArrivalSoc}% `, (0, E.jsxDEV)('span', { className: 'text-[10px] font-normal text-[var(--text-muted)]', children: 'restante' }, void 0, false)] }, void 0, true),
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] block', children: `Gasto: ~${remainingEnergyKwh} kWh` }, void 0, false)
            ]
          }, void 0, true)
        ]
      }, void 0, true),

      // Interactive Vector Map Canvas
      (0, E.jsxDEV)('div', {
        className: 'relative autoos-surface rounded-2xl border border-[var(--border-color)] overflow-hidden p-4',
        children: [
          (0, E.jsxDEV)('div', {
            className: 'flex flex-wrap items-center justify-between gap-2 mb-3',
            children: [
              (0, E.jsxDEV)('div', {
                className: 'flex items-center gap-2 text-xs font-mono',
                children: [
                  (0, E.jsxDEV)(IconRoute, { className: 'w-4 h-4 text-[var(--accent-primary)]' }, void 0, false),
                  (0, E.jsxDEV)('span', { className: 'font-bold text-[var(--text-primary)]', children: currentRoute.name }, void 0, false),
                  (0, E.jsxDEV)('span', { className: 'text-[11px] text-[var(--text-muted)]', children: `(${currentRoute.waypoints.length} waypoints · ${totalDistKm.toFixed(1)} km)` }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('div', {
                className: 'flex items-center gap-2 text-xs font-mono',
                children: [
                  (0, E.jsxDEV)('span', { className: 'text-[11px] text-[var(--text-muted)]', children: 'Simulación de Señal:' }, void 0, false),
                  (0, E.jsxDEV)('div', {
                    className: 'flex items-center gap-1 autoos-card p-0.5 rounded-lg border text-[10px]',
                    children: [
                      (0, E.jsxDEV)('button', {
                        onClick: function() { setSignalMode('RTK'); },
                        disabled: isDeviceFailed,
                        className: `px-2 py-0.5 rounded transition ${signalMode === 'RTK' && !isDeviceFailed ? 'bg-emerald-600 text-white font-bold' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'}`,
                        children: '🛰️ RTK Óptima'
                      }, void 0, false),
                      (0, E.jsxDEV)('button', {
                        onClick: function() { setSignalMode('DEGRADED'); },
                        disabled: isDeviceFailed,
                        className: `px-2 py-0.5 rounded transition ${signalMode === 'DEGRADED' && !isDeviceFailed ? 'bg-yellow-600 text-white font-bold' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'}`,
                        children: '🏢 Jitter Urbano'
                      }, void 0, false),
                      (0, E.jsxDEV)('button', {
                        onClick: function() { setSignalMode('TUNNEL'); },
                        className: `px-2 py-0.5 rounded transition ${signalMode === 'TUNNEL' || isDeviceFailed ? 'bg-red-600 text-white font-bold' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'}`,
                        children: '🚇 Túnel (IMU)'
                      }, void 0, false)
                    ]
                  }, void 0, true)
                ]
              }, void 0, true)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'relative w-full h-56 rounded-xl bg-slate-900 border border-slate-800 overflow-hidden shadow-inner flex items-center justify-center',
            children: [
              (0, E.jsxDEV)('div', { className: 'absolute inset-0 opacity-15 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]' }, void 0, false),
              (function() {
                var numPoints = currentRoute.waypoints.length;
                var points = currentRoute.waypoints.map(function(wp, idx) {
                  var x = 70 + (idx / Math.max(1, numPoints - 1)) * 660;
                  var y = 120 + Math.sin(idx * 1.5) * 45;
                  return { x: x, y: y, wp: wp };
                });
                var pathStr = `M ${points[0].x} ${points[0].y}`;
                for (var i = 1; i < points.length; i++) {
                  var prev = points[i - 1];
                  var curr = points[i];
                  var midX = (prev.x + curr.x) / 2;
                  pathStr += ` C ${midX} ${prev.y}, ${midX} ${curr.y}, ${curr.x} ${curr.y}`;
                }
                var pCurrent = points[currentWaypointIdx] || points[0];
                var pNext = points[Math.min(currentWaypointIdx + 1, numPoints - 1)];
                var carX = pCurrent.x + (pNext.x - pCurrent.x) * segmentProgress;
                var carY = pCurrent.y + (pNext.y - pCurrent.y) * segmentProgress;

                return (0, E.jsxDEV)('svg', {
                  className: 'w-full h-full',
                  viewBox: '0 0 800 240',
                  preserveAspectRatio: 'none',
                  children: [
                    (0, E.jsxDEV)('defs', {
                      children: [
                        (0, E.jsxDEV)('linearGradient', {
                          id: 'routeGrad', x1: '0%', y1: '0%', x2: '100%', y2: '0%',
                          children: [
                            (0, E.jsxDEV)('stop', { offset: '0%', stopColor: '#8b5cf6' }, void 0, false),
                            (0, E.jsxDEV)('stop', { offset: '50%', stopColor: '#06b6d4' }, void 0, false),
                            (0, E.jsxDEV)('stop', { offset: '100%', stopColor: '#10b981' }, void 0, false)
                          ]
                        }, void 0, true),
                        (0, E.jsxDEV)('filter', {
                          id: 'glow', x: '-20%', y: '-20%', width: '140%', height: '140%',
                          children: [
                            (0, E.jsxDEV)('feGaussianBlur', { stdDeviation: '3', result: 'glow' }, void 0, false),
                            (0, E.jsxDEV)('feComposite', { in: 'SourceGraphic', in2: 'glow', operator: 'over' }, void 0, false)
                          ]
                        }, void 0, true)
                      ]
                    }, void 0, true),
                    (0, E.jsxDEV)('path', { d: pathStr, fill: 'none', stroke: '#1e293b', strokeWidth: '18', strokeLinecap: 'round' }, void 0, false),
                    (0, E.jsxDEV)('path', { d: pathStr, fill: 'none', stroke: '#475569', strokeWidth: '2', strokeDasharray: '6 6' }, void 0, false),
                    (0, E.jsxDEV)('path', { d: pathStr, fill: 'none', stroke: 'url(#routeGrad)', strokeWidth: '4', strokeLinecap: 'round', filter: 'url(#glow)' }, void 0, false),
                    points.map(function(p, idx) {
                      var isPassed = idx < currentWaypointIdx;
                      var isCurrent = idx === currentWaypointIdx;
                      return (0, E.jsxDEV)('g', {
                        className: 'transition-all duration-300',
                        children: [
                          (0, E.jsxDEV)('circle', {
                            cx: p.x, cy: p.y, r: isCurrent ? 12 : 7,
                            fill: isPassed ? '#10b981' : isCurrent ? '#06b6d4' : '#334155',
                            fillOpacity: isCurrent ? 0.3 : 0.8,
                            stroke: isCurrent ? '#06b6d4' : '#64748b', strokeWidth: '2'
                          }, void 0, false),
                          (0, E.jsxDEV)('circle', {
                            cx: p.x, cy: p.y, r: isCurrent ? 6 : 4,
                            fill: isPassed ? '#10b981' : isCurrent ? '#ffffff' : '#94a3b8'
                          }, void 0, false),
                          (0, E.jsxDEV)('text', {
                            x: p.x, y: p.y - 18, textAnchor: 'middle', fill: '#e2e8f0', fontSize: '10', fontWeight: 'bold', fontFamily: 'monospace',
                            children: p.wp.name.split('/')[0]
                          }, void 0, false)
                        ]
                      }, p.wp.id, true);
                    }),
                    (0, E.jsxDEV)('g', {
                      transform: `translate(${carX}, ${carY})`,
                      children: [
                        (0, E.jsxDEV)('circle', { r: '22', fill: isDeviceFailed ? '#ef4444' : '#06b6d4', fillOpacity: '0.25', className: 'animate-ping' }, void 0, false),
                        (0, E.jsxDEV)('circle', { r: '12', fill: isDeviceFailed ? '#ef4444' : '#06b6d4', stroke: '#ffffff', strokeWidth: '2.5', filter: 'url(#glow)' }, void 0, false),
                        (0, E.jsxDEV)('polygon', { points: '0,-8 6,6 -6,6', fill: '#ffffff', transform: `rotate(${headingDeg})` }, void 0, false)
                      ]
                    }, void 0, true)
                  ]
                }, void 0, true);
              })(),
              (0, E.jsxDEV)('div', {
                className: 'absolute bottom-2 left-3 right-3 flex items-center justify-between text-[11px] font-mono text-slate-300 bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700',
                children: [
                  (0, E.jsxDEV)('span', {
                    className: 'flex items-center gap-1.5',
                    children: [
                      (0, E.jsxDEV)(IconMapPin, { className: 'w-3.5 h-3.5 text-cyan-400' }, void 0, false),
                      (0, E.jsxDEV)('span', { children: ['Siguiente: ', (0, E.jsxDEV)('strong', { children: pB.name }, void 0, false), ` (${pB.description})`] }, void 0, true)
                    ]
                  }, void 0, true),
                  (0, E.jsxDEV)('span', { className: 'text-cyan-400 font-bold', children: `${Math.round(segmentProgress * 100)}% tramo completado` }, void 0, false)
                ]
              }, void 0, true)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'mt-3 flex items-center justify-between gap-1 overflow-x-auto py-1',
            children: currentRoute.waypoints.map(function(wp, idx) {
              var isDone = idx < currentWaypointIdx;
              var isCurrent = idx === currentWaypointIdx;
              return (0, E.jsxDEV)('div', {
                className: `flex-1 min-w-[130px] p-2 rounded-xl border text-xs font-mono transition ${isCurrent ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/10 text-[var(--text-primary)] ring-1 ring-[var(--accent-primary)]/30' : isDone ? 'border-emerald-500/30 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400' : 'autoos-card opacity-60 text-[var(--text-muted)]'}`,
                children: [
                  (0, E.jsxDEV)('div', {
                    className: 'flex items-center justify-between text-[10px] font-bold',
                    children: [
                      (0, E.jsxDEV)('span', { children: `Punto ${idx + 1}` }, void 0, false),
                      isDone ? (0, E.jsxDEV)('span', { className: 'text-emerald-500', children: '✓ Pasado' }, void 0, false) : isCurrent ? (0, E.jsxDEV)('span', { className: 'text-[var(--accent-primary)] animate-pulse', children: '● En Ruta' }, void 0, false) : (0, E.jsxDEV)('span', { children: 'Pendiente' }, void 0, false)
                    ]
                  }, void 0, true),
                  (0, E.jsxDEV)('div', { className: 'font-bold text-[11px] truncate mt-0.5', children: wp.name }, void 0, false),
                  (0, E.jsxDEV)('div', { className: 'text-[9px] text-[var(--text-muted)] truncate', children: `${wp.speedLimitKmh} km/h máx` }, void 0, false)
                ]
              }, wp.id, true);
            })
          }, void 0, false)
        ]
      }, void 0, true),

      // Action Bar
      (0, E.jsxDEV)('div', {
        className: 'flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-[var(--border-color)]',
        children: [
          (0, E.jsxDEV)('div', {
            className: 'flex items-center gap-2',
            children: [
              (0, E.jsxDEV)('button', {
                onClick: function() { setIsNavigating(!isNavigating); },
                className: `px-3.5 py-2 rounded-xl text-xs font-bold font-mono flex items-center gap-1.5 transition shadow-sm ${isNavigating ? 'bg-amber-500 hover:bg-amber-400 text-white' : 'bg-emerald-600 hover:bg-emerald-500 text-white'}`,
                children: [
                  isNavigating ? (0, E.jsxDEV)(Pe, { className: 'w-3.5 h-3.5 fill-current' }, void 0, false) : (0, E.jsxDEV)(Oe, { className: 'w-3.5 h-3.5 fill-current' }, void 0, false),
                  (0, E.jsxDEV)('span', { children: isNavigating ? 'Pausar Simulación GPS' : 'Reanudar Navegación' }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('button', {
                onClick: function() { setCurrentWaypointIdx(0); setSegmentProgress(0); },
                className: 'px-3 py-2 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-muted)] hover:text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold flex items-center gap-1.5 transition font-mono',
                children: [(0, E.jsxDEV)(Re, { className: 'w-3.5 h-3.5' }, void 0, false), (0, E.jsxDEV)('span', { children: 'Reiniciar al Origen' }, void 0, false)]
              }, void 0, true)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'flex items-center gap-1.5 autoos-surface p-1 rounded-xl text-xs font-mono',
            children: [
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] px-1 font-bold', children: 'Velocidad:' }, void 0, false),
              [1, 2, 5].map(function(m) {
                return (0, E.jsxDEV)('button', {
                  onClick: function() { setSpeedMultiplier(m); },
                  className: `px-2.5 py-1 rounded-lg font-bold transition ${speedMultiplier === m ? 'bg-[var(--accent-primary)] text-white shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'}`,
                  children: `${m}x`
                }, m, false);
              })
            ]
          }, void 0, true)
        ]
      }, void 0, true)
    ]
  }, void 0, true);
};
"""

# Replace rt_gps in build_script
idx_start = build_script.find('// COMPONENT: GPS REAL-TIME SIMULATOR (rt_gps)')
idx_end = build_script.find('// COMPONENT: CRITICAL PROCESS SIMULATOR (tt)', idx_start)

if idx_start != -1 and idx_end != -1:
    build_script = build_script[:idx_start] + new_rt_gps_code + '\n' + build_script[idx_end:]
    print("Replaced rt_gps implementation in build_script.")
else:
    print("Error: Could not find rt_gps markers in build_script.")

# ==============================================================================
# ENHANCEMENT 3: Hide SCHEDULER tab button for Conductor
# ==============================================================================
old_tab_markup = """(0, E.jsxDEV)('div', {
              className: 'flex items-center autoos-card p-1 rounded-2xl border text-xs font-mono',
              children: [
                (0, E.jsxDEV)('button', {
                  onClick: function() { setActiveTab('SCHEDULER'); },"""

new_tab_markup = """(0, E.jsxDEV)('div', {
              className: 'flex items-center autoos-card p-1 rounded-2xl border text-xs font-mono',
              children: [
                userRole !== 'conductor' ? (0, E.jsxDEV)('button', {
                  onClick: function() { setActiveTab('SCHEDULER'); },"""

if old_tab_markup in build_script:
    # Also find the end of that first button
    btn_end_marker = "children: [(0, E.jsxDEV)(Ce, { className: 'w-4 h-4' }, void 0, false), (0, E.jsxDEV)('span', { children: 'Planificador & Simuladores' }, void 0, false)]\n                }, void 0, true),"
    btn_end_replace = "children: [(0, E.jsxDEV)(Ce, { className: 'w-4 h-4' }, void 0, false), (0, E.jsxDEV)('span', { children: 'Planificador & Simuladores' }, void 0, false)]\n                }, void 0, true) : null,"

    build_script = build_script.replace(old_tab_markup, new_tab_markup, 1)
    build_script = build_script.replace(btn_end_marker, btn_end_replace, 1)
    print("Modified tab bar to hide SCHEDULER for conductor.")

# Also add effect to auto-switch conductor to COCKPIT if activeTab is SCHEDULER
conductor_guard = """
  (0, _.useEffect)(function() {
    if (userRole === 'conductor' && activeTab === 'SCHEDULER') {
      setActiveTab('COCKPIT');
    }
  }, [userRole, activeTab]);
"""
if "userRole === 'conductor' && activeTab === 'SCHEDULER'" not in build_script:
    guard_marker = "var [activeTab, setActiveTab] = (0, _.useState)('SCHEDULER');"
    build_script = build_script.replace(guard_marker, guard_marker + conductor_guard, 1)
    print("Added conductor tab guard.")

# ==============================================================================
# ENHANCEMENT 4: Add rt_gps inside Tab 2 (COCKPIT)
# ==============================================================================
old_cockpit_tab = """(0, E.jsxDEV)('main', {
        className: `flex-1 w-full flex flex-col ${activeTab === 'COCKPIT' ? '' : 'hidden'}`,
        children: [
          (0, E.jsxDEV)('div', {
            className: 'autoos-surface border-b px-6 py-2.5 flex items-center justify-between text-xs font-mono text-[var(--text-muted)]',"""

new_cockpit_tab = """(0, E.jsxDEV)('main', {
        className: `flex-1 w-full flex flex-col ${activeTab === 'COCKPIT' ? '' : 'hidden'}`,
        children: [
          (0, E.jsxDEV)('div', {
            className: 'p-4 max-w-7xl mx-auto w-full',
            children: (0, E.jsxDEV)(rt_gps, {
              isDeviceFailed: isGpsFailed, activeDtc: gpsActiveDtc, userRole: userRole, onRoleRestricted: handleRoleRestricted, batteryLevel: battery.level
            }, void 0, false)
          }, void 0, false),
          (0, E.jsxDEV)('div', {
            className: 'autoos-surface border-b px-6 py-2.5 flex items-center justify-between text-xs font-mono text-[var(--text-muted)]',"""

if old_cockpit_tab in build_script:
    build_script = build_script.replace(old_cockpit_tab, new_cockpit_tab, 1)
    print("Mounted rt_gps in Cockpit panel.")

# Save modified build_unified_bundle.py
with open('C:/Users/Usuario/Desktop/mio/universidad/autoos/build_unified_bundle.py', 'w', encoding='utf-8') as f:
    f.write(build_script)
print("Updated build_unified_bundle.py successfully!")
