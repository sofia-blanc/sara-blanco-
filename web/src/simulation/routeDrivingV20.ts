/**
 * AUTOOS V20 - elección de ruta con conducción continua.
 * Reglas puras: sin React, DOM, datos de Supabase ni efectos.
 * Las opciones mantienen el orden del escenario original.
 */
export type RoadLane = 0 | 1 | 2;

/**
 * En cruces de dos vías, el carril central sigue la vía izquierda
 * (decisión explícita y visible en el HUD). El derecho toma la segunda.
 * En cruces de tres, cada carril corresponde a una ruta.
 */
export function routeIndexFromLane(lane: RoadLane, optionCount: number): number {
  if (!Number.isInteger(optionCount) || optionCount <= 0) return -1;
  if (optionCount === 1) return 0;
  if (optionCount === 2) return lane === 2 ? 1 : 0;
  return Math.max(0, Math.min(optionCount - 1, lane));
}

export function minutesToDrivingFork(elapsed: number, decisionCount: number): number {
  if (!Number.isFinite(elapsed) || !Number.isInteger(decisionCount) || decisionCount < 0) return 0;
  return Math.max(0, 5 * (decisionCount + 1) - elapsed);
}

export function forkVisibleWhileDriving(elapsed: number, decisionCount: number, running: boolean): boolean {
  return Boolean(running && minutesToDrivingFork(elapsed, decisionCount) <= 3);
}
