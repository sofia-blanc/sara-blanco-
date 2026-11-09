// COMPONENT: GPS REAL-TIME SIMULATOR (rt_gps)
// ==========================================
var PRESET_GPS_ROUTES = [
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
    name: 'Ruta 3: Tramo de Túneles y Montaña (Prueba Dead Reckoning)',
    description: 'Pérdida forzada de satélites para verificar la odometría inercial IMU.',
    waypoints: [
      { id: 't1', name: 'Portal Occidental', lat: 4.6400, lon: -74.1200, speedLimitKmh: 50, description: 'Entrada con cielo abierto' },
      { id: 't2', name: 'Boca Túnel de la Línea Este', lat: 4.6490, lon: -74.1350, speedLimitKmh: 60, description: 'Pérdida de señal GNSS' },
      { id: 't3', name: 'Cámara Subterránea Intermedia', lat: 4.6620, lon: -74.1480, speedLimitKmh: 55, description: 'Navegación 100% Inercial IMU' },
      { id: 't4', name: 'Salida Galería Valle Verde', lat: 4.6780, lon: -74.1620, speedLimitKmh: 45, description: 'Recuperación de señal RTK' }
    ]
  }
];

var rt_gps = function({ isDeviceFailed, activeDtc, userRole, onRoleRestricted, batteryLevel }) {
  var [selectedRouteIdx, setSelectedRouteIdx] = (0, _.useState)(0);
  var currentRoute = PRESET_GPS_ROUTES[selectedRouteIdx];

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

  var pA = currentRoute.waypoints[currentWaypointIdx];
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

  var waypointsRemaining = currentRoute.waypoints.length - 1 - currentWaypointIdx;
  var distanceRemainingKm = Math.max(0.4, Number((waypointsRemaining * 2.8 + (1 - segmentProgress) * 2.8).toFixed(1)));
  var etaMinutes = currentSpeed > 0 ? Math.round((distanceRemainingKm / currentSpeed) * 60) : 0;

  var satellites = 18;
  var hdop = 0.7;
  var signalStatusText = 'Óptimo RTK Submétrica';
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

  var estimatedKwhToArrival = Number((distanceRemainingKm * 0.16).toFixed(2));
  var estimatedArrivalSoc = Math.max(2, Math.round(batteryLevel - (estimatedKwhToArrival / 60) * 100));

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
                      'Simulador GNSS / GPS Dinámico en Tiempo Real',
                      isDeviceFailed ? (0, E.jsxDEV)('span', { className: 'text-[10px] font-mono px-2 py-0.5 rounded-full bg-red-600 text-white font-bold uppercase animate-pulse', children: `DTC: ${activeDtc || 'U0100-87'}` }, void 0, false) : null
                    ]
                  }, void 0, true),
                  (0, E.jsxDEV)('p', { className: 'text-[11px] text-[var(--text-muted)]', children: 'Cálculo cinemático de waypoints, odometría satelital, rumbo inercial y consumo energético proyectado' }, void 0, false)
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
                onChange: function(e) { setSelectedRouteIdx(Number(e.target.value)); setCurrentWaypointIdx(0); setSegmentProgress(0); },
                className: 'autoos-surface border border-[var(--border-color)] text-[var(--text-primary)] px-3 py-1.5 rounded-xl font-bold text-xs focus:outline-none cursor-pointer',
                children: PRESET_GPS_ROUTES.map(function(r, i) {
                  return (0, E.jsxDEV)('option', { value: i, className: 'text-black dark:text-white dark:bg-[#180E24]', children: r.name }, r.id, false);
                })
              }, void 0, false)
            ]
          }, void 0, true)
        ]
      }, void 0, true),
      isDeviceFailed ? (0, E.jsxDEV)('div', {
        className: 'p-3 rounded-xl bg-red-500/15 border border-red-500/30 text-red-600 dark:text-red-400 text-xs font-mono flex items-center justify-between gap-3 animate-pulse',
        children: [
          (0, E.jsxDEV)('div', {
            className: 'flex items-center gap-2',
            children: [
              (0, E.jsxDEV)(Fe, { className: 'w-4 h-4 shrink-0 text-red-500' }, void 0, false),
              (0, E.jsxDEV)('span', { children: [(0, E.jsxDEV)('strong', { children: 'FALLA EN RECEPTOR GNSS (DEV_GPS_01):' }, void 0, false), ' Pérdida total de trama NMEA. Conmutando automáticamente a estimación inercial por Giroscopio IMU y Odometría (Dead Reckoning).'] }, void 0, true)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('span', { className: 'px-2 py-0.5 rounded bg-red-500 text-white font-bold text-[10px] shrink-0', children: 'ASIL-D FALLBACK' }, void 0, false)
        ]
      }, void 0, true) : null,
      (0, E.jsxDEV)('div', {
        className: 'grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 font-mono text-xs',
        children: [
          (0, E.jsxDEV)('div', {
            className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)]',
            children: [
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold', children: [(0, E.jsxDEV)(IconCrosshair, { className: 'w-3 h-3 text-[var(--accent-primary)]' }, void 0, false), ' Coordenadas WGS84'] }, void 0, true),
              (0, E.jsxDEV)('strong', { className: 'text-xs text-[var(--text-primary)] block font-bold truncate', children: `${currentLat.toFixed(4)}° N` }, void 0, false),
              (0, E.jsxDEV)('strong', { className: 'text-xs text-[var(--text-primary)] block font-bold truncate', children: `${currentLon.toFixed(4)}° O` }, void 0, false)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)]',
            children: [
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold', children: [(0, E.jsxDEV)(De, { className: 'w-3 h-3 text-emerald-500' }, void 0, false), ' Velocidad Real'] }, void 0, true),
              (0, E.jsxDEV)('strong', { className: 'text-lg text-emerald-600 dark:text-emerald-400 font-bold', children: [currentSpeed, ' ', (0, E.jsxDEV)('span', { className: 'text-xs font-normal', children: 'km/h' }, void 0, false)] }, void 0, true),
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] block', children: `Límite: ${isLastPoint ? 0 : pA.speedLimitKmh} km/h` }, void 0, false)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)]',
            children: [
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold', children: [(0, E.jsxDEV)(IconCompass, { className: 'w-3 h-3 text-cyan-500' }, void 0, false), ' Rumbo / Brújula'] }, void 0, true),
              (0, E.jsxDEV)('strong', { className: 'text-base text-cyan-600 dark:text-cyan-400 font-bold', children: `${headingDeg}° ${getHeadingLabel(headingDeg).split(' ')[0]}` }, void 0, false),
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] block truncate', children: getHeadingLabel(headingDeg) }, void 0, false)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)]',
            children: [
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold', children: [(0, E.jsxDEV)(IconSignal, { className: 'w-3 h-3 text-amber-500' }, void 0, false), ' Satélites GNSS'] }, void 0, true),
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
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1 font-bold', children: [(0, E.jsxDEV)(me, { className: 'w-3 h-3 text-emerald-500' }, void 0, false), ' Proyección SoC'] }, void 0, true),
              (0, E.jsxDEV)('strong', { className: 'text-base text-[var(--text-primary)] font-bold', children: [`${estimatedArrivalSoc}% `, (0, E.jsxDEV)('span', { className: 'text-[10px] font-normal text-[var(--text-muted)]', children: 'llegada' }, void 0, false)] }, void 0, true),
              (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] block', children: `Gasto: ~${estimatedKwhToArrival} kWh` }, void 0, false)
            ]
          }, void 0, true)
        ]
      }, void 0, true),
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
                  (0, E.jsxDEV)('span', { className: 'text-[11px] text-[var(--text-muted)]', children: `(${currentRoute.waypoints.length} waypoints)` }, void 0, false)
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
                  var x = 70 + (idx / (numPoints - 1)) * 660;
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
                var pCurrent = points[currentWaypointIdx];
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
                  isNavigating ? (0, E.jsxDEV)(Ae, { className: 'w-3.5 h-3.5 fill-current' }, void 0, false) : (0, E.jsxDEV)(je, { className: 'w-3.5 h-3.5 fill-current' }, void 0, false),
                  (0, E.jsxDEV)('span', { children: isNavigating ? 'Pausar Simulación GPS' : 'Reanudar Navegación' }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('button', {
                onClick: function() { setCurrentWaypointIdx(0); setSegmentProgress(0); },
                className: 'px-3 py-2 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-muted)] hover:text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold flex items-center gap-1.5 transition font-mono',
                children: [
                  (0, E.jsxDEV)(Pe, { className: 'w-3.5 h-3.5' }, void 0, false),
                  (0, E.jsxDEV)('span', { children: 'Reiniciar al Origen' }, void 0, false)
                ]
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

// ==========================================
