/**
 * AUTOOS V17 · reglas puras para mostrar la bifurcación de la ruta.
 *
 * Estas funciones no cambian los recursos: el motor React existente es la fuente
 * de CPU/RAM/batería. La interfaz SOLO decide cuándo mostrar una elección.
 */
import type { ScenarioDefinition } from './scenarios';

export type MissionViewV17 = 'ready'|'driving'|'fork'|'paused'|'exhausted'|'finished';

export interface MissionViewInput {
  active: boolean;
  finished: boolean;
  checkpointDue: boolean;
  running: boolean;
  batteryPct: number;
}

/** Prioridad explícita para evitar mostrar opciones al agotarse la batería. */
export function missionViewV17(s: MissionViewInput): MissionViewV17 {
  if (!s.active) return 'ready';
  if (s.finished) return 'finished';
  if (!Number.isFinite(s.batteryPct) || s.batteryPct <= 0) return 'exhausted';
  if (s.checkpointDue) return 'fork';
  return s.running ? 'driving' : 'paused';
}

/** Solo opciones definidas en el escenario (nunca decisiones ficticias). */
export function routePathsV17(s: ScenarioDefinition) { return s.options.slice(0,3); }

/** Los checkpoints dependen de la cantidad de decisiones, NO de un temporizador independiente. */
export function minutesUntilForkV17(elapsed: number, decisionCount: number): number {
  if (!Number.isFinite(elapsed) || !Number.isInteger(decisionCount) || decisionCount < 0) return 0;
  return Math.max(0, 5 * (decisionCount + 1) - elapsed);
}

/** Guarda las respuestas para el siguiente checkpoint y rechaza clicks fuera de la bifurcación. */
export function canChoosePathV17(s: MissionViewInput, allowed: boolean): boolean {
  return allowed && missionViewV17(s) === 'fork';
}
