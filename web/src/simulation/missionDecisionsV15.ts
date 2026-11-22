/**
 * Opciones narrativas de la misión de conducción educativa.
 * La selección se valida con accessPolicyV15 antes de modificar App.tsx.
 * No se inventan mediciones: el consumo energético sigue calculándose en V9.
 */
import type {VehicleAction} from './accessPolicyV15';
export type MissionDecision = 'start'|'continue'|'slow'|'economy'|'reroute'|'inspect'|'recover'|'inject'|'ignore';
export interface MissionOption {
  id:MissionDecision; label:string; detail:string; permission:VehicleAction;
}
export const MISSION_OPTIONS:readonly MissionOption[] = [
  {id:'start',label:'INICIAR MISIÓN',detail:'Comienza el circuito didáctico y el reloj de AutoOS.',permission:'mission.start'},
  {id:'continue',label:'CONTINUAR 1 MIN',detail:'Ejecuta un tick: CPU, RAM, batería, GPS y Caja Negra.',permission:'mission.drive'},
  {id:'slow',label:'REDUCIR VELOCIDAD',detail:'Limita la velocidad a 25 km/h y cambia la potencia de tracción.',permission:'mission.slow'},
  {id:'economy',label:'ACTIVAR AHORRO',detail:'Activa el modo de batería baja; el planificador aplica sus políticas.',permission:'mission.economy'},
  {id:'reroute',label:'RUTA ALTERNATIVA',detail:'Comienza un circuito alternativo y registra la decisión.',permission:'mission.reroute'},
  {id:'inspect',label:'DETENER E INSPECCIONAR',detail:'Detiene el avance para revisar periféricos sin borrar el historial.',permission:'mission.inspect'},
  {id:'recover',label:'RECUPERAR GNSS',detail:'Reinicia el sensor GNSS del laboratorio (solo personal técnico).',permission:'sensor.recover'},
  {id:'inject',label:'SIMULAR FALLA GNSS',detail:'Inyecta un fallo de entrenamiento, sin afectar hardware real.',permission:'sensor.inject'},
  {id:'ignore',label:'IGNORAR ADVERTENCIA',detail:'Conserva los riesgos y deja trazabilidad de esta decisión.',permission:'mission.ignore'},
];
