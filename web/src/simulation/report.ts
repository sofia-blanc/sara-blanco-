import type { ScenarioId, Weather } from './scenarios';
import { saveSimulationReportToSupabase } from '../supabaseClient';

export interface SimulationSnapshot {
  battery: number;
  speed: number;
  weather: Weather;
  cpuLoad: number;
  usedMemory: number;
  running: number;
  suspended: number;
  failures: string[];
  scheduler: string;
  tick: number;
}

export interface SimulationDecisionRecord {
  time: string;
  choice: string;
  effect: string;
}

export interface AutoOSReport {
  id: string;
  scenario: ScenarioId;
  title: string;
  startedAt: string;
  completedAt: string;
  diagnosis: string;
  initial: SimulationSnapshot;
  final: SimulationSnapshot;
  actions: SimulationDecisionRecord[];
  recommendations: string[];
  status: string;
}

const dateText = (value: string) => new Date(value).toLocaleString('es-CO');

export function reportAsText(report: AutoOSReport): string {
  const snap = (item: SimulationSnapshot) => [
    `Batería: ${item.battery.toFixed(1)} % | Velocidad: ${item.speed} km/h | Tiempo CPU: ${item.tick}`,
    `Carga solicitada CPU: ${item.cpuLoad} % | Memoria ocupada: ${item.usedMemory} MB`,
    `Procesos en actividad: ${item.running} | Suspendidos: ${item.suspended}`,
    `Dispositivos con anomalía: ${item.failures.length ? item.failures.join(', ') : 'ninguno'}`,
    `Scheduler: ${item.scheduler} | Clima: ${item.weather}`,
  ].join('\n');
  return [
    'AUTOOS | INFORME TÉCNICO DE SIMULACIÓN',
    '====================================',
    `ID: ${report.id}`,
    `Escenario: ${report.title}`,
    `Inicio: ${dateText(report.startedAt)}`,
    `Finalización: ${dateText(report.completedAt)}`,
    `Evaluación: ${report.status}`,
    `Diagnóstico: ${report.diagnosis}`,
    '', 'ESTADO INICIAL', snap(report.initial),
    '', 'DECISIONES Y EFECTOS',
    ...(report.actions.length ? report.actions.map((a, i) => `${i + 1}. ${a.time} | ${a.choice}\n   ${a.effect}`) : ['Sin intervención registrada.']),
    '', 'ESTADO FINAL', snap(report.final),
    '', 'RECOMENDACIONES', ...report.recommendations.map((r) => `- ${r}`),
    '', 'IMPORTANTE: Los valores corresponden a una abstracción educativa de un sistema operativo vehicular; no son telemetría de un automóvil real.',
  ].join('\n');
}

export function saveReport(report: AutoOSReport): void {
  try {
    const key = 'autoos_sim_reports_v1';
    const previous: AutoOSReport[] = JSON.parse(localStorage.getItem(key) || '[]');
    localStorage.setItem(key, JSON.stringify([report, ...previous.filter((r) => r.id !== report.id)].slice(0, 20)));
  } catch { /* almacenamiento del navegador deshabilitado: aún es posible exportar */ }

  // Sincronizar de manera asíncrona con Supabase Cloud si está configurado
  saveSimulationReportToSupabase(report).catch((err) => {
    console.debug('[AutoOS] Fallback local activo para reporte:', err);
  });
}

export function readReports(): AutoOSReport[] {
  try { return JSON.parse(localStorage.getItem('autoos_sim_reports_v1') || '[]'); }
  catch { return []; }
}

export function downloadReport(report: AutoOSReport): void {
  const blob = new Blob([reportAsText(report)], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `AutoOS_Informe_${report.scenario}_${report.id}.txt`;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
