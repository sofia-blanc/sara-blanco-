with open('orig_bundle.js', 'r', encoding='utf-16') as f:
    orig_js = f.read()

cps_marker = '/app/applet/src/components/CriticalProcessSimulator.tsx'
cps_pos = orig_js.find(cps_marker)
m_decl = orig_js.rfind('M=`', 0, cps_pos)

base_js = orig_js[:m_decl].rstrip(' ,\n\r') + ';\n'

p_acm = orig_js.find('N=`/app/applet/src/components/AlgorithmComparisonModal.tsx`')
p_app = orig_js.find('F=`/app/applet/src/App.tsx`')
middle_raw = orig_js[p_acm:p_app].rstrip(' ,\n\r')
middle_components = 'var ' + middle_raw + ';\n'

custom_js = r"""
// ==========================================
// ADDITIONAL LUCIDE ICONS
// ==========================================
var IconNavigation = x(`navigation`, [[`polygon`, {points: `3 11 22 2 13 21 11 13 3 11`, key: `nav1`}]]);
var IconCompass = x(`compass`, [[`circle`, {cx: `12`, cy: `12`, r: `10`, key: `cp1`}], [`polygon`, {points: `16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76`, key: `cp2`}]] );
var IconCrosshair = x(`crosshair`, [[`circle`, {cx: `12`, cy: `12`, r: `10`, key: `ch1`}], [`line`, {x1: `22`, y1: `12`, x2: `18`, y2: `12`, key: `ch2`}], [`line`, {x1: `6`, y1: `12`, x2: `2`, y2: `12`, key: `ch3`}], [`line`, {x1: `12`, y1: `6`, x2: `12`, y2: `2`, key: `ch4`}], [`line`, {x1: `12`, y1: `22`, x2: `12`, y2: `18`, key: `ch5`}]] );
var IconSignal = x(`signal`, [[`path`, {d: `M2 20h.01`, key: `sg1`}], [`path`, {d: `M7 20v-4`, key: `sg2`}], [`path`, {d: `M12 20v-8`, key: `sg3`}], [`line`, {x1: `17`, y1: `20`, x2: `17`, y2: `8`, key: `sg4`}], [`path`, {d: `M22 4v16`, key: `sg5`}]] );
var IconSliders = x(`sliders`, [[`line`, {x1: `4`, y1: `21`, x2: `4`, y2: `14`, key: `sl1`}], [`line`, {x1: `4`, y1: `10`, x2: `4`, y2: `3`, key: `sl2`}], [`line`, {x1: `12`, y1: `21`, x2: `12`, y2: `12`, key: `sl3`}], [`line`, {x1: `12`, y1: `8`, x2: `12`, y2: `3`, key: `sl4`}], [`line`, {x1: `20`, y1: `21`, x2: `20`, y2: `16`, key: `sl5`}], [`line`, {x1: `20`, y1: `12`, x2: `20`, y2: `3`, key: `sl6`}]] );
var IconWrench = x(`wrench`, [[`path`, {d: `M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z`, key: `wr1`}]] );
var IconRoute = x(`route`, [[`circle`, {cx: `6`, cy: `19`, r: `3`, key: `ro1`}], [`path`, {d: `M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15`, key: `ro2`}], [`circle`, {cx: `18`, cy: `5`, r: `3`, key: `ro3`}]] );
var IconSparkles = x(`sparkles`, [[`path`, {d: `m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z`, key: `sp1`}]] );
var IconMapPin = x(`map-pin`, [[`path`, {d: `M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0`, key: `mp1`}], [`circle`, {cx: `12`, cy: `10`, r: `3`, key: `mp2`}]] );

// ==========================================
// 11 HARDWARE DEVICES DEFINITION
// ==========================================
var INITIAL_VEHICLE_DEVICES = [
  { id: 'dev_01', code: 'DEV_GPS_01', name: 'Receptor GNSS / GPS Diferencial', subsystem: 'Navegación', status: 'operativo', health: 98, criticalLevel: 'esencial', bus: 'CAN-Bus Principal', activeDtc: null, failureMode: null },
  { id: 'dev_02', code: 'DEV_CAM_FRONT', name: 'Cámara Estereoscópica ADAS Frontal', subsystem: 'Visión', status: 'operativo', health: 95, criticalLevel: 'critico', bus: 'Automotive Ethernet', activeDtc: null, failureMode: null },
  { id: 'dev_03', code: 'DEV_LIDAR_01', name: 'Sensor LiDAR 360° Solid-State', subsystem: 'Sensores', status: 'operativo', health: 99, criticalLevel: 'critico', bus: 'Automotive Ethernet', activeDtc: null, failureMode: null },
  { id: 'dev_04', code: 'DEV_RADAR_01', name: 'Radar Milimétrico 77GHz (ACC)', subsystem: 'Sensores', status: 'operativo', health: 94, criticalLevel: 'critico', bus: 'CAN-Bus ADAS', activeDtc: null, failureMode: null },
  { id: 'dev_05', code: 'DEV_BATTERY_BMS', name: 'BMS Batería LiFePO4 Alta Tensión', subsystem: 'Batería', status: 'operativo', health: 92, criticalLevel: 'critico', bus: 'CAN-Bus Principal', activeDtc: null, failureMode: null },
  { id: 'dev_06', code: 'DEV_ACT_BRAKE', name: 'Actuador Frenado By-Wire AEB', subsystem: 'Seguridad Dinámica', status: 'operativo', health: 100, criticalLevel: 'critico', bus: 'CAN-Bus ADAS', activeDtc: null, failureMode: null },
  { id: 'dev_07', code: 'DEV_ACT_STEER', name: 'Actuador Dirección Eléctrica EPS', subsystem: 'Seguridad Dinámica', status: 'operativo', health: 97, criticalLevel: 'critico', bus: 'CAN-Bus ADAS', activeDtc: null, failureMode: null },
  { id: 'dev_08', code: 'DEV_COM_V2X', name: 'Módulo Telemetría 5G / V2X Cloud', subsystem: 'Comunicación', status: 'operativo', health: 91, criticalLevel: 'esencial', bus: 'Automotive Ethernet', activeDtc: null, failureMode: null },
  { id: 'dev_09', code: 'DEV_GATEWAY_CAN', name: 'Gateway Bus CAN-FD Chasis', subsystem: 'Chasis', status: 'operativo', health: 98, criticalLevel: 'critico', bus: 'CAN-Bus Principal', activeDtc: null, failureMode: null },
  { id: 'dev_10', code: 'DEV_INFOTAINMENT', name: 'Pantalla Central Cockpit & Audio', subsystem: 'Multimedia', status: 'operativo', health: 96, criticalLevel: 'confort', bus: 'LIN-Bus Confort', activeDtc: null, failureMode: null },
  { id: 'dev_11', code: 'DEV_HVAC_CLIMA', name: 'Climatización y Gestión Térmica', subsystem: 'Confort', status: 'operativo', health: 89, criticalLevel: 'confort', bus: 'LIN-Bus Confort', activeDtc: null, failureMode: null }
];

var DEVICE_ICON_MAP = {
  DEV_GPS_01: IconNavigation,
  DEV_CAM_FRONT: Te,
  DEV_LIDAR_01: Ne,
  DEV_RADAR_01: we,
  DEV_BATTERY_BMS: Ee,
  DEV_ACT_BRAKE: we,
  DEV_ACT_STEER: _e,
  DEV_COM_V2X: Ge,
  DEV_GATEWAY_CAN: Ce,
  DEV_INFOTAINMENT: _e,
  DEV_HVAC_CLIMA: Ve
};

// ==========================================
// COMPONENT: HARDWARE STATUS GRID (rt_hw)
// ==========================================
var rt_hw = function({ devices, onResetDevice, onResetAllDevices, onTriggerQuickFault, userRole, onRoleRestricted }) {
  var canModify = userRole === 'mecanico';
  var totalHealth = devices.reduce(function(acc, d) { return acc + d.health; }, 0);
  var averageHealth = Math.round(totalHealth / devices.length);
  var faultCount = devices.filter(function(d) { return d.status === 'falla' || d.status === 'desconectado'; }).length;
  var degradedCount = devices.filter(function(d) { return d.status === 'degradado'; }).length;

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
                className: `p-2 rounded-xl border ${faultCount > 0 ? 'bg-red-500/15 text-red-500 border-red-500/30 animate-pulse' : degradedCount > 0 ? 'bg-amber-500/15 text-amber-500 border-amber-500/30' : 'bg-emerald-500/15 text-emerald-500 border-emerald-500/30'}`,
                children: (0, E.jsxDEV)(qe, { className: 'w-5 h-5' }, void 0, false)
              }, void 0, false),
              (0, E.jsxDEV)('div', {
                children: [
                  (0, E.jsxDEV)('div', {
                    className: 'flex items-center gap-2',
                    children: [
                      (0, E.jsxDEV)('h3', { className: 'text-sm font-serif font-bold text-[var(--text-primary)]', children: 'Matriz de Salud de Hardware y Subsistemas Vehiculares' }, void 0, false),
                      (0, E.jsxDEV)('span', {
                        className: `text-[10px] font-mono px-2 py-0.5 rounded-full font-bold uppercase ${faultCount > 0 ? 'bg-red-600 text-white animate-pulse' : degradedCount > 0 ? 'bg-amber-500 text-white' : 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'}`,
                        children: faultCount > 0 ? `🚨 ${faultCount} Falla(s) Crítica(s)` : degradedCount > 0 ? `⚠️ ${degradedCount} Degradado(s)` : '✓ Todos los Sistemas Nominales'
                      }, void 0, false)
                    ]
                  }, void 0, true),
                  (0, E.jsxDEV)('p', { className: 'text-[11px] text-[var(--text-muted)]', children: 'Supervisión en tiempo real de buses CAN-FD, Automotive Ethernet y LIN con inyección bidireccional' }, void 0, false)
                ]
              }, void 0, true)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'flex items-center gap-3',
            children: [
              (0, E.jsxDEV)('div', {
                className: 'text-right font-mono hidden sm:block',
                children: [
                  (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block', children: 'Salud Global:' }, void 0, false),
                  (0, E.jsxDEV)('strong', { className: `text-base font-bold ${averageHealth < 60 ? 'text-red-500' : averageHealth < 85 ? 'text-amber-500' : 'text-emerald-500'}`, children: `${averageHealth}%` }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('button', {
                onClick: function() {
                  if (!canModify) { onRoleRestricted('Restablecer Parámetros de Hardware y Diagnóstico OBD-II'); return; }
                  onResetAllDevices();
                },
                className: 'px-3.5 py-2 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold flex items-center gap-1.5 transition font-mono shadow-sm',
                children: [
                  (0, E.jsxDEV)(Pe, { className: 'w-3.5 h-3.5 text-[var(--accent-primary)]' }, void 0, false),
                  (0, E.jsxDEV)('span', { children: 'Restablecer Todo a Nominal' }, void 0, false)
                ]
              }, void 0, true)
            ]
          }, void 0, true)
        ]
      }, void 0, true),
      (0, E.jsxDEV)('div', {
        className: 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3',
        children: devices.map(function(dev) {
          var IconComp = DEVICE_ICON_MAP[dev.code] || Ce;
          var isFailing = dev.status === 'falla' || dev.status === 'desconectado';
          var isDegraded = dev.status === 'degradado';

          return (0, E.jsxDEV)('div', {
            className: `p-3.5 rounded-xl border transition-all relative flex flex-col justify-between gap-2.5 ${isFailing ? 'border-red-500/70 bg-red-500/10 shadow-md ring-1 ring-red-500/40' : isDegraded ? 'border-amber-500/60 bg-amber-500/5 ring-1 ring-amber-500/30' : 'autoos-surface hover:border-[var(--accent-primary)]/40'}`,
            children: [
              (0, E.jsxDEV)('div', {
                className: 'flex items-start justify-between gap-2',
                children: [
                  (0, E.jsxDEV)('div', {
                    className: 'flex items-center gap-2',
                    children: [
                      (0, E.jsxDEV)('div', {
                        className: `p-1.5 rounded-lg shrink-0 ${isFailing ? 'bg-red-500/20 text-red-500' : isDegraded ? 'bg-amber-500/20 text-amber-500' : 'autoos-card text-[var(--accent-primary)]'}`,
                        children: (0, E.jsxDEV)(IconComp, { className: 'w-4 h-4' }, void 0, false)
                      }, void 0, false),
                      (0, E.jsxDEV)('div', {
                        children: [
                          (0, E.jsxDEV)('h5', { className: 'text-xs font-bold text-[var(--text-primary)] leading-tight', children: dev.name }, void 0, false),
                          (0, E.jsxDEV)('span', { className: 'text-[9px] font-mono text-[var(--text-muted)] block', children: `${dev.code} • ${dev.bus}` }, void 0, false)
                        ]
                      }, void 0, true)
                    ]
                  }, void 0, true),
                  (0, E.jsxDEV)('span', {
                    className: `text-[9px] font-mono px-2 py-0.5 rounded-full font-bold uppercase shrink-0 ${isFailing ? 'bg-red-600 text-white animate-pulse' : isDegraded ? 'bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-500/30' : 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'}`,
                    children: dev.status
                  }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('div', {
                className: 'space-y-1',
                children: [
                  (0, E.jsxDEV)('div', {
                    className: 'flex items-center justify-between text-[10px] font-mono',
                    children: [
                      (0, E.jsxDEV)('span', { className: 'text-[var(--text-muted)]', children: 'Salud Operativa:' }, void 0, false),
                      (0, E.jsxDEV)('span', { className: `font-bold ${isFailing ? 'text-red-500' : isDegraded ? 'text-amber-500' : 'text-emerald-500'}`, children: `${dev.health}%` }, void 0, false)
                    ]
                  }, void 0, true),
                  (0, E.jsxDEV)('div', {
                    className: 'w-full h-1.5 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden',
                    children: (0, E.jsxDEV)('div', {
                      className: `h-full rounded-full transition-all duration-500 ${isFailing ? 'bg-red-500' : isDegraded ? 'bg-amber-500' : 'bg-emerald-500'}`,
                      style: { width: `${dev.health}%` }
                    }, void 0, false)
                  }, void 0, false)
                ]
              }, void 0, true),
              dev.activeDtc ? (0, E.jsxDEV)('div', {
                className: 'p-1.5 rounded-lg bg-red-500/15 border border-red-500/30 text-[10px] font-mono text-red-600 dark:text-red-400',
                children: [
                  (0, E.jsxDEV)('span', { className: 'font-bold', children: `DTC: ${dev.activeDtc}` }, void 0, false),
                  dev.failureMode ? (0, E.jsxDEV)('div', { className: 'text-[9px] opacity-90 truncate', children: dev.failureMode }, void 0, false) : null
                ]
              }, void 0, true) : null,
              (0, E.jsxDEV)('div', {
                className: 'flex items-center justify-between gap-2 pt-1 border-t border-[var(--border-color)]',
                children: isFailing || isDegraded ? (0, E.jsxDEV)('button', {
                  onClick: function() {
                    if (!canModify) { onRoleRestricted('Calibrar / Restablecer Dispositivo de Hardware'); return; }
                    onResetDevice(dev.code);
                  },
                  className: 'w-full py-1 px-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-[10px] font-bold flex items-center justify-center gap-1 transition shadow-sm',
                  children: [
                    (0, E.jsxDEV)(IconWrench, { className: 'w-3 h-3' }, void 0, false),
                    (0, E.jsxDEV)('span', { children: 'Calibrar / Restaurar' }, void 0, false)
                  ]
                }, void 0, true) : (0, E.jsxDEV)('button', {
                  onClick: function() {
                    if (!canModify) { onRoleRestricted('Inyectar Fallas en Sensores o Actuadores'); return; }
                    onTriggerQuickFault(dev.code);
                  },
                  className: 'w-full py-1 px-2 rounded-lg autoos-card hover:bg-red-500/15 hover:text-red-500 hover:border-red-500/30 text-[var(--text-muted)] font-mono text-[10px] font-semibold flex items-center justify-center gap-1 transition border border-[var(--border-color)]',
                  children: [
                    (0, E.jsxDEV)(qe, { className: 'w-3 h-3' }, void 0, false),
                    (0, E.jsxDEV)('span', { children: 'Inyectar Falla de Prueba' }, void 0, false)
                  ]
                }, void 0, true)
              }, void 0, false)
            ]
          }, dev.id, true);
        })
      }, void 0, false)
    ]
  }, void 0, true);
};

// ==========================================
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
// COMPONENT: CRITICAL PROCESS SIMULATOR (tt)
// Total Custom Builder + 7 Presets + Powertrain
// ==========================================
var CUSTOM_FAILURE_TYPES = [
  'Falla Crítica Total / Desconexión de Bus',
  'Degradación de Rendimiento y Descalibración',
  'Sobrecalentamiento Térmico Extremo (>52°C)',
  'Ataque DoS / Inyección Anómala de Tramas',
  'Oclusión Óptica / Ceguera de Sensores',
  'Pérdida de Presión Hidráulica / Retardo Actuador',
  'Desfase de Ángulo y Sobrecorriente By-Wire',
  'Pérdida de Cobertura y Señal Satelital',
  'Personalizado'
];

var PRESET_INCIDENT_SCENARIOS = [
  { id: 'scen_lidar', name: 'Falla Sensor LiDAR 360°', dispositivo: 'DEV_LIDAR_01', dtc: 'U0100-87', burstTime: 4, category: 'sensor', color: '#06b6d4', icon: Ne, desc: 'Oclusión óptica de lentes y pérdida de reflectancia. Conmuta a radar secundario.', powerWatts: 40, memoryMb: 180 },
  { id: 'scen_bms_thermal', name: 'Sobrecalentamiento BMS (48°C)', dispositivo: 'DEV_BATTERY_BMS', dtc: 'P0A7E-00', burstTime: 5, category: 'control', color: '#f59e0b', icon: Ee, desc: 'Celdas HV en límite térmico. Corte preventivo de potencia e inyección de refrigerante.', powerWatts: 70, memoryMb: 110 },
  { id: 'scen_can_attack', name: 'Inyección Anómala Bus CAN-FD', dispositivo: 'DEV_GATEWAY_CAN', dtc: 'U1101-08', burstTime: 3, category: 'seguridad', color: '#ec4899', icon: Fe, desc: 'Saturación por DoS con tramas maliciosas. Aislamiento y conmutación a bus redundante.', powerWatts: 45, memoryMb: 85 },
  { id: 'scen_camera_occlusion', name: 'Descalibración Cámara ADAS', dispositivo: 'DEV_CAM_FRONT', dtc: 'B1203-54', burstTime: 4, category: 'sensor', color: '#8b5cf6', icon: Te, desc: 'Pérdida de reconocimiento de carril 4K. Despliega advertencia en HUD.', powerWatts: 35, memoryMb: 240 },
  { id: 'scen_telemetry_drop', name: 'Corte de Cobertura 5G Nube', dispositivo: 'DEV_COM_V2X', dtc: 'U0140-00', burstTime: 3, category: 'control', color: '#3b82f6', icon: Ge, desc: 'Pérdida de señal celular/satelital. Activa búfer NVRAM local determinístico.', powerWatts: 25, memoryMb: 64 },
  { id: 'scen_aeb', name: 'Frenado Autónomo Emergencia (AEB)', dispositivo: 'DEV_ACT_BRAKE', dtc: 'B1000-01', burstTime: 3, category: 'seguridad', color: '#dc2626', icon: we, desc: 'Obstáculo inminente a 15m. Requiere desalojo inmediato de CPU para actuación EBS.', powerWatts: 65, memoryMb: 64 },
  { id: 'scen_steer', name: 'Fallo Crítico Dirección By-Wire', dispositivo: 'DEV_ACT_STEER', dtc: 'C0040-04', burstTime: 4, category: 'control', color: '#e11d48', icon: _e, desc: 'Desfase anómalo en servomotores EPS. Requiere conmutación a canal redundante.', powerWatts: 55, memoryMb: 96 }
];

var tt = function({ onInjectCriticalProcess, onResetDevice, onResetAllScenarios, currentTime, userRole, onRoleRestricted }) {
  var [viewSubtab, setViewSubtab] = (0, _.useState)('CUSTOM');

  var [targetDeviceCode, setTargetDeviceCode] = (0, _.useState)('DEV_GPS_01');
  var [selectedFailureType, setSelectedFailureType] = (0, _.useState)(CUSTOM_FAILURE_TYPES[0]);
  var [customFaultName, setCustomFaultName] = (0, _.useState)('Falla Crítica de Navegación GNSS');
  var [customDtc, setCustomDtc] = (0, _.useState)('U0100-87');
  var [severityLevel, setSeverityLevel] = (0, _.useState)('ASIL-D');
  var [burstDuration, setBurstDuration] = (0, _.useState)(4);
  var [cpuUsagePct, setCpuUsagePct] = (0, _.useState)(45);
  var [powerWatts, setPowerWatts] = (0, _.useState)(55);
  var [memoryMb, setMemoryMb] = (0, _.useState)(140);
  var [customDescription, setCustomDescription] = (0, _.useState)('Pérdida súbita de señal diferencial RTK. Conmuta a estimación inercial por giróscopo IMU.');

  var [selectedPresetIdx, setSelectedPresetIdx] = (0, _.useState)(0);
  var [activePresetId, setActivePresetId] = (0, _.useState)(null);
  var [lastInjectedPhase, setLastInjectedPhase] = (0, _.useState)(null);

  var canInject = userRole === 'mecanico';

  var handleDeviceChange = function(devCode) {
    setTargetDeviceCode(devCode);
    var dev = INITIAL_VEHICLE_DEVICES.find(function(d) { return d.code === devCode; });
    if (dev) {
      var defaultDtc = dev.code === 'DEV_GPS_01' ? 'U0100-87' : dev.code === 'DEV_CAM_FRONT' ? 'B1203-54' : dev.code === 'DEV_BATTERY_BMS' ? 'P0A7E-00' : dev.code === 'DEV_ACT_BRAKE' ? 'B1000-01' : dev.code === 'DEV_ACT_STEER' ? 'C0040-04' : dev.code === 'DEV_GATEWAY_CAN' ? 'U1101-08' : 'P0100-F1';
      setCustomDtc(defaultDtc);
      setCustomFaultName(`Falla en ${dev.name.split('/')[0].trim()}`);
      setCustomDescription(`Comportamiento anómalo en ${dev.name}. Conmutación a fail-safe.`);
    }
  };

  var handleInjectCustomFault = function() {
    if (!canInject) {
      onRoleRestricted('Inyectar Fallas Críticas de Hardware ASIL-D (Requiere Rol Mecánico / Nivel 10)');
      return;
    }
    var dev = INITIAL_VEHICLE_DEVICES.find(function(d) { return d.code === targetDeviceCode; }) || INITIAL_VEHICLE_DEVICES[0];
    var priority = severityLevel === 'ASIL-D' ? 1 : severityLevel === 'ASIL-B' ? 2 : 4;
    var procToInject = {
      pid: Math.floor(Math.random() * 800) + 200,
      name: customFaultName || `Falla en ${dev.name}`,
      category: dev.subsystem === 'Seguridad Dinámica' ? 'seguridad' : dev.subsystem === 'Sensores' ? 'sensor' : 'control',
      arrivalTime: currentTime,
      burstTime: burstDuration,
      remainingTime: burstDuration,
      priority: priority,
      critical: severityLevel === 'ASIL-D',
      color: '#ef4444',
      state: 'LISTO',
      powerConsumptionWatts: powerWatts,
      cpuUsagePct: cpuUsagePct,
      memoryMb: memoryMb
    };
    setLastInjectedPhase(`[${dev.code}] ${customFaultName} disparada → Impacto en Hardware y CPU`);
    onInjectCriticalProcess(procToInject, dev.code, customDtc, selectedFailureType);
  };

  var handleInjectPreset = function() {
    if (!canInject) {
      onRoleRestricted('Inyectar Fallas Críticas de Hardware ASIL-D (Requiere Rol Mecánico / Nivel 10)');
      return;
    }
    var sc = PRESET_INCIDENT_SCENARIOS[selectedPresetIdx];
    var procToInject = {
      pid: Math.floor(Math.random() * 800) + 200,
      name: sc.name,
      category: sc.category,
      arrivalTime: currentTime,
      burstTime: sc.burstTime,
      remainingTime: sc.burstTime,
      priority: 1,
      critical: true,
      color: sc.color,
      state: 'LISTO',
      powerConsumptionWatts: sc.powerWatts,
      cpuUsagePct: 35,
      memoryMb: sc.memoryMb
    };
    setActivePresetId(sc.id);
    setLastInjectedPhase(`${sc.name} detectada → Desalojando CPU con Prioridad 1`);
    onInjectCriticalProcess(procToInject, sc.dispositivo, sc.dtc, sc.name);
  };

  var handleResetAll = function() {
    setActivePresetId(null);
    setLastInjectedPhase('Todos los escenarios restablecidos. Parámetros nominales ISO 26262 ASIL-D.');
    if (onResetAllScenarios) onResetAllScenarios();
  };

  return (0, E.jsxDEV)('div', {
    className: 'autoos-card rounded-2xl p-5 shadow-xl space-y-4',
    children: [
      (0, E.jsxDEV)('div', {
        className: 'flex flex-wrap items-center justify-between gap-3 pb-3.5 border-b border-[var(--border-color)]',
        children: [
          (0, E.jsxDEV)('div', {
            className: 'flex items-center gap-2.5',
            children: [
              (0, E.jsxDEV)('div', {
                className: 'p-2 rounded-xl bg-red-500/15 text-red-500 border border-red-500/30 animate-pulse',
                children: (0, E.jsxDEV)(Fe, { className: 'w-5 h-5' }, void 0, false)
              }, void 0, false),
              (0, E.jsxDEV)('div', {
                children: [
                  (0, E.jsxDEV)('h3', { className: 'text-sm font-serif font-bold text-[var(--text-primary)] flex items-center gap-2', children: 'Simulador & Configurador Total de Fallas Vehiculares' }, void 0, false),
                  (0, E.jsxDEV)('p', { className: 'text-[11px] text-[var(--text-muted)]', children: 'Personalización total de modo de falla, dispositivo receptor, código DTC, severidad ASIL e impacto en CPU' }, void 0, false)
                ]
              }, void 0, true)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'flex items-center gap-1.5 autoos-surface p-1 rounded-xl text-xs font-mono',
            children: [
              (0, E.jsxDEV)('button', {
                onClick: function() { setViewSubtab('CUSTOM'); },
                className: `px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 ${viewSubtab === 'CUSTOM' ? 'bg-[var(--accent-primary)] text-white shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'}`,
                children: [
                  (0, E.jsxDEV)(IconSliders, { className: 'w-3.5 h-3.5' }, void 0, false),
                  (0, E.jsxDEV)('span', { children: 'Configurador Personalizado' }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('button', {
                onClick: function() { setViewSubtab('PRESETS'); },
                className: `px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 ${viewSubtab === 'PRESETS' ? 'bg-[var(--accent-primary)] text-white shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'}`,
                children: [
                  (0, E.jsxDEV)(IconSparkles, { className: 'w-3.5 h-3.5' }, void 0, false),
                  (0, E.jsxDEV)('span', { children: 'Escenarios Rápidos (7)' }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('button', {
                onClick: function() { setViewSubtab('POWERTRAIN'); },
                className: `px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-1.5 ${viewSubtab === 'POWERTRAIN' ? 'bg-[var(--accent-primary)] text-white shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'}`,
                children: [
                  (0, E.jsxDEV)(De, { className: 'w-3.5 h-3.5' }, void 0, false),
                  (0, E.jsxDEV)('span', { children: 'Tren Motriz' }, void 0, false)
                ]
              }, void 0, true)
            ]
          }, void 0, true)
        ]
      }, void 0, true),
      !canInject ? (0, E.jsxDEV)('div', {
        className: 'px-3 py-1.5 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-600 dark:text-amber-300 text-xs font-mono flex items-center gap-2',
        children: [
          (0, E.jsxDEV)(T, { className: 'w-4 h-4 shrink-0' }, void 0, false),
          (0, E.jsxDEV)('span', { children: 'Acceso Restringido: Solo el Mecánico Certificado (Nivel 10) tiene privilegios para inyectar fallas ASIL-D.' }, void 0, false)
        ]
      }, void 0, true) : null,
      viewSubtab === 'CUSTOM' ? (0, E.jsxDEV)('div', {
        className: 'space-y-4',
        children: [
          (0, E.jsxDEV)('div', {
            className: 'grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono',
            children: [
              (0, E.jsxDEV)('div', {
                className: 'space-y-1.5',
                children: [
                  (0, E.jsxDEV)('label', { className: 'text-[11px] text-[var(--text-muted)] uppercase font-bold block', children: '1. Dispositivo / Subsistema a Fallar:' }, void 0, false),
                  (0, E.jsxDEV)('select', {
                    value: targetDeviceCode,
                    onChange: function(e) { handleDeviceChange(e.target.value); },
                    className: 'w-full autoos-surface border border-[var(--border-color)] text-[var(--text-primary)] p-2.5 rounded-xl font-bold text-xs focus:outline-none',
                    children: INITIAL_VEHICLE_DEVICES.map(function(d) {
                      return (0, E.jsxDEV)('option', { value: d.code, className: 'text-black dark:text-white dark:bg-[#180E24]', children: `${d.name} (${d.code})` }, d.code, false);
                    })
                  }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('div', {
                className: 'space-y-1.5',
                children: [
                  (0, E.jsxDEV)('label', { className: 'text-[11px] text-[var(--text-muted)] uppercase font-bold block', children: '2. Modo / Tipo de Falla:' }, void 0, false),
                  (0, E.jsxDEV)('select', {
                    value: selectedFailureType,
                    onChange: function(e) { setSelectedFailureType(e.target.value); },
                    className: 'w-full autoos-surface border border-[var(--border-color)] text-[var(--text-primary)] p-2.5 rounded-xl font-bold text-xs focus:outline-none',
                    children: CUSTOM_FAILURE_TYPES.map(function(ft) {
                      return (0, E.jsxDEV)('option', { value: ft, className: 'text-black dark:text-white dark:bg-[#180E24]', children: ft }, ft, false);
                    })
                  }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('div', {
                className: 'space-y-1.5',
                children: [
                  (0, E.jsxDEV)('label', { className: 'text-[11px] text-[var(--text-muted)] uppercase font-bold block', children: '3. Nivel de Severidad ISO 26262:' }, void 0, false),
                  (0, E.jsxDEV)('div', {
                    className: 'grid grid-cols-3 gap-2',
                    children: [
                      (0, E.jsxDEV)('button', {
                        type: 'button',
                        onClick: function() { setSeverityLevel('ASIL-D'); },
                        className: `py-2 px-2 rounded-xl font-bold transition text-center ${severityLevel === 'ASIL-D' ? 'bg-red-600 text-white shadow-sm ring-2 ring-red-500/40' : 'autoos-surface text-[var(--text-muted)] hover:text-[var(--text-primary)] border border-[var(--border-color)]'}`,
                        children: '🔴 ASIL-D (P1)'
                      }, void 0, false),
                      (0, E.jsxDEV)('button', {
                        type: 'button',
                        onClick: function() { setSeverityLevel('ASIL-B'); },
                        className: `py-2 px-2 rounded-xl font-bold transition text-center ${severityLevel === 'ASIL-B' ? 'bg-amber-600 text-white shadow-sm ring-2 ring-amber-500/40' : 'autoos-surface text-[var(--text-muted)] hover:text-[var(--text-primary)] border border-[var(--border-color)]'}`,
                        children: '🟡 ASIL-B (P2)'
                      }, void 0, false),
                      (0, E.jsxDEV)('button', {
                        type: 'button',
                        onClick: function() { setSeverityLevel('CONFORT'); },
                        className: `py-2 px-2 rounded-xl font-bold transition text-center ${severityLevel === 'CONFORT' ? 'bg-blue-600 text-white shadow-sm ring-2 ring-blue-500/40' : 'autoos-surface text-[var(--text-muted)] hover:text-[var(--text-primary)] border border-[var(--border-color)]'}`,
                        children: '🔵 Confort (P4)'
                      }, void 0, false)
                    ]
                  }, void 0, true)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('div', {
                className: 'space-y-1.5',
                children: [
                  (0, E.jsxDEV)('label', { className: 'text-[11px] text-[var(--text-muted)] uppercase font-bold block', children: '4. Código DTC OBD-II / UDS:' }, void 0, false),
                  (0, E.jsxDEV)('input', {
                    type: 'text',
                    value: customDtc,
                    onChange: function(e) { setCustomDtc(e.target.value); },
                    placeholder: 'Ej. U0100-87, P0A7E, B1203',
                    className: 'w-full autoos-surface border border-[var(--border-color)] text-[var(--text-primary)] p-2.5 rounded-xl font-bold text-xs focus:outline-none'
                  }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('div', {
                className: 'space-y-1.5',
                children: [
                  (0, E.jsxDEV)('label', { className: 'text-[11px] text-[var(--text-muted)] uppercase font-bold block', children: '5. Nombre del Evento / Proceso:' }, void 0, false),
                  (0, E.jsxDEV)('input', {
                    type: 'text',
                    value: customFaultName,
                    onChange: function(e) { setCustomFaultName(e.target.value); },
                    placeholder: 'Nombre descriptivo',
                    className: 'w-full autoos-surface border border-[var(--border-color)] text-[var(--text-primary)] p-2.5 rounded-xl font-bold text-xs focus:outline-none'
                  }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('div', {
                className: 'space-y-1.5',
                children: [
                  (0, E.jsxDEV)('label', {
                    className: 'text-[11px] text-[var(--text-muted)] uppercase font-bold block flex justify-between',
                    children: [
                      (0, E.jsxDEV)('span', { children: '6. Duración Ráfaga CPU:' }, void 0, false),
                      (0, E.jsxDEV)('span', { className: 'text-[var(--accent-primary)]', children: `${burstDuration}s (${cpuUsagePct}% CPU, ${powerWatts}W)` }, void 0, false)
                    ]
                  }, void 0, true),
                  (0, E.jsxDEV)('div', {
                    className: 'flex items-center gap-3 autoos-surface p-2.5 rounded-xl border border-[var(--border-color)]',
                    children: [
                      (0, E.jsxDEV)('input', {
                        type: 'range', min: '1', max: '10', value: burstDuration,
                        onChange: function(e) { setBurstDuration(Number(e.target.value)); },
                        className: 'w-full accent-[var(--accent-primary)] cursor-pointer'
                      }, void 0, false),
                      (0, E.jsxDEV)('span', { className: 'font-bold text-xs shrink-0 w-8 text-right', children: `${burstDuration}s` }, void 0, false)
                    ]
                  }, void 0, true)
                ]
              }, void 0, true)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'space-y-1.5 text-xs font-mono',
            children: [
              (0, E.jsxDEV)('label', { className: 'text-[11px] text-[var(--text-muted)] uppercase font-bold block', children: '7. Descripción Técnica del Incidente:' }, void 0, false),
              (0, E.jsxDEV)('input', {
                type: 'text',
                value: customDescription,
                onChange: function(e) { setCustomDescription(e.target.value); },
                placeholder: 'Detalles del comportamiento anómalo',
                className: 'w-full autoos-surface border border-[var(--border-color)] text-[var(--text-primary)] p-2.5 rounded-xl text-xs focus:outline-none'
              }, void 0, false)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-[var(--border-color)]',
            children: [
              (0, E.jsxDEV)('button', {
                onClick: handleResetAll,
                className: 'px-3.5 py-2.5 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold flex items-center gap-1.5 transition font-mono',
                children: [
                  (0, E.jsxDEV)(Pe, { className: 'w-3.5 h-3.5 text-[var(--accent-primary)]' }, void 0, false),
                  (0, E.jsxDEV)('span', { children: 'Restablecer Todo a Nominal' }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('button', {
                onClick: handleInjectCustomFault,
                className: `px-5 py-2.5 rounded-xl font-bold text-xs uppercase tracking-wider flex items-center gap-2 shadow-md transition font-mono ${canInject ? 'bg-red-600 hover:bg-red-500 text-white shadow-red-500/20 hover:scale-[1.02] active:scale-[0.98]' : 'bg-[var(--bg-surface)] text-[var(--text-muted)] border border-[var(--border-color)] cursor-not-allowed opacity-60'}`,
                children: [
                  (0, E.jsxDEV)(je, { className: 'w-4 h-4 fill-current' }, void 0, false),
                  (0, E.jsxDEV)('span', { children: '⚡ Disparar Falla Personalizada al Sistema!' }, void 0, false)
                ]
              }, void 0, true)
            ]
          }, void 0, true)
        ]
      }, void 0, true) : null,
      viewSubtab === 'PRESETS' ? (0, E.jsxDEV)('div', {
        className: 'space-y-3',
        children: [
          (0, E.jsxDEV)('div', {
            className: 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 max-h-[290px] overflow-y-auto pr-1',
            children: PRESET_INCIDENT_SCENARIOS.map(function(sc, idx) {
              var isSelected = selectedPresetIdx === idx;
              var isActive = activePresetId === sc.id;
              var IconComp = sc.icon;
              return (0, E.jsxDEV)('button', {
                onClick: function() { setSelectedPresetIdx(idx); },
                className: `p-3.5 rounded-xl border text-left transition-all relative flex flex-col justify-between gap-2 cursor-pointer ${isActive ? 'border-red-500 ring-2 ring-red-500/30 bg-red-500/10' : isSelected ? 'autoos-card border-[var(--accent-primary)] ring-1 ring-[var(--accent-primary)]/40 shadow-sm' : 'autoos-surface hover:border-[var(--accent-primary)]/40'}`,
                children: [
                  (0, E.jsxDEV)('div', {
                    className: 'flex items-start justify-between gap-2',
                    children: [
                      (0, E.jsxDEV)('div', {
                        className: 'flex items-center gap-2',
                        children: [
                          (0, E.jsxDEV)('div', {
                            className: `p-1.5 rounded-lg shrink-0 ${isActive ? 'bg-red-500/20 text-red-500' : isSelected ? 'bg-[var(--accent-primary)]/15 text-[var(--accent-primary)]' : 'autoos-card text-[var(--text-muted)]'}`,
                            children: (0, E.jsxDEV)(IconComp, { className: 'w-4 h-4' }, void 0, false)
                          }, void 0, false),
                          (0, E.jsxDEV)('h5', { className: 'text-xs font-bold text-[var(--text-primary)] leading-tight', children: sc.name }, void 0, false)
                        ]
                      }, void 0, true),
                      (0, E.jsxDEV)('div', {
                        className: 'flex items-center gap-1 shrink-0',
                        children: [
                          isActive ? (0, E.jsxDEV)('span', { className: 'text-[9px] font-mono px-1.5 py-0.5 rounded-full bg-red-600 text-white font-bold uppercase animate-pulse', children: 'Activo' }, void 0, false) : null,
                          (0, E.jsxDEV)('span', { className: 'text-[10px] font-mono px-1.5 py-0.5 rounded autoos-surface text-[var(--text-muted)] border border-[var(--border-color)]', children: `${sc.burstTime}s` }, void 0, false)
                        ]
                      }, void 0, true)
                    ]
                  }, void 0, true),
                  (0, E.jsxDEV)('p', { className: 'text-[11px] text-[var(--text-muted)] leading-relaxed', children: sc.desc }, void 0, false)
                ]
              }, sc.id, true);
            })
          }, void 0, false),
          (0, E.jsxDEV)('div', {
            className: 'p-3 autoos-surface rounded-xl flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono text-[var(--text-muted)]',
            children: [
              (0, E.jsxDEV)('div', {
                className: 'flex items-center gap-2',
                children: [
                  (0, E.jsxDEV)(fe, { className: 'w-3.5 h-3.5 text-[var(--accent-primary)]' }, void 0, false),
                  (0, E.jsxDEV)('span', { children: 'Mitigación RTOS: ' }, void 0, false),
                  (0, E.jsxDEV)('span', { className: 'text-[var(--text-primary)] font-semibold', children: '1. Detectar DTC' }, void 0, false),
                  (0, E.jsxDEV)('span', { children: '→' }, void 0, false),
                  (0, E.jsxDEV)('span', { className: 'text-amber-500 font-semibold', children: '2. Preempt CPU' }, void 0, false),
                  (0, E.jsxDEV)('span', { children: '→' }, void 0, false),
                  (0, E.jsxDEV)('span', { className: 'text-emerald-500 font-semibold', children: '3. Fail-Safe Nominal' }, void 0, false)
                ]
              }, void 0, true),
              lastInjectedPhase ? (0, E.jsxDEV)('span', { className: 'text-red-500 font-bold animate-pulse text-[10px]', children: `⚡ ${lastInjectedPhase}` }, void 0, false) : null
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-[var(--border-color)]',
            children: [
              (0, E.jsxDEV)('button', {
                onClick: handleResetAll,
                className: 'px-3.5 py-2 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold flex items-center gap-1.5 transition font-mono',
                children: [
                  (0, E.jsxDEV)(Pe, { className: 'w-3.5 h-3.5' }, void 0, false),
                  (0, E.jsxDEV)('span', { children: 'Restablecer Sistema a Normal' }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('button', {
                onClick: handleInjectPreset,
                className: `px-4 py-2.5 rounded-xl font-bold text-xs uppercase tracking-wider flex items-center gap-2 shadow-md transition font-mono ${canInject ? 'bg-red-600 hover:bg-red-500 text-white shadow-red-500/20 hover:scale-[1.02] active:scale-[0.98]' : 'bg-[var(--bg-surface)] text-[var(--text-muted)] border border-[var(--border-color)] cursor-not-allowed opacity-60'}`,
                children: [
                  (0, E.jsxDEV)(je, { className: 'w-4 h-4 fill-current' }, void 0, false),
                  (0, E.jsxDEV)('span', { children: '⚡ Disparar Escenario Seleccionado!' }, void 0, false)
                ]
              }, void 0, true)
            ]
          }, void 0, true)
        ]
      }, void 0, true) : null,
      viewSubtab === 'POWERTRAIN' ? (0, E.jsxDEV)('div', {
        className: 'space-y-3 font-mono',
        children: [
          (0, E.jsxDEV)('div', {
            className: 'grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs',
            children: [
              (0, E.jsxDEV)('div', {
                className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)]',
                children: [
                  (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1', children: [(0, E.jsxDEV)(Ve, { className: 'w-3 h-3 text-amber-500' }, void 0, false), ' Motor Delantero'] }, void 0, true),
                  (0, E.jsxDEV)('strong', { className: 'text-lg text-[var(--text-primary)] font-bold', children: '58.4 °C' }, void 0, false),
                  (0, E.jsxDEV)('span', { className: 'text-[10px] text-emerald-500 block', children: 'Nominal (< 85°C)' }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('div', {
                className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)]',
                children: [
                  (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1', children: [(0, E.jsxDEV)(Ve, { className: 'w-3 h-3 text-amber-500' }, void 0, false), ' Motor Trasero'] }, void 0, true),
                  (0, E.jsxDEV)('strong', { className: 'text-lg text-[var(--text-primary)] font-bold', children: '62.1 °C' }, void 0, false),
                  (0, E.jsxDEV)('span', { className: 'text-[10px] text-emerald-500 block', children: 'Nominal (< 85°C)' }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('div', {
                className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)]',
                children: [
                  (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1', children: [(0, E.jsxDEV)(qe, { className: 'w-3 h-3 text-[var(--accent-primary)]' }, void 0, false), ' Inversor IGBT'] }, void 0, true),
                  (0, E.jsxDEV)('strong', { className: 'text-lg text-[var(--accent-primary)] font-bold', children: '49.2 °C' }, void 0, false),
                  (0, E.jsxDEV)('span', { className: 'text-[10px] text-emerald-500 block', children: 'PWM 16 kHz' }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('div', {
                className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)]',
                children: [
                  (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block flex items-center gap-1', children: [(0, E.jsxDEV)(De, { className: 'w-3 h-3 text-emerald-500' }, void 0, false), ' Caudal Refrig.'] }, void 0, true),
                  (0, E.jsxDEV)('strong', { className: 'text-lg text-emerald-600 dark:text-emerald-400 font-bold', children: '14.2 L/min' }, void 0, false),
                  (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] block', children: 'Bomba Lin Bus' }, void 0, false)
                ]
              }, void 0, true)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'grid grid-cols-3 gap-3 text-xs',
            children: [
              (0, E.jsxDEV)('div', {
                className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)]',
                children: [
                  (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block', children: 'RPM Motor' }, void 0, false),
                  (0, E.jsxDEV)('strong', { className: 'text-base text-[var(--text-primary)]', children: '4,850 RPM' }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('div', {
                className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)]',
                children: [
                  (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block', children: 'Torque Inmediato' }, void 0, false),
                  (0, E.jsxDEV)('strong', { className: 'text-base text-[var(--text-primary)]', children: '285 Nm' }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('div', {
                className: 'autoos-surface p-3 rounded-xl border border-[var(--border-color)]',
                children: [
                  (0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase block', children: 'Potencia Neta' }, void 0, false),
                  (0, E.jsxDEV)('strong', { className: 'text-base text-[var(--text-primary)]', children: '142.8 kW' }, void 0, false)
                ]
              }, void 0, true)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('div', {
            className: 'p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-xs flex items-center justify-between',
            children: [
              (0, E.jsxDEV)('span', {
                className: 'flex items-center gap-2 font-bold',
                children: [
                  (0, E.jsxDEV)('span', { className: 'w-2 h-2 rounded-full bg-emerald-500 animate-pulse' }, void 0, false),
                  'Watchdog RTOS ASIL-D Nominal'
                ]
              }, void 0, true),
              (0, E.jsxDEV)('span', { children: 'Aislamiento de Memoria MPU Activo' }, void 0, false)
            ]
          }, void 0, true)
        ]
      }, void 0, true) : null
    ]
  }, void 0, true);
};
"""

