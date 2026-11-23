/**
 * AutoOS V21: dos cruces importantes en una misión de veinte minutos.
 * Los cruces NO se infieren del número de intervenciones del informe.
 * Esto evita que el sistema repita decisiones cada cinco minutos.
 */
import type { ScenarioId, SimulationAction } from './scenarios';

export const JUNCTION_MINUTES_V21 = [8, 16] as const;

export function nextJunctionMinute(junctionIndex: number): number | null {
  if (!Number.isInteger(junctionIndex) || junctionIndex < 0) return null;
  return JUNCTION_MINUTES_V21[junctionIndex] ?? null;
}

export function isRouteJunctionDue(elapsed: number, junctionIndex: number): boolean {
  const minute = nextJunctionMinute(junctionIndex);
  return minute !== null && Number.isFinite(elapsed) && elapsed >= minute;
}

export function minutesToDrivingForkV21(elapsed: number, junctionIndex: number): number | null {
  const minute = nextJunctionMinute(junctionIndex);
  if (minute === null || !Number.isFinite(elapsed)) return null;
  return Math.max(0, minute - elapsed);
}

export function forkVisibleWhileDrivingV21(elapsed: number, junctionIndex: number, running: boolean): boolean {
  const left = minutesToDrivingForkV21(elapsed, junctionIndex);
  return Boolean(running && left !== null && left <= 2);
}

/**
 * "Continuar sin cambios" no revoca el ahorro ya activado.
 * La excepción aplica exclusivamente a batería crítica, con ahorro
 * elegido explícitamente y todavía reflejado en la batería compartida.
 * Nunca ignora batería agotada ni las detenciones por colisión.
 */
export function preserveEnergySavingOnIgnore(
  scenario: ScenarioId,
  action: SimulationAction,
  powerSaveChosen: boolean,
  batterySaving: boolean,
  batteryLevel: number,
): boolean {
  return scenario === 'battery' && action === 'ignore' &&
    powerSaveChosen && batterySaving && Number.isFinite(batteryLevel) && batteryLevel > 0;
}
