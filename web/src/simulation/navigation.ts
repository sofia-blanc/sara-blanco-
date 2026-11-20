/**
 * AUTOOS V11 — Navegación didáctica conectada al motor de recursos.
 *
 * Las coordenadas y longitudes son trayectos de DEMOSTRACIÓN, no indicaciones
 * de tráfico ni rutas verificadas por un proveedor de mapas. Un tick equivale
 * a un minuto virtual; el gasto de energía lo aplica App mediante el motor V9.
 *
 * Un fallo GNSS congela la última posición válida (sin inventar coordenadas),
 * aunque el odómetro de la ruta virtual y el reloj siguen avanzando.
 */
export type RouteId = 'norte' | 'centro' | 'aeropuerto';
export type NavigationSignal = 'RTK' | 'DEGRADADA' | 'SIN_GPS';

export interface DemoRoute {
  id: RouteId;
  name: string;
  destination: string;
  km: number;
  coordinates: readonly [number, number][];
  mapPoints: readonly [number, number][];
}

export const DEMO_ROUTES: readonly DemoRoute[] = [
  { id: 'norte', name: 'Corredor Norte', destination: 'Terminal de carga de prueba', km: 14.4,
    coordinates: [[4.6097,-74.0817],[4.622,-74.078],[4.632,-74.072],[4.65,-74.065],[4.674,-74.055]],
    mapPoints: [[80,345],[260,300],[390,185],[590,240],[770,93]] },
  { id: 'centro', name: 'Circuito Central', destination: 'Estación de control virtual', km: 8.6,
    coordinates: [[4.6097,-74.0817],[4.613,-74.087],[4.607,-74.093],[4.601,-74.089],[4.596,-74.080]],
    mapPoints: [[92,110],[235,255],[414,202],[589,322],[780,282]] },
  { id: 'aeropuerto', name: 'Ruta Aérea', destination: 'Punto de transferencia simulado', km: 12.1,
    coordinates: [[4.6097,-74.0817],[4.615,-74.097],[4.63,-74.115],[4.655,-74.129],[4.685,-74.139]],
    mapPoints: [[102,95],[263,154],[410,258],[620,260],[795,395]] },
];

export interface MissionState {
  routeId: RouteId;
  active: boolean;
  completed: boolean;
  elapsedMin: number;
  distanceKm: number;
  speedKmh: number;
  latitude: number;
  longitude: number;
  signal: NavigationSignal;
}

export function currentRoute(id: RouteId): DemoRoute {
  return DEMO_ROUTES.find(r => r.id === id) ?? DEMO_ROUTES[0];
}

function interpolate(points: readonly [number,number][], fraction: number): [number,number] {
  const f = Math.max(0,Math.min(.999999, fraction)) * (points.length - 1);
  const index = Math.floor(f);
  const t = f - index;
  return [points[index][0] + (points[index+1][0]-points[index][0])*t,
          points[index][1] + (points[index+1][1]-points[index][1])*t];
}

export function createMission(routeId: RouteId = 'norte'): MissionState {
  const route = currentRoute(routeId);
  return {routeId, active:false, completed:false, elapsedMin:0, distanceKm:0, speedKmh:45,
    latitude:route.coordinates[0][0],longitude:route.coordinates[0][1],signal:'RTK'};
}

export function startMission(routeId: RouteId, speedKmh=45): MissionState {
  const state = createMission(routeId);
  return {...state,active:true,speedKmh:Math.min(110,Math.max(0,speedKmh))};
}

export function advanceMission(state:MissionState, gpsWorking:boolean, speedKmh=state.speedKmh):MissionState {
  if(!state.active || state.completed) return state;
  const route = currentRoute(state.routeId);
  const speed = Math.max(0,Math.min(110,speedKmh));
  const distanceKm = Math.min(route.km, state.distanceKm + speed/60);
  const completed = distanceKm >= route.km;
  const coordinate = gpsWorking ? interpolate(route.coordinates, distanceKm/route.km) : [state.latitude,state.longitude];
  return {...state, distanceKm, speedKmh:speed, elapsedMin:state.elapsedMin+1,
    latitude:coordinate[0], longitude:coordinate[1],signal:gpsWorking?'RTK':'SIN_GPS',
    completed,active:!completed};
}

export function routeProgress(state:MissionState):number {
  return Math.max(0,Math.min(1,state.distanceKm/currentRoute(state.routeId).km));
}

export function etaMinutes(state:MissionState):number | null {
  if(state.speedKmh <= 0) return null;
  return Math.ceil((currentRoute(state.routeId).km-state.distanceKm)/state.speedKmh*60);
}

export interface MissionEvent {
  id: string;
  tick: number;
  timestamp: string;
  kind: 'GPS'|'RUTA'|'SISTEMA'|'NUBE';
  severity: 'info'|'warning'|'critical';
  message: string;
}
