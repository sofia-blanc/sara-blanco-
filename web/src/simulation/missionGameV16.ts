/** AUTOOS V16 — Reglas puras de la experiencia de simulación.
 * El dominio de permisos se deriva de accessPolicyV15, no de una bandera de CSS.
 * El checkpoint solicita una decisión cada 5 ticks virtuales completados.
 */
import type {UserRole} from '../types/scheduler';
import {canExecute} from './accessPolicyV15';

/** Solo los roles con permiso de laboratorio pueden iniciar/decidir escenarios. */
export const maySimulate = (role: UserRole): boolean => canExecute(role,'simulation.inject');

/** Devuelve true si se alcanzó un punto que requiere una decisión nueva. */
export function decisionCheckpoint(elapsed: number, decisionCount: number): boolean {
  return Number.isFinite(elapsed) && elapsed >= 5 * (decisionCount + 1) && decisionCount >= 0;
}

/** Si la batería llega a cero, el motor no puede seguir consumiendo energía. */
export function canRunMission(active: boolean, finished: boolean, batteryPct: number): boolean {
  return active && !finished && Number.isFinite(batteryPct) && batteryPct > 0;
}