app_js = r"""
// ==========================================
// COMPONENT: MAIN APP (st)
// ==========================================
var F = `/app/applet/src/App.tsx`;
function st() {
  var [activeTab, setActiveTab] = (0, _.useState)('SCHEDULER');
  var [theme, setTheme] = (0, _.useState)(function() {
    try {
      return localStorage.getItem('autoos_theme') === 'light' ? 'light' : 'dark';
    } catch (_) { return 'dark'; }
  });
  var [userRole, setUserRole] = (0, _.useState)('mecanico');
  var [rbacAlertMessage, setRbacAlertMessage] = (0, _.useState)(null);
  var [cockpitHtml, setCockpitHtml] = (0, _.useState)(function() {
    return (typeof window !== 'undefined' && window.__AUTOOS_COCKPIT_HTML__) ? window.__AUTOOS_COCKPIT_HTML__ : null;
  });

  // State: Hardware Devices
  var [devices, setDevices] = (0, _.useState)(INITIAL_VEHICLE_DEVICES);

  (0, _.useEffect)(function() {
    if (!cockpitHtml) {
      fetch('/autoos_interactive.html')
        .then(function(res) { return res.ok ? res.text() : ''; })
        .then(function(html) { if (html) setCockpitHtml(html); })
        .catch(function() {});
    }
  }, [cockpitHtml]);

  var iframeRef = (0, _.useRef)(null);
  var syncIframeState = (0, _.useCallback)(function() {
    var iframe = iframeRef.current;
    if (typeof window !== 'undefined') {
      window.__AUTOOS_CURRENT_ROLE__ = userRole;
      window.__AUTOOS_CURRENT_THEME__ = theme;
    }
    if (!iframe) return;
    try {
      if (iframe.contentDocument && iframe.contentDocument.documentElement) {
        if (theme === 'dark') iframe.contentDocument.documentElement.classList.add('dark');
        else iframe.contentDocument.documentElement.classList.remove('dark');
      }
    } catch (_) {}
    try {
      if (iframe.contentWindow) {
        iframe.contentWindow.postMessage({ type: 'AUTOOS_SET_THEME', theme: theme }, '*');
        iframe.contentWindow.postMessage({ type: 'AUTOOS_SET_ROLE', role: userRole }, '*');
        if (typeof iframe.contentWindow.__AUTOOS_SET_THEME__ === 'function') iframe.contentWindow.__AUTOOS_SET_THEME__(theme);
        if (typeof iframe.contentWindow.__AUTOOS_SET_ROLE__ === 'function') iframe.contentWindow.__AUTOOS_SET_ROLE__(userRole);
      }
    } catch (_) {}
  }, [theme, userRole]);

  (0, _.useEffect)(function() {
    try {
      localStorage.setItem('autoos_theme', theme);
    } catch (_) {}
    if (theme === 'dark') document.documentElement.classList.add('dark');
    else document.documentElement.classList.remove('dark');
    syncIframeState();
  }, [theme, syncIframeState]);

  (0, _.useEffect)(function() {
    syncIframeState();
    var t1 = setTimeout(syncIframeState, 60);
    var t2 = setTimeout(syncIframeState, 200);
    var t3 = setTimeout(syncIframeState, 500);
    return function() { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); };
  }, [userRole, activeTab, theme, syncIframeState]);

  (0, _.useEffect)(function() {
    var handleIframeMessage = function(e) {
      if (!e.data) return;
      if (e.data.type === 'AUTOOS_THEME_CHANGED') setTheme(e.data.theme === 'dark' ? 'dark' : 'light');
      if (e.data.type === 'AUTOOS_ROLE_CHANGED') {
        if (['mecanico', 'conductor', 'pasajero'].includes(e.data.role)) setUserRole(e.data.role);
      }
      if (e.data.type === 'AUTOOS_NAVIGATE_TAB') {
        if (e.data.tab === 'SCHEDULER') setActiveTab('SCHEDULER');
      }
      if (e.data.type === 'AUTOOS_REQUEST_SYNC') syncIframeState();
    };
    window.addEventListener('message', handleIframeMessage);
    return function() { window.removeEventListener('message', handleIframeMessage); };
  }, [syncIframeState]);

  var toggleTheme = function() { setTheme(function(prev) { return prev === 'dark' ? 'light' : 'dark'; }); };

  var handleRoleRestricted = function(action) {
    var roleName = userRole === 'pasajero' ? 'Pasajero' : userRole === 'conductor' ? 'Conductor' : 'Mecánico';
    setRbacAlertMessage(`⛔ Acceso Denegado por Política RBAC! El rol actual [${roleName}] no posee privilegios de seguridad para: ${action}. Cambia de rol en la barra superior para continuar.`);
  };

  var [algorithm, setAlgorithm] = (0, _.useState)('RR');
  var [quantum, setQuantum] = (0, _.useState)(2);
  var [speedMs] = (0, _.useState)(800);
  var [isPlaying, setIsPlaying] = (0, _.useState)(false);

  var [isCompareModalOpen, setIsCompareModalOpen] = (0, _.useState)(false);
  var [isNewProcessModalOpen, setIsNewProcessModalOpen] = (0, _.useState)(false);

  var [baseProcesses, setBaseProcesses] = (0, _.useState)(function() {
    return y.map(function(p) { return { ...p, waitingTime: 0, turnaroundTime: 0 }; });
  });

  var [battery, setBattery] = (0, _.useState)({
    level: 85, voltage: 392, temperature: 28, isLowBatteryMode: false, isCriticalBatteryMode: false, autoThrottlingEnabled: true, powerSavingWattsSaved: 0
  });

  var [simState, setSimState] = (0, _.useState)(function() {
    return ee(baseProcesses, 'RR', 2);
  });

  var metrics = ie(simState);
  var activeProcs = simState.processes.filter(function(p) { return p.state !== 'TERMINADO'; });
  var ramUsedMb = activeProcs.reduce(function(acc, p) { return acc + (p.memoryMb || 64); }, 128);
  var ramUsagePercent = Math.min(100, Math.round((ramUsedMb / 2048) * 100));

  var handleReset = (0, _.useCallback)(function(alg, q, procs) {
    setIsPlaying(false);
    var targetAlg = alg || algorithm;
    var targetQ = q !== undefined ? q : quantum;
    var targetProcs = procs || baseProcesses;
    setSimState(ee(targetProcs, targetAlg, targetQ));
  }, [algorithm, quantum, baseProcesses]);

  var handleAlgorithmChange = function(newAlg) {
    if (userRole === 'pasajero') { handleRoleRestricted('Modificar Algoritmo de Planificación de CPU'); return; }
    setAlgorithm(newAlg);
    handleReset(newAlg, quantum);
  };

  var handleQuantumChange = function(newQ) {
    if (userRole === 'pasajero') { handleRoleRestricted('Ajustar Quantum de Tiempo'); return; }
    setQuantum(newQ);
    if (algorithm === 'RR') handleReset(algorithm, newQ);
  };

  var handleStepForward = (0, _.useCallback)(function() {
    if (userRole === 'pasajero') { handleRoleRestricted('Avanzar Ciclos de CPU Manualmente'); return; }
    setSimState(function(prev) { return re(prev, battery.isLowBatteryMode); });
  }, [battery.isLowBatteryMode, userRole]);

  var handleTogglePlay = function() {
    if (userRole === 'pasajero') { handleRoleRestricted('Iniciar / Pausar la Ejecución de CPU'); return; }
    setIsPlaying(!isPlaying);
  };

  var timerRef = (0, _.useRef)(null);
  (0, _.useEffect)(function() {
    if (isPlaying) {
      if (simState.isFinished) { setIsPlaying(false); return; }
      timerRef.current = setInterval(function() {
        setSimState(function(prev) {
          if (prev.isFinished) { setIsPlaying(false); return prev; }
          return re(prev, battery.isLowBatteryMode);
        });
      }, speedMs);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return function() { if (timerRef.current) clearInterval(timerRef.current); };
  }, [isPlaying, speedMs, battery.isLowBatteryMode, simState.isFinished]);

  var handleUpdateBatteryLevel = function(newLevel) {
    var isCritical = newLevel <= 10;
    var isLow = newLevel <= 20;
    var voltage = Math.round(340 + (newLevel / 100) * 60);
    var isLowMode = isLow || isCritical;

    setBattery({
      level: newLevel, voltage: voltage, temperature: isCritical ? 56 : 28, isLowBatteryMode: isLowMode, isCriticalBatteryMode: isCritical, autoThrottlingEnabled: true, powerSavingWattsSaved: isLowMode ? 90 : 0
    });

    setSimState(function(prev) {
      var updatedProcesses = prev.processes.map(function(p) {
        if (isLowMode && (p.category === 'multimedia' || p.category === 'confort' || p.priority >= 4)) {
          if (p.state !== 'TERMINADO') return { ...p, state: 'SUSPENDIDO', suspendedDueToBattery: true };
        } else if (!isLowMode && p.suspendedDueToBattery) {
          return { ...p, state: 'LISTO', suspendedDueToBattery: false };
        }
        return p;
      });

      var updatedReady = isLowMode
        ? prev.readyQueue.filter(function(p) { return p.category !== 'multimedia' && p.category !== 'confort' && p.priority < 4; })
        : [...prev.readyQueue];

      if (!isLowMode) {
        updatedProcesses.forEach(function(p) {
          if (p.state === 'LISTO' && !updatedReady.some(function(rq) { return rq.pid === p.pid; })) updatedReady.push(p);
        });
      }

      return {
        ...prev, processes: updatedProcesses, readyQueue: updatedReady,
        events: [
          {
            id: `evt-bat-${Date.now()}`, time: prev.currentTime, timestamp: new Date().toLocaleTimeString(), type: 'BATTERY_ALERT',
            message: isLowMode ? `⚡ [BATERÍA BAJA ${newLevel}%] Activado Limp-Mode: Procesos de confort y multimedia suspendidos para proteger la tracción y dirección.` : `✓ [BATERÍA NOMINAL ${newLevel}%] Carga restablecida al ${newLevel}%. Procesos reactivados.`,
            severity: isCritical ? 'critical' : isLow ? 'warning' : 'success'
          },
          ...prev.events
        ]
      };
    });
  };

  var handleTogglePowerSaving = function() { handleUpdateBatteryLevel(battery.isLowBatteryMode ? 85 : 18); };

  // Critical Fault Injection with Device Reflection
  var handleInjectCriticalProcess = function(procData, deviceCode, dtc, failureMode) {
    var fullProc = { ...procData, waitingTime: 0, turnaroundTime: 0 };

    if (deviceCode) {
      setDevices(function(prev) {
        return prev.map(function(d) {
          if (d.code === deviceCode) {
            var isCrit = procData.priority === 1;
            return {
              ...d,
              status: isCrit ? 'falla' : 'degradado',
              health: isCrit ? 15 : 60,
              activeDtc: dtc || d.activeDtc || 'U0100-87',
              failureMode: failureMode || procData.name
            };
          }
          return d;
        });
      });
    }

    setBaseProcesses(function(prev) { return [...prev, fullProc]; });

    setSimState(function(prev) {
      var newProc = { ...fullProc };
      var currentT = prev.currentTime;
      var updatedProcesses = [...prev.processes, newProc];
      var updatedRunning = prev.runningProcess;
      var preemptedId = null;
      var newEvents = [...prev.events];
      var updatedReady = [...prev.readyQueue];

      newEvents.unshift({
        id: `evt-crit-inj-${newProc.pid}-${currentT}`, time: currentT, timestamp: new Date().toLocaleTimeString(), type: 'CRITICAL_INJECT',
        message: `🚨 PROCESO CRÍTICO ASIL-D INYECTADO! '${newProc.name}' [DTC: ${dtc || 'U0100'}] (PID ${newProc.pid}, P${newProc.priority}) ingresa a la CPU.`,
        pid: newProc.pid, severity: 'critical'
      });

      if (prev.algorithm === 'PRIORITY_PREEMPTIVE' && updatedRunning && updatedRunning.priority > 1) {
        preemptedId = updatedRunning.pid;
        var preempted = { ...updatedRunning, state: 'LISTO' };
        updatedReady.unshift(preempted);
        newProc.state = 'EJECUTANDO';
        newProc.startTime = currentT;
        newProc.responseTime = 0;
        updatedRunning = newProc;

        newEvents.unshift({
          id: `evt-crit-preempt-${newProc.pid}-${currentT}`, time: currentT, timestamp: new Date().toLocaleTimeString(), type: 'PREEMPTION',
          message: `⚡ DESALOJO PREEMPTIVO! PID ${newProc.pid} (${newProc.name}) desaloja a PID ${preempted.pid} (${preempted.name}) en el núcleo.`,
          pid: newProc.pid, severity: 'critical'
        });
      } else {
        newProc.state = 'LISTO';
        updatedReady.push(newProc);
      }

      return {
        ...prev, processes: updatedProcesses, readyQueue: updatedReady, runningProcess: updatedRunning, preemptedProcessId: preemptedId, events: newEvents
      };
    });

    try {
      if (iframeRef.current && iframeRef.current.contentWindow) {
        iframeRef.current.contentWindow.postMessage({
          type: 'AUTOOS_HARDWARE_FAULT', deviceCode: deviceCode, dtc: dtc, name: procData.name
        }, '*');
      }
    } catch (_) {}
  };

  var handleResetDevice = function(deviceCode) {
    setDevices(function(prev) {
      return prev.map(function(d) {
        if (d.code === deviceCode) return { ...d, status: 'operativo', health: 98, activeDtc: null, failureMode: null };
        return d;
      });
    });

    setSimState(function(prev) {
      return {
        ...prev,
        events: [
          {
            id: `evt-dev-rst-${deviceCode}-${Date.now()}`, time: prev.currentTime, timestamp: new Date().toLocaleTimeString(), type: 'STATE_CHANGE',
            message: `✓ Calibración OBD-II completada: Dispositivo [${deviceCode}] restablecido a OPERATIVO (100% Nominal).`, severity: 'success'
          },
          ...prev.events
        ]
      };
    });

    try {
      if (iframeRef.current && iframeRef.current.contentWindow) {
        iframeRef.current.contentWindow.postMessage({ type: 'AUTOOS_RESET_DEVICE', deviceCode: deviceCode }, '*');
      }
    } catch (_) {}
  };

  var handleResetAllDevices = function() {
    setDevices(INITIAL_VEHICLE_DEVICES);
    setSimState(function(prev) {
      return {
        ...prev,
        events: [
          {
            id: `evt-dev-rstall-${Date.now()}`, time: prev.currentTime, timestamp: new Date().toLocaleTimeString(), type: 'STATE_CHANGE',
            message: `✓ RESTABLECIMIENTO GLOBAL: Todos los subsistemas y buses CAN/Ethernet restablecidos a 100% NOMINAL ASIL-D.`, severity: 'success'
          },
          ...prev.events
        ]
      };
    });

    try {
      if (iframeRef.current && iframeRef.current.contentWindow) {
        iframeRef.current.contentWindow.postMessage({ type: 'AUTOOS_RESET_ALL_FAULTS' }, '*');
      }
    } catch (_) {}
  };

  var handleTriggerQuickFault = function(deviceCode) {
    var dev = devices.find(function(d) { return d.code === deviceCode; }) || INITIAL_VEHICLE_DEVICES[0];
    var dtc = dev.activeDtc || 'P0100-F1';
    var procData = {
      pid: Math.floor(Math.random() * 800) + 200,
      name: `Falla Simulada en ${dev.name.split('/')[0]}`,
      category: dev.subsystem === 'Seguridad Dinámica' ? 'seguridad' : dev.subsystem === 'Sensores' ? 'sensor' : 'control',
      arrivalTime: simState.currentTime,
      burstTime: 4, remainingTime: 4, priority: 1, critical: true, color: '#ef4444', state: 'LISTO', powerConsumptionWatts: 50, cpuUsagePct: 35, memoryMb: 128
    };
    handleInjectCriticalProcess(procData, deviceCode, dtc, 'Prueba de Diagnóstico Forzado OBD-II');
  };

  var handleAddCustomProcess = function(procData) {
    if (userRole === 'pasajero') { handleRoleRestricted('Crear Nuevos Procesos en el Kernel'); return; }
    var fullProc = { ...procData, waitingTime: 0, turnaroundTime: 0 };
    setBaseProcesses(function(prev) { return [...prev, fullProc]; });
    setSimState(function(prev) {
      var newProc = { ...fullProc };
      var isReadyNow = newProc.arrivalTime <= prev.currentTime;
      newProc.state = isReadyNow ? 'LISTO' : 'NUEVO';
      var updatedProcs = [...prev.processes, newProc];
      var updatedReady = isReadyNow ? [...prev.readyQueue, newProc] : [...prev.readyQueue];
      return {
        ...prev, processes: updatedProcs, readyQueue: updatedReady,
        events: [
          {
            id: `evt-add-${newProc.pid}-${prev.currentTime}`, time: prev.currentTime, timestamp: new Date().toLocaleTimeString(), type: 'ARRIVAL',
            message: `Proceso '${newProc.name}' (PID ${newProc.pid}, Ráfaga: ${newProc.burstTime}s, Prio: ${newProc.priority}) añadido.`, pid: newProc.pid, severity: 'info'
          },
          ...prev.events
        ]
      };
    });
  };

  var handleToggleSuspend = function(pid) {
    setSimState(function(prev) {
      var updated = prev.processes.map(function(p) {
        if (p.pid === pid) {
          var nextState = p.state === 'SUSPENDIDO' ? 'LISTO' : 'SUSPENDIDO';
          return { ...p, state: nextState };
        }
        return p;
      });
      var proc = updated.find(function(p) { return p.pid === pid; });
      var ready = [...prev.readyQueue];
      if (proc && proc.state === 'SUSPENDIDO') ready = ready.filter(function(p) { return p.pid !== pid; });
      else if (proc && proc.state === 'LISTO') {
        if (!ready.some(function(p) { return p.pid === pid; })) ready.push(proc);
      }
      return {
        ...prev, processes: updated, readyQueue: ready,
        events: [
          {
            id: `evt-user-susp-${pid}-${prev.currentTime}`, time: prev.currentTime, timestamp: new Date().toLocaleTimeString(), type: 'STATE_CHANGE',
            message: `Estado de PID ${pid} (${proc && proc.name}) cambiado a [${proc && proc.state}].`, pid: pid, severity: 'info'
          },
          ...prev.events
        ]
      };
    });
  };

  var handleTerminateProcess = function(pid) {
    setSimState(function(prev) {
      var proc = prev.processes.find(function(p) { return p.pid === pid; });
      var updated = prev.processes.map(function(p) {
        if (p.pid === pid) {
          return {
            ...p, state: 'TERMINADO', completionTime: prev.currentTime, remainingTime: 0,
            turnaroundTime: prev.currentTime - p.arrivalTime,
            waitingTime: Math.max(0, prev.currentTime - p.arrivalTime - (p.burstTime - p.remainingTime))
          };
        }
        return p;
      });
      var ready = prev.readyQueue.filter(function(p) { return p.pid !== pid; });
      var running = prev.runningProcess;
      if (running && running.pid === pid) running = null;
      return {
        ...prev, processes: updated, readyQueue: ready, runningProcess: running,
        events: [
          {
            id: `evt-kill-${pid}-${prev.currentTime}`, time: prev.currentTime, timestamp: new Date().toLocaleTimeString(), type: 'COMPLETION',
            message: `Proceso PID ${pid} (${proc && proc.name}) finalizado (SIGKILL).`, pid: pid, severity: 'warning'
          },
          ...prev.events
        ]
      };
    });
  };

  var suspendedProcesses = simState.processes.filter(function(p) { return p.state === 'SUSPENDIDO'; });
  var failingDevices = devices.filter(function(d) { return d.status === 'falla' || d.status === 'desconectado'; });
  var degradedDevices = devices.filter(function(d) { return d.status === 'degradado'; });
  var avgHealth = Math.round(devices.reduce(function(acc, d) { return acc + d.health; }, 0) / devices.length);

  var gpsDevice = devices.find(function(d) { return d.code === 'DEV_GPS_01'; });
  var isGpsFailed = gpsDevice && (gpsDevice.status === 'falla' || gpsDevice.status === 'desconectado');
  var gpsActiveDtc = gpsDevice && gpsDevice.activeDtc;

  return (0, E.jsxDEV)('div', {
    className: 'min-h-screen flex flex-col font-sans transition-colors duration-200 bg-[var(--bg-base)] text-[var(--text-primary)]',
    children: [
      (0, E.jsxDEV)('header', {
        className: 'sticky top-0 z-40 autoos-surface border-b px-4 lg:px-8 py-3',
        children: (0, E.jsxDEV)('div', {
          className: 'max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4',
          children: [
            (0, E.jsxDEV)('div', {
              className: 'flex items-center gap-3',
              children: [
                (0, E.jsxDEV)('div', {
                  className: 'p-2 rounded-2xl bg-[var(--accent-primary)]/15 text-[var(--accent-primary)] border border-[var(--accent-primary)]/30 shadow-sm',
                  children: (0, E.jsxDEV)(_e, { className: 'w-6 h-6' }, void 0, false)
                }, void 0, false),
                (0, E.jsxDEV)('div', {
                  children: [
                    (0, E.jsxDEV)('div', {
                      className: 'flex items-center gap-2',
                      children: [
                        (0, E.jsxDEV)('h1', { className: 'text-lg font-serif font-bold text-[var(--text-primary)] tracking-wide', children: ['AutoOS ', (0, E.jsxDEV)('span', { className: 'text-[var(--accent-primary)] font-mono text-xs font-semibold', children: 'v2.5.0' }, void 0, false)] }, void 0, true),
                        (0, E.jsxDEV)('span', {
                          className: `text-[10px] font-mono px-2 py-0.5 rounded-full font-bold flex items-center gap-1 ${failingDevices.length > 0 ? 'bg-red-500/15 text-red-500 border border-red-500/30 animate-pulse' : degradedDevices.length > 0 ? 'bg-amber-500/15 text-amber-500 border border-amber-500/30' : 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'}`,
                          children: [
                            (0, E.jsxDEV)('span', { className: `w-1.5 h-1.5 rounded-full ${failingDevices.length > 0 ? 'bg-red-500 animate-ping' : degradedDevices.length > 0 ? 'bg-amber-500' : 'bg-emerald-500 animate-pulse'}` }, void 0, false),
                            failingDevices.length > 0 ? 'FALLA ACTIVA' : degradedDevices.length > 0 ? 'DEGRADADO' : 'OPERATIVO 100%'
                          ]
                        }, void 0, true)
                      ]
                    }, void 0, true),
                    (0, E.jsxDEV)('p', { className: 'text-[11px] text-[var(--text-muted)]', children: 'Sistema Operativo para Vehículo Inteligente — RTOS ISO 26262 ASIL-D' }, void 0, false)
                  ]
                }, void 0, true)
              ]
            }, void 0, true),
            (0, E.jsxDEV)('div', {
              className: 'flex items-center autoos-card p-1 rounded-2xl border text-xs font-mono',
              children: [
                (0, E.jsxDEV)('button', {
                  onClick: function() { setActiveTab('SCHEDULER'); },
                  className: `px-3.5 py-2 rounded-xl font-bold flex items-center gap-2 transition-all ${activeTab === 'SCHEDULER' ? 'bg-[var(--accent-primary)] text-white shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'}`,
                  children: [(0, E.jsxDEV)(Ce, { className: 'w-4 h-4' }, void 0, false), (0, E.jsxDEV)('span', { children: 'Planificador & Simuladores' }, void 0, false)]
                }, void 0, true),
                (0, E.jsxDEV)('button', {
                  onClick: function() { setActiveTab('COCKPIT'); },
                  className: `px-3.5 py-2 rounded-xl font-bold flex items-center gap-2 transition-all ${activeTab === 'COCKPIT' ? 'bg-[var(--accent-primary)] text-white shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'}`,
                  children: [(0, E.jsxDEV)(_e, { className: 'w-4 h-4' }, void 0, false), (0, E.jsxDEV)('span', { children: 'Cockpit AutoOS Completo' }, void 0, false)]
                }, void 0, true)
              ]
            }, void 0, true),
            (0, E.jsxDEV)('div', {
              className: 'flex items-center gap-2.5 text-xs font-mono',
              children: [
                (0, E.jsxDEV)('div', {
                  className: 'flex items-center gap-1.5 px-3 py-1.5 rounded-xl autoos-card border text-[var(--text-primary)]',
                  children: [
                    (0, E.jsxDEV)(Le, { className: 'w-3.5 h-3.5 text-[var(--accent-primary)]' }, void 0, false),
                    (0, E.jsxDEV)('span', { className: 'text-[11px] text-[var(--text-muted)] font-semibold', children: 'Usuario:' }, void 0, false),
                    (0, E.jsxDEV)('select', {
                      value: userRole,
                      onChange: function(e) { setUserRole(e.target.value); },
                      className: 'bg-transparent text-[var(--text-primary)] font-bold text-xs focus:outline-none cursor-pointer',
                      children: [
                        (0, E.jsxDEV)('option', { value: 'mecanico', className: 'text-black dark:text-white dark:bg-[#180E24]', children: '🔧 Carlos Vélez (Mecánico / Admin)' }, void 0, false),
                        (0, E.jsxDEV)('option', { value: 'conductor', className: 'text-black dark:text-white dark:bg-[#180E24]', children: '🚗 Laura Gómez (Conductora)' }, void 0, false),
                        (0, E.jsxDEV)('option', { value: 'pasajero', className: 'text-black dark:text-white dark:bg-[#180E24]', children: '👤 Andrés Rivera (Pasajero)' }, void 0, false)
                      ]
                    }, void 0, true)
                  ]
                }, void 0, true),
                (0, E.jsxDEV)('div', {
                  className: 'hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl autoos-card border text-[var(--text-primary)]',
                  children: [(0, E.jsxDEV)(me, { className: 'w-3.5 h-3.5 text-[var(--accent-primary)]' }, void 0, false), (0, E.jsxDEV)('span', { children: `${battery.level}% (${battery.voltage}V)` }, void 0, false)]
                }, void 0, true),
                (0, E.jsxDEV)('button', {
                  onClick: toggleTheme,
                  className: 'p-2 rounded-xl autoos-card border hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] transition flex items-center gap-1.5',
                  children: [
                    theme === 'dark' ? (0, E.jsxDEV)(ze, { className: 'w-4 h-4 text-amber-400' }, void 0, false) : (0, E.jsxDEV)(ke, { className: 'w-4 h-4 text-[#391214]' }, void 0, false),
                    (0, E.jsxDEV)('span', { className: 'hidden md:inline text-[11px]', children: theme === 'dark' ? 'Modo Claro' : 'Modo Oscuro' }, void 0, false)
                  ]
                }, void 0, true)
              ]
            }, void 0, true)
          ]
        }, void 0, true)
      }, void 0, false),
      rbacAlertMessage ? (0, E.jsxDEV)('div', {
        className: 'fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200',
        children: (0, E.jsxDEV)('div', {
          className: 'relative w-full max-w-md autoos-card border-2 border-red-500 rounded-3xl p-6 shadow-2xl space-y-4',
          children: [
            (0, E.jsxDEV)('div', {
              className: 'flex items-center justify-between pb-2 border-b border-[var(--border-color)]',
              children: [
                (0, E.jsxDEV)('div', {
                  className: 'flex items-center gap-2.5 text-red-500 font-bold',
                  children: [(0, E.jsxDEV)(Fe, { className: 'w-6 h-6 animate-bounce' }, void 0, false), (0, E.jsxDEV)('h3', { className: 'font-serif text-base text-[var(--text-primary)]', children: 'Control de Acceso RBAC' }, void 0, false)]
                }, void 0, true),
                (0, E.jsxDEV)('button', { onClick: function() { setRbacAlertMessage(null); }, className: 'p-1 rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)]', children: (0, E.jsxDEV)(Ke, { className: 'w-5 h-5' }, void 0, false) }, void 0, false)
              ]
            }, void 0, true),
            (0, E.jsxDEV)('p', { className: 'text-xs text-[var(--text-primary)] leading-relaxed', children: rbacAlertMessage }, void 0, false),
            (0, E.jsxDEV)('div', { className: 'flex justify-end pt-2', children: (0, E.jsxDEV)('button', { onClick: function() { setRbacAlertMessage(null); }, className: 'px-4 py-2 rounded-xl bg-[var(--accent-primary)] text-white text-xs font-bold', children: 'Entendido' }, void 0, false) }, void 0, false)
          ]
        }, void 0, true)
      }, void 0, false) : null,
      (0, E.jsxDEV)('main', {
        className: `flex-1 max-w-7xl w-full mx-auto p-4 lg:p-8 space-y-6 ${activeTab === 'SCHEDULER' ? '' : 'hidden'}`,
        children: [
          (0, E.jsxDEV)('div', {
            className: `p-4 rounded-2xl border transition-all duration-300 shadow-md flex flex-wrap items-center justify-between gap-3 font-mono text-xs ${failingDevices.length > 0 ? 'bg-red-500/15 border-red-500 text-red-600 dark:text-red-400 ring-2 ring-red-500/30' : degradedDevices.length > 0 ? 'bg-amber-500/15 border-amber-500 text-amber-600 dark:text-amber-400' : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-600 dark:text-emerald-400'}`,
            children: [
              (0, E.jsxDEV)('div', {
                className: 'flex items-center gap-3',
                children: [
                  (0, E.jsxDEV)('div', {
                    className: `p-2 rounded-xl shrink-0 ${failingDevices.length > 0 ? 'bg-red-600 text-white animate-bounce' : degradedDevices.length > 0 ? 'bg-amber-500 text-white' : 'bg-emerald-500/20 text-emerald-500'}`,
                    children: failingDevices.length > 0 ? (0, E.jsxDEV)(Fe, { className: 'w-5 h-5' }, void 0, false) : degradedDevices.length > 0 ? (0, E.jsxDEV)(We, { className: 'w-5 h-5' }, void 0, false) : (0, E.jsxDEV)(ye, { className: 'w-5 h-5' }, void 0, false)
                  }, void 0, false),
                  (0, E.jsxDEV)('div', {
                    children: [
                      (0, E.jsxDEV)('div', {
                        className: 'font-bold text-sm flex items-center gap-2',
                        children: [
                          (0, E.jsxDEV)('span', { children: failingDevices.length > 0 ? `🚨 ALERTA ASIL-D: ${failingDevices.length} FALLA(S) ACTIVA(S) EN HARDWARE` : degradedDevices.length > 0 ? `⚠️ ADVERTENCIA: ${degradedDevices.length} SUBSISTEMA(S) EN MODO DEGRADADO` : '✓ SISTEMA VEHICULAR NOMINAL (100% OPERATIVO)' }, void 0, false),
                          (0, E.jsxDEV)('span', { className: 'text-[10px] px-2 py-0.5 rounded-full bg-slate-900/10 dark:bg-white/10 font-bold', children: `Salud: ${avgHealth}%` }, void 0, false)
                        ]
                      }, void 0, true),
                      (0, E.jsxDEV)('p', {
                        className: 'text-[11px] opacity-90',
                        children: failingDevices.length > 0
                          ? `Fallas detectadas en: ${failingDevices.map(function(d) { return `${d.name.split('/')[0]} [${d.activeDtc || 'DTC'}]`; }).join(', ')}. Conmutado a algoritmos de contingencia pre-emptivos.`
                          : degradedDevices.length > 0
                          ? `Subsistemas con rendimiento reducido: ${degradedDevices.map(function(d) { return d.name.split('/')[0]; }).join(', ')}.`
                          : 'Buses CAN-FD, Automotive Ethernet y LIN sincronizados. Planificación de tiempo real en rango de latencia < 2ms.'
                      }, void 0, false)
                    ]
                  }, void 0, true)
                ]
              }, void 0, true),
              failingDevices.length > 0 ? (0, E.jsxDEV)('button', {
                onClick: handleResetAllDevices,
                className: 'px-4 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white font-bold text-xs uppercase tracking-wider shadow-md hover:scale-105 transition flex items-center gap-1.5',
                children: [(0, E.jsxDEV)(Pe, { className: 'w-4 h-4' }, void 0, false), (0, E.jsxDEV)('span', { children: 'Restablecer Fallas' }, void 0, false)]
              }, void 0, true) : null
            ]
          }, void 0, true),
          (0, E.jsxDEV)('section', {
            className: 'autoos-card rounded-3xl p-5 shadow-xl',
            children: (0, E.jsxDEV)('div', {
              className: 'flex flex-wrap items-center justify-between gap-4',
              children: [
                (0, E.jsxDEV)('div', {
                  className: 'space-y-1.5',
                  children: [
                    (0, E.jsxDEV)('label', { className: 'text-[11px] font-mono text-[var(--text-muted)] uppercase tracking-wider block font-bold', children: 'Algoritmo de Planificación:' }, void 0, false),
                    (0, E.jsxDEV)('div', {
                      className: 'flex flex-wrap gap-1.5 autoos-surface p-1.5 rounded-2xl',
                      children: [
                        (0, E.jsxDEV)('button', {
                          onClick: function() { handleAlgorithmChange('FCFS'); },
                          className: `px-3 py-1.5 rounded-xl text-xs font-mono font-bold transition-all ${algorithm === 'FCFS' ? 'bg-[var(--accent-primary)] text-white shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'}`,
                          children: 'FCFS (First-Come)'
                        }, void 0, false),
                        (0, E.jsxDEV)('button', {
                          onClick: function() { handleAlgorithmChange('RR'); },
                          className: `px-3 py-1.5 rounded-xl text-xs font-mono font-bold transition-all ${algorithm === 'RR' ? 'bg-[var(--accent-primary)] text-white shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'}`,
                          children: 'Round Robin (RR)'
                        }, void 0, false),
                        (0, E.jsxDEV)('button', {
                          onClick: function() { handleAlgorithmChange('PRIORITY'); },
                          className: `px-3 py-1.5 rounded-xl text-xs font-mono font-bold transition-all ${algorithm === 'PRIORITY' ? 'bg-[var(--accent-primary)] text-white shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'}`,
                          children: 'Prioridad No Apropiativa'
                        }, void 0, false),
                        (0, E.jsxDEV)('button', {
                          onClick: function() { handleAlgorithmChange('PRIORITY_PREEMPTIVE'); },
                          className: `px-3 py-1.5 rounded-xl text-xs font-mono font-bold transition-all ${algorithm === 'PRIORITY_PREEMPTIVE' ? 'bg-[var(--accent-primary)] text-white shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'}`,
                          children: 'Prioridad Apropiativa (Preemptive)'
                        }, void 0, false)
                      ]
                    }, void 0, true)
                  ]
                }, void 0, true),
                algorithm === 'RR' ? (0, E.jsxDEV)('div', {
                  className: 'space-y-1.5',
                  children: [
                    (0, E.jsxDEV)('label', { className: 'text-[11px] font-mono text-[var(--text-muted)] uppercase tracking-wider block font-bold', children: 'Quantum (q):' }, void 0, false),
                    (0, E.jsxDEV)('div', {
                      className: 'flex items-center gap-1.5 autoos-surface p-1.5 rounded-2xl font-mono text-xs',
                      children: [1, 2, 3, 4, 5].map(function(q) {
                        return (0, E.jsxDEV)('button', {
                          onClick: function() { handleQuantumChange(q); },
                          className: `w-7 h-7 rounded-xl font-bold transition ${quantum === q ? 'bg-[var(--accent-primary)] text-white' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'}`,
                          children: `${q}s`
                        }, q, false);
                      })
                    }, void 0, true)
                  ]
                }, void 0, true) : null,
                (0, E.jsxDEV)('div', {
                  className: 'space-y-1.5',
                  children: [
                    (0, E.jsxDEV)('label', { className: 'text-[11px] font-mono text-[var(--text-muted)] uppercase tracking-wider block font-bold', children: 'Controles de Simulación:' }, void 0, false),
                    (0, E.jsxDEV)('div', {
                      className: 'flex items-center gap-2',
                      children: [
                        (0, E.jsxDEV)('button', {
                          onClick: handleTogglePlay, disabled: simState.isFinished,
                          className: `px-4 py-2 rounded-xl font-bold text-xs flex items-center gap-2 transition shadow-md ${isPlaying ? 'bg-amber-500 hover:bg-amber-400 text-white' : 'bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50'}`,
                          children: [isPlaying ? (0, E.jsxDEV)(Ae, { className: 'w-4 h-4 fill-current' }, void 0, false) : (0, E.jsxDEV)(je, { className: 'w-4 h-4 fill-current' }, void 0, false), (0, E.jsxDEV)('span', { children: isPlaying ? 'Pausar' : 'Reproducir' }, void 0, false)]
                        }, void 0, true),
                        (0, E.jsxDEV)('button', {
                          onClick: handleStepForward, disabled: isPlaying || simState.isFinished,
                          className: 'px-3 py-2 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-50',
                          children: [(0, E.jsxDEV)(Re, { className: 'w-4 h-4 text-[var(--accent-primary)]' }, void 0, false), (0, E.jsxDEV)('span', { children: 'Paso (+1s)' }, void 0, false)]
                        }, void 0, true),
                        (0, E.jsxDEV)('button', {
                          onClick: function() { handleReset(); },
                          className: 'px-3 py-2 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-muted)] hover:text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold flex items-center gap-1.5 transition',
                          children: [(0, E.jsxDEV)(Pe, { className: 'w-4 h-4' }, void 0, false), (0, E.jsxDEV)('span', { children: 'Reiniciar' }, void 0, false)]
                        }, void 0, true),
                        (0, E.jsxDEV)('button', {
                          onClick: function() { setIsCompareModalOpen(true); },
                          className: 'px-3 py-2 rounded-xl autoos-surface hover:bg-[var(--bg-card-hover)] text-[var(--text-primary)] border border-[var(--border-color)] text-xs font-semibold flex items-center gap-1.5 transition',
                          children: [(0, E.jsxDEV)(C, { className: 'w-4 h-4 text-[var(--accent-primary)]' }, void 0, false), (0, E.jsxDEV)('span', { children: 'Comparar' }, void 0, false)]
                        }, void 0, true),
                        (0, E.jsxDEV)('button', {
                          onClick: function() {
                            if (userRole === 'pasajero') { handleRoleRestricted('Crear Procesos en el Sistema'); return; }
                            setIsNewProcessModalOpen(true);
                          },
                          className: 'px-3.5 py-2 rounded-xl bg-[var(--accent-primary)] text-white font-bold text-xs flex items-center gap-1.5 transition shadow-sm hover:opacity-90',
                          children: [(0, E.jsxDEV)(xe, { className: 'w-4 h-4' }, void 0, false), (0, E.jsxDEV)('span', { children: 'Añadir' }, void 0, false)]
                        }, void 0, true)
                      ]
                    }, void 0, true)
                  ]
                }, void 0, true)
              ]
            }, void 0, true)
          }, void 0, false),
          (0, E.jsxDEV)('section', {
            className: 'grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5 font-mono',
            children: [
              (0, E.jsxDEV)('div', { className: 'autoos-card p-3.5 rounded-2xl shadow-sm', children: [(0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase tracking-wider block font-bold', children: 'Reloj Simulado' }, void 0, false), (0, E.jsxDEV)('strong', { className: 'text-xl text-[var(--accent-primary)] font-bold', children: `t = ${simState.currentTime}s` }, void 0, false)] }, void 0, true),
              (0, E.jsxDEV)('div', { className: 'autoos-card p-3.5 rounded-2xl shadow-sm', children: [(0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase tracking-wider block font-bold', children: 'Uso de CPU (Bajo=Óptimo)' }, void 0, false), (0, E.jsxDEV)('strong', { className: `text-xl font-bold ${metrics.cpuUtilization < 50 ? 'text-emerald-500 dark:text-emerald-400' : (metrics.cpuUtilization <= 75 ? 'text-amber-500' : 'text-red-500 animate-pulse')}`, children: `${metrics.cpuUtilization}%` }, void 0, false)] }, void 0, true),
              (0, E.jsxDEV)('div', { className: 'autoos-card p-3.5 rounded-2xl shadow-sm', children: [(0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase tracking-wider block font-bold', children: 'Uso de RAM (Bajo=Óptimo)' }, void 0, false), (0, E.jsxDEV)('strong', { className: `text-xl font-bold ${ramUsagePercent < 50 ? 'text-emerald-500 dark:text-emerald-400' : (ramUsagePercent <= 75 ? 'text-amber-500' : 'text-red-500 animate-pulse')}`, children: `${ramUsagePercent}%` }, void 0, false)] }, void 0, true),
              (0, E.jsxDEV)('div', { className: 'autoos-card p-3.5 rounded-2xl shadow-sm', children: [(0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase tracking-wider block font-bold', children: 'T. Espera Prom' }, void 0, false), (0, E.jsxDEV)('strong', { className: 'text-xl text-amber-600 dark:text-amber-400 font-bold', children: `${metrics.averageWaitingTime}s` }, void 0, false)] }, void 0, true),
              (0, E.jsxDEV)('div', { className: 'autoos-card p-3.5 rounded-2xl shadow-sm', children: [(0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase tracking-wider block font-bold', children: 'T. Retorno Prom' }, void 0, false), (0, E.jsxDEV)('strong', { className: 'text-xl text-[var(--text-primary)] font-bold', children: `${metrics.averageTurnaroundTime}s` }, void 0, false)] }, void 0, true),
              (0, E.jsxDEV)('div', { className: 'autoos-card p-3.5 rounded-2xl shadow-sm', children: [(0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase tracking-wider block font-bold', children: 'Conmutaciones' }, void 0, false), (0, E.jsxDEV)('strong', { className: 'text-xl text-[var(--text-primary)] font-bold', children: `${metrics.contextSwitches}` }, void 0, false)] }, void 0, true),
              (0, E.jsxDEV)('div', { className: 'autoos-card p-3.5 rounded-2xl shadow-sm', children: [(0, E.jsxDEV)('span', { className: 'text-[10px] text-[var(--text-muted)] uppercase tracking-wider block font-bold', children: 'Completados' }, void 0, false), (0, E.jsxDEV)('strong', { className: 'text-xl text-emerald-600 dark:text-emerald-400 font-bold', children: `${metrics.completedCount} / ${metrics.totalProcesses}` }, void 0, false)] }, void 0, true)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('section', {
            children: (0, E.jsxDEV)(rt_hw, {
              devices: devices, onResetDevice: handleResetDevice, onResetAllDevices: handleResetAllDevices, onTriggerQuickFault: handleTriggerQuickFault, userRole: userRole, onRoleRestricted: handleRoleRestricted
            }, void 0, false)
          }, void 0, false),
          (0, E.jsxDEV)('section', {
            children: (0, E.jsxDEV)(rt_gps, {
              isDeviceFailed: isGpsFailed, activeDtc: gpsActiveDtc, userRole: userRole, onRoleRestricted: handleRoleRestricted, batteryLevel: battery.level
            }, void 0, false)
          }, void 0, false),
          (0, E.jsxDEV)('section', {
            children: (0, E.jsxDEV)(Ye, {
              slots: simState.ganttSlots, currentTime: simState.currentTime, totalTime: simState.currentTime, processes: simState.processes
            }, void 0, false)
          }, void 0, false),
          (0, E.jsxDEV)('section', {
            className: 'grid grid-cols-1 lg:grid-cols-3 gap-6',
            children: [
              (0, E.jsxDEV)('div', {
                className: 'lg:col-span-1',
                children: (0, E.jsxDEV)(Ze, {
                  runningProcess: simState.runningProcess, algorithm: simState.algorithm, quantum: simState.quantum, quantumRemaining: simState.quantumRemaining, preemptedProcessId: simState.preemptedProcessId, contextSwitches: simState.contextSwitchCount, currentTime: simState.currentTime, isLowBatteryActive: battery.isLowBatteryMode
                }, void 0, false)
              }, void 0, false),
              (0, E.jsxDEV)('div', {
                className: 'lg:col-span-2',
                children: (0, E.jsxDEV)(et, {
                  readyQueue: simState.readyQueue, algorithm: simState.algorithm, suspendedProcesses: suspendedProcesses
                }, void 0, false)
              }, void 0, false)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('section', {
            className: 'space-y-3',
            children: [
              (0, E.jsxDEV)('div', {
                className: 'flex items-center gap-2 px-1',
                children: [
                  (0, E.jsxDEV)(fe, { className: 'w-4 h-4 text-[var(--accent-primary)]' }, void 0, false),
                  (0, E.jsxDEV)('h3', { className: 'text-sm font-serif font-bold text-[var(--text-primary)] uppercase tracking-wider', children: 'Simuladores de Contingencia y Gestión Energética' }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('div', {
                className: 'grid grid-cols-1 lg:grid-cols-2 gap-6',
                children: [
                  (0, E.jsxDEV)($e, {
                    battery: battery, onUpdateBatteryLevel: handleUpdateBatteryLevel, onTogglePowerSaving: handleTogglePowerSaving, wattsSaved: battery.powerSavingWattsSaved, suspendedCount: suspendedProcesses.length, userRole: userRole, onRoleRestricted: handleRoleRestricted
                  }, void 0, false),
                  (0, E.jsxDEV)(tt, {
                    onInjectCriticalProcess: handleInjectCriticalProcess, onResetDevice: handleResetDevice, onResetAllScenarios: handleResetAllDevices, currentTime: simState.currentTime, userRole: userRole, onRoleRestricted: handleRoleRestricted
                  }, void 0, false)
                ]
              }, void 0, true)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('section', {
            className: 'grid grid-cols-1 lg:grid-cols-3 gap-6',
            children: [
              (0, E.jsxDEV)('div', {
                className: 'lg:col-span-2',
                children: (0, E.jsxDEV)(Qe, {
                  processes: simState.processes, onToggleSuspend: handleToggleSuspend, onTerminate: handleTerminateProcess, currentTime: simState.currentTime, userRole: userRole, onRoleRestricted: handleRoleRestricted
                }, void 0, false)
              }, void 0, false),
              (0, E.jsxDEV)('div', {
                className: 'lg:col-span-1',
                children: (0, E.jsxDEV)(ot, { events: simState.events }, void 0, false)
              }, void 0, false)
            ]
          }, void 0, true)
        ]
      }, void 0, true),
      (0, E.jsxDEV)('main', {
        className: `flex-1 w-full flex flex-col ${activeTab === 'COCKPIT' ? '' : 'hidden'}`,
        children: [
          (0, E.jsxDEV)('div', {
            className: 'autoos-surface border-b px-6 py-2.5 flex items-center justify-between text-xs font-mono text-[var(--text-muted)]',
            children: [
              (0, E.jsxDEV)('span', {
                className: 'flex items-center gap-2',
                children: [
                  (0, E.jsxDEV)(_e, { className: 'w-4 h-4 text-[var(--accent-primary)]' }, void 0, false),
                  (0, E.jsxDEV)('span', { className: 'text-[var(--text-primary)] font-semibold', children: 'Cockpit AutoOS Completo (Velocímetro, Medidores, Audio Player, Chat y Cámaras)' }, void 0, false)
                ]
              }, void 0, true),
              (0, E.jsxDEV)('span', {
                className: `font-bold flex items-center gap-1.5 ${failingDevices.length > 0 ? 'text-red-500 animate-pulse' : degradedDevices.length > 0 ? 'text-amber-500' : 'text-emerald-600 dark:text-emerald-400'}`,
                children: [
                  (0, E.jsxDEV)('span', { className: `w-2 h-2 rounded-full ${failingDevices.length > 0 ? 'bg-red-500 animate-ping' : degradedDevices.length > 0 ? 'bg-amber-500' : 'bg-emerald-500 animate-pulse'}` }, void 0, false),
                  failingDevices.length > 0 ? `Falla en ${failingDevices.length} Subsistema(s)` : degradedDevices.length > 0 ? 'Rendimiento Degradado' : 'Sistemas Activos 100%'
                ]
              }, void 0, true)
            ]
          }, void 0, true),
          (0, E.jsxDEV)('iframe', {
            ref: iframeRef, onLoad: syncIframeState,
            src: cockpitHtml ? void 0 : '/autoos_interactive.html',
            srcDoc: cockpitHtml || void 0,
            title: 'AutoOS Cockpit Completo',
            className: 'w-full flex-1 border-none',
            style: { minHeight: 'calc(100vh - 120px)' }
          }, void 0, false)
        ]
      }, void 0, true),
      (0, E.jsxDEV)('footer', {
        className: 'autoos-surface border-t text-xs text-[var(--text-muted)] py-3.5 px-6 text-center font-mono',
        children: (0, E.jsxDEV)('div', {
          className: 'max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2',
          children: [
            (0, E.jsxDEV)('span', { children: 'AutoOS — Sistema Operativo Vehicular' }, void 0, false),
            (0, E.jsxDEV)('span', { className: 'text-[var(--accent-primary)] font-bold', children: theme === 'dark' ? 'Tema: Purple Night (Oscuro)' : 'Tema: Soft Dove (Claro)' }, void 0, false),
            (0, E.jsxDEV)('span', {
              className: 'text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5 font-bold',
              children: [(0, E.jsxDEV)(ye, { className: 'w-3.5 h-3.5' }, void 0, false), ' FCFS • Round Robin • Prioridad • Batería Baja • Falla Configurable • GPS Dinámico']
            }, void 0, true)
          ]
        }, void 0, false)
      }, void 0, false),
      (0, E.jsxDEV)(nt, {
        isOpen: isCompareModalOpen, onClose: function() { setIsCompareModalOpen(false); }, processes: baseProcesses, quantum: quantum
      }, void 0, false),
      (0, E.jsxDEV)(it, {
        isOpen: isNewProcessModalOpen, onClose: function() { setIsNewProcessModalOpen(false); }, onAddProcess: handleAddCustomProcess, currentTime: simState.currentTime
      }, void 0, false)
    ]
  }, void 0, true);
}

(0, v.createRoot)(document.getElementById('root')).render((0, E.jsxDEV)(st, {}, void 0, false));
"""

new_bundle = base_js + custom_js + middle_components + app_js

with open('web/dist/assets/index-1GvPeIaz.js', 'w', encoding='utf-8') as f:
    f.write(new_bundle)

print('Successfully created and saved web/dist/assets/index-1GvPeIaz.js! Length:', len(new_bundle))
