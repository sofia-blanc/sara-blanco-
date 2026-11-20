/**
 * AUTOOS · Orientación funcional (V3)
 *
 * Problema resuelto: una pantalla técnica sin instrucciones deja al usuario
 * sin saber cuál es el objetivo ni qué botones debe pulsar primero.
 *
 * Diseño: breve descripción + tres pasos. Es una capa informativa:
 * NO altera el estado del kernel, los permisos RBAC ni la simulación.
 */
import React from 'react';
import { ArrowDownRight, Compass, HelpCircle } from 'lucide-react';
import type { AutoOSModule } from './CinematicMenu';

const ORIENTATION: Record<AutoOSModule, {
  number: string;
  objective: string;
  steps: [string, string, string];
  tip: string;
}> = {
  HOME: {
    number: '01',
    objective: 'Inicio del SO reúne CPU, RAM, batería, procesos y alertas en una vista.',
    steps: ['Revisa el estado general.', 'Consulta los procesos y recursos.', 'Abre un módulo desde la navegación.'],
    tip: 'La información comparte el motor de simulación React.',
  },
  GPS: {
    number: '02',
    objective: 'Navegación muestra rutas virtuales y eventos de ubicación simulados.',
    steps: ['Selecciona una ruta virtual.', 'Inicia la misión y avanza ciclos.', 'Observa consumo, señal GNSS e historial.'],
    tip: 'El GPS didáctico no es navegación de carretera en tiempo real.',
  },
  BLACKBOX: {
    number: '06',
    objective: 'Caja Negra conserva el historial de eventos de la sesión.',
    steps: ['Realiza una simulación.', 'Filtra los registros por categoría.', 'Exporta el historial para la demostración.'],
    tip: 'Distingue entre almacenamiento local y persistencia en la nube.',
  },
  CLOUD: {
    number: '07',
    objective: 'Supabase verifica conexión y persistencia desde el servidor.',
    steps: ['Consulta el diagnóstico de conexión.', 'Revisa los permisos y errores de acceso.', 'Comprueba eventos e informes sincronizados.'],
    tip: 'Una credencial configurada no garantiza acceso válido a la base de datos.',
  },
  COCKPIT: {
    number: '01',
    objective: '¿Qué hace Conducción? Te muestra el estado de un vehículo inteligente y permite consultar sus instrumentos, sensores, navegación, multimedia y seguridad.',
    steps: [
      'Panel principal: revisa batería, CPU, memoria y salud del vehículo.',
      'Subsistemas: abre GPS, cámara, LiDAR o climatización y observa su telemetría.',
      'Multimedia y seguridad: usa el reproductor y consulta qué puede hacer cada perfil.',
    ],
    tip: 'Las pestañas dentro de la cabina cambian la herramienta, no el vehículo. Puedes volver al menú superior cuando quieras.',
  },
  SIMULATOR: {
    number: '02',
    objective: '¿Qué hace Simulación? Te deja provocar situaciones virtuales y ver cómo responde el sistema operativo del vehículo, sin afectar un automóvil real.',
    steps: [
      'Escoge un escenario: batería crítica, GPS, cámara, CPU o clima.',
      'Pulsa «Iniciar simulación» y observa qué cambia en la cabina y el diagnóstico.',
      'Elige una acción de respuesta y revisa el resultado o el informe.',
    ],
    tip: 'Empieza por «Batería crítica»: permite explicar al profesor por qué el sistema prioriza la seguridad.',
  },
  SCHEDULER: {
    number: '03',
    objective: '¿Qué hace el Planificador? Simula cómo un sistema operativo de tiempo real decide qué proceso usa la CPU y durante cuánto tiempo.',
    steps: [
      'Elige FCFS, Round Robin o prioridad; con Round Robin puedes cambiar el quantum.',
      'Pulsa «Paso (+1 s)» para observar cada decisión o «Reproducir» para avanzar.',
      'Compara el diagrama de Gantt, la CPU y la cola de procesos. Abre hardware avanzado solo si lo necesitas.',
    ],
    tip: 'Para presentarlo: usa Round Robin (quantum 2 s), avanza tres pasos y explica las conmutaciones de CPU.',
  },
};

export function ModuleOrientationV3({ active }: { active: AutoOSModule }) {
  const guide = ORIENTATION[active];
  return (
    <section className="autoos-guide-v3" aria-label={`Guía de ${active.toLowerCase()}`}>
      <div className="autoos-guide-v3__identity" aria-hidden="true">
        <span>GUÍA</span><strong>{guide.number}</strong>
      </div>
      <div className="autoos-guide-v3__copy">
        <div className="autoos-guide-v3__eyebrow"><Compass size={15} /> ANTES DE COMENZAR</div>
        <p>{guide.objective}</p>
        <details open={active !== 'COCKPIT'}>
          <summary><HelpCircle size={15} /> ¿Cómo se utiliza? <ArrowDownRight size={17} /></summary>
          <ol>{guide.steps.map((step, i) => <li key={step}><b>0{i + 1}</b><span>{step}</span></li>)}</ol>
          <p className="autoos-guide-v3__tip">Consejo para la exposición: {guide.tip}</p>
        </details>
      </div>
    </section>
  );
}
