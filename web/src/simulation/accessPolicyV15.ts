/**
 * AUTOOS V15 — Matriz central de acceso de la demostración React.
 *
 * IMPORTANTE: este archivo organiza la EXPERIENCIA DE USUARIO; no concede
 * privilegios de backend. Python autentica y autoriza independientemente las
 * escrituras en Supabase, las tareas del kernel y las operaciones sensibles.
 */
import type { UserRole } from '../types/scheduler';

export type ProtectedModule = 'HOME'|'GPS'|'COCKPIT'|'SIMULATOR'|'SCHEDULER'|'BLACKBOX'|'CLOUD';
export type VehicleAction = 'mission.start'|'mission.drive'|'mission.stop'|'mission.slow'|'mission.economy'|
  'mission.reroute'|'mission.inspect'|'mission.ignore'|'sensor.recover'|'sensor.inject'|
  'kernel.configure'|'simulation.inject'|'cloud.diagnose'|'audit.read';

export const ROLE_NAMES: Readonly<Record<UserRole,string>> = {
  admin:'Administrador', mecanico:'Mecánico', conductor:'Conductor', pasajero:'Pasajero',
};

/** Listas explícitas: denegar por defecto al incorporar una operación nueva. */
const MODULES: Readonly<Record<UserRole,readonly ProtectedModule[]>> = {
  admin:['HOME','GPS','COCKPIT','SIMULATOR','SCHEDULER','BLACKBOX','CLOUD'],
  mecanico:['HOME','GPS','COCKPIT','SIMULATOR','SCHEDULER','BLACKBOX'],
  conductor:['HOME','GPS','COCKPIT','BLACKBOX'],
  pasajero:['HOME','COCKPIT'],
};
const ACTIONS: Readonly<Record<UserRole,readonly VehicleAction[]>> = {
  admin:['mission.start','mission.drive','mission.stop','mission.slow','mission.economy','mission.reroute',
    'mission.inspect','mission.ignore','sensor.recover','sensor.inject','kernel.configure',
    'simulation.inject','cloud.diagnose','audit.read'],
  mecanico:['mission.start','mission.drive','mission.stop','mission.slow','mission.economy',
    'mission.reroute','mission.inspect','mission.ignore','sensor.recover','sensor.inject',
    'kernel.configure','simulation.inject','audit.read'],
  conductor:['mission.start','mission.drive','mission.stop','mission.slow','mission.economy',
    'mission.reroute','mission.inspect','mission.ignore'],
  pasajero:[],
};
export function canOpenModule(role:UserRole,module:ProtectedModule):boolean {
  return MODULES[role]?.includes(module) ?? false;
}
export function canExecute(role:UserRole,action:VehicleAction):boolean {
  return ACTIONS[role]?.includes(action) ?? false;
}
export function visibleModules(role:UserRole):readonly ProtectedModule[] {
  return MODULES[role] ?? ['HOME'];
}
/** Acceso a mantenimiento, sin equivaler a identidad Python autenticada. */
export function isTechnician(role:UserRole):boolean {return role==='mecanico'||role==='admin';}
