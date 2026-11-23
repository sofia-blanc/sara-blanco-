/**
 * AutoOS V19 - reglas DETERMINISTAS del minijuego.
 * No usa DOM, React, Supabase ni altera procesos por su cuenta.
 * Recibe un estado y devuelve otro; SimulationCenter conecta los efectos reales.
 */
export type DrivingLane = 0 | 1 | 2;
export type HazardKind = 'obstacle' | 'energy' | 'camera' | 'cpu';
export interface DrivingHazard {
  id: number;
  lane: DrivingLane;
  progress: number; // 0: horizonte; 1: sobre el conductor
  kind: HazardKind;
}
export interface DrivingIncident {
  id: number;
  kind: HazardKind;
  lane: DrivingLane;
  collision: boolean;
}
export interface DrivingGameState {
  lane: DrivingLane;
  frame: number;
  hazards: DrivingHazard[];
  collisions: number;
  avoided: number;
  nextId: number;
}
export const GAME_FRAME_MS = 120;
export const SPAWN_EVERY_FRAMES = 26;
export const HIT_PROGRESS = 0.82;
const HAZARD_PATTERN: readonly HazardKind[] = ['obstacle','energy','camera','cpu'];
const LANE_PATTERN: readonly DrivingLane[] = [1,0,2,1,2,0,1,2];

export function newDrivingGame(): DrivingGameState {
  return {lane:1,frame:0,hazards:[],collisions:0,avoided:0,nextId:0};
}

export function steerDrivingGame(s: DrivingGameState, direction: -1 | 1): DrivingGameState {
  const lane = Math.max(0,Math.min(2,s.lane+direction)) as DrivingLane;
  return lane===s.lane ? s : {...s,lane};
}

export function lanePosition(lane: DrivingLane, progress: number): number {
  const p = Math.max(0,Math.min(1,progress));
  // Los carriles se separan hacia el espectador: perspectiva de la carretera.
  return 720 + (lane-1) * (42+315*p);
}

export function advanceDrivingGame(s: DrivingGameState, speedKmh = 65): {state: DrivingGameState; incidents: DrivingIncident[]} {
  const frame = s.frame+1;
  // La aproximación de peligros depende de la velocidad virtual real.
  const motion=0.046 * Math.max(0.3,Math.min(1.6,speedKmh/65));
  const hazards = s.hazards.map(h=>({...h,progress:h.progress+motion}));
  // Primer obstáculo aparece a los ~0.6 s; los siguientes cada ~3.1 s.
  let nextId=s.nextId;
  if (frame%SPAWN_EVERY_FRAMES===5) {
    const id=nextId++;
    hazards.push({id,lane:LANE_PATTERN[id%LANE_PATTERN.length],kind:HAZARD_PATTERN[id%HAZARD_PATTERN.length],progress:0});
  }
  const incidents: DrivingIncident[]=[];
  const pending: DrivingHazard[]=[];
  let collisions=s.collisions, avoided=s.avoided;
  for (const h of hazards) {
    if (h.progress >= HIT_PROGRESS) {
      const collision=h.lane===s.lane;
      incidents.push({id:h.id,kind:h.kind,lane:h.lane,collision});
      if (collision) collisions++; else avoided++;
    } else pending.push(h);
  }
  return {state:{lane:s.lane,frame,hazards:pending,collisions,avoided,nextId},incidents};
}

export function hazardCaption(kind: HazardKind):string {
  switch(kind){
    case 'obstacle':return 'Obstáculo en carretera';
    case 'energy':return 'Zona de alto consumo';
    case 'camera':return 'Interferencia del sensor ADAS';
    case 'cpu':return 'Sobrecarga de procesamiento';
  }
}
