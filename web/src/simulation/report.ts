import type { ScenarioId, Weather } from './scenarios';
import { saveSimulationReportToSupabase } from '../supabaseClient';
import { sendCloudRequest } from '../kernelBridge';

export interface SimulationSnapshot {
  battery: number;
  speed: number;
  weather: Weather;
  cpuLoad: number;
  usedMemory: number;
  /** Campos V9 opcionales para mantener informes V8 anteriores compatibles. */
  energyWh?: number;
  powerW?: number;
  swapMb?: number;
  cpuBusyPct?: number;
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
    `Demanda CPU: ${item.cpuLoad} % | Utilización CPU: ${item.cpuBusyPct ?? 'no disponible'} %`,
    `RAM física estimada: ${item.usedMemory} MB / 2048 MB | SWAP solicitada: ${item.swapMb ?? 0} MB`,
    `Potencia instantánea estimada: ${item.powerW ?? 'no disponible'} W | Energía consumida en sesión: ${item.energyWh?.toFixed(1) ?? 'no disponible'} Wh`,
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
    '', 'IMPORTANTE: Estas cifras corresponden al motor DIDÁCTICO React (memoria por proceso y consumo energético estimados). NO provienen de un automóvil real ni de la instancia kernel Python.',
  ].join('\n');
}

export function saveReport(report: AutoOSReport): void {
  try {
    const key = 'autoos_sim_reports_v1';
    const previous: AutoOSReport[] = JSON.parse(localStorage.getItem(key) || '[]');
    localStorage.setItem(key, JSON.stringify([report, ...previous.filter((r) => r.id !== report.id)].slice(0, 20)));
  } catch { /* almacenamiento del navegador deshabilitado: aún es posible exportar */ }

  // AUTOOS V11: si Streamlit está disponible, el servidor persiste el
  // reporte con sus propios Secrets y controles RBAC. Evitar doble escritura.
  const viaStreamlit = sendCloudRequest({
    type: 'autoos:cloud-report', requestId: `report_${report.id}`,
    report: report as unknown as Record<string, unknown>,
  });
  if (!viaStreamlit) {
    // En Vite independiente, usar el cliente web con clave pública si existe.
    saveSimulationReportToSupabase(report).catch((err) => {
      console.debug('[AutoOS] Reporte solo local, sin sincronización Cloud:', err);
    });
  }
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
