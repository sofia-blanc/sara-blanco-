/** Escenarios de enseñanza: representan un VEHÍCULO SIMULADO, nunca un automóvil real. */
export type ScenarioId = 'normal' | 'battery' | 'gps' | 'camera' | 'cpu' | 'network' | 'storm' | 'sandbox';
export type Weather = 'soleado' | 'lluvia' | 'niebla';
export type SimulationAction =
  | 'power_save' | 'suspend_media' | 'reduce_speed' | 'restart_gps'
  | 'offline_navigation' | 'ignore' | 'prioritize' | 'sensor_backup'
  | 'isolate_camera' | 'restart_network' | 'local_mode' | 'limit_comfort';

export interface ScenarioOption {
  id: SimulationAction;
  label: string;
  detail: string;
  explanation: string;
}

export interface ScenarioDefinition {
  id: ScenarioId;
  title: string;
  icon: string;
  description: string;
  cause: string;
  risk: string;
  battery: number;
  speed: number;
  weather: Weather;
  faultDevice?: string;
  stressCpu?: boolean;
  options: ScenarioOption[];
}

export const SCENARIOS: ScenarioDefinition[] = [
  {
    id: 'normal', title: 'Conducción normal', icon: '🚗', description: 'Viaje de prueba sin fallas para explorar la telemetría.',
    cause: 'Todos los dispositivos operan dentro de parámetros nominales.', risk: 'Bajo', battery: 85, speed: 65, weather: 'soleado',
    options: [
      { id: 'prioritize', label: 'Priorizar seguridad', detail: 'Scheduler apropiativo', explanation: 'Los procesos de seguridad quedan con máxima prioridad en la cola de CPU.' },
      { id: 'suspend_media', label: 'Apagar multimedia', detail: 'Liberar CPU y memoria', explanation: 'El SO suspende procesos multimedia y libera sus recursos estimados.' },
    ],
  },
  {
    id: 'battery', title: 'Batería crítica', icon: '🔋', description: 'La carga baja a 12 % durante el viaje.',
    cause: 'Nivel de carga insuficiente para sostener todos los servicios de confort.', risk: 'Alto', battery: 12, speed: 74, weather: 'soleado',
    options: [
      { id: 'power_save', label: 'Activar ahorro extremo', detail: 'Suspender servicios no críticos', explanation: 'El SO conserva procesos críticos y suspende multimedia y climatización.' },
      { id: 'reduce_speed', label: 'Reducir velocidad', detail: 'Limitar a 35 km/h', explanation: 'Se reduce la demanda energética del movimiento virtual.' },
      { id: 'ignore', label: 'Continuar sin cambios', detail: 'Mantener el riesgo', explanation: 'El SO registra que se rechazó la recomendación; el riesgo de autonomía sigue activo.' },
    ],
  },
  {
    id: 'gps', title: 'Pérdida de GPS', icon: '🛰️', description: 'Se pierde la señal GNSS durante una ruta.',
    cause: 'El receptor GPS deja de proporcionar coordenadas válidas.', risk: 'Medio', battery: 74, speed: 58, weather: 'soleado', faultDevice: 'DEV_GPS_01',
    options: [
      { id: 'restart_gps', label: 'Reiniciar módulo GPS', detail: 'Autodiagnóstico y recuperación simulada', explanation: 'Se restablece el dispositivo GPS y se borra el código de falla de la simulación.' },
      { id: 'offline_navigation', label: 'Navegación sin conexión', detail: 'Usar referencias almacenadas', explanation: 'El navegador pasa a modo offline; la falla GPS no se oculta.' },
      { id: 'ignore', label: 'Continuar sin GPS', detail: 'No intervenir', explanation: 'El SO conserva el fallo y registra la decisión del usuario.' },
    ],
  },
  {
    id: 'camera', title: 'Falla de cámara frontal', icon: '📷', description: 'La cámara ADAS deja de responder.',
    cause: 'El controlador de la cámara no entrega datos al bus Automotive Ethernet.', risk: 'Alto', battery: 81, speed: 49, weather: 'soleado', faultDevice: 'DEV_CAM_FRONT',
    options: [
      { id: 'sensor_backup', label: 'Habilitar sensores redundantes', detail: 'Priorizar radar y LiDAR', explanation: 'El SO asigna prioridad máxima al diagnóstico de los sensores redundantes.' },
      { id: 'isolate_camera', label: 'Aislar cámara', detail: 'Evitar lecturas inválidas', explanation: 'El dispositivo queda desconectado y se registra el aislamiento preventivo.' },
      { id: 'reduce_speed', label: 'Reducir velocidad', detail: 'Limitar a 35 km/h', explanation: 'El conductor virtual reduce su velocidad mientras la falla permanece visible.' },
    ],
  },
  {
    id: 'cpu', title: 'Sobrecarga de CPU', icon: '🧠', description: 'Un proceso de fondo consume gran parte del procesador.',
    cause: 'Competencia por CPU y memoria entre multimedia, sensores y tareas auxiliares.', risk: 'Alto', battery: 77, speed: 67, weather: 'soleado', stressCpu: true,
    options: [
      { id: 'suspend_media', label: 'Suspender multimedia', detail: 'Liberar carga de trabajo', explanation: 'Se extraen las tareas multimedia de la cola de ejecución.' },
      { id: 'prioritize', label: 'Dar prioridad a seguridad', detail: 'Planificación apropiativa', explanation: 'El scheduler cambia a prioridad apropiativa, favoreciendo tareas críticas.' },
      { id: 'ignore', label: 'Mantener carga actual', detail: 'Sin optimización', explanation: 'Se mantiene la carga de CPU y se registra el riesgo de latencia.' },
    ],
  },
  {
    id: 'network', title: 'Pérdida de comunicación', icon: '📡', description: 'La telemetría V2X deja de conectarse con la red.',
    cause: 'El módulo de comunicación 5G/V2X queda desconectado.', risk: 'Medio', battery: 68, speed: 60, weather: 'soleado', faultDevice: 'DEV_COM_V2X',
    options: [
      { id: 'restart_network', label: 'Reiniciar comunicaciones', detail: 'Recuperación virtual del módem', explanation: 'El enlace V2X vuelve a estado operativo en la simulación.' },
      { id: 'local_mode', label: 'Operación local', detail: 'Continuar sin cloud', explanation: 'Se habilita un modo local simulado y se conserva el fallo en el dispositivo.' },
      { id: 'ignore', label: 'Ignorar advertencia', detail: 'Mantener desconexión', explanation: 'La interrupción continúa y queda documentada.' },
    ],
  },
  {
    id: 'storm', title: 'Lluvia intensa y niebla', icon: '🌧️', description: 'El entorno reduce la visibilidad y exige adaptación.',
    cause: 'Condiciones ambientales que demandan más procesamiento de sensores.', risk: 'Alto', battery: 69, speed: 85, weather: 'lluvia',
    options: [
      { id: 'reduce_speed', label: 'Reducir velocidad', detail: 'Limitar a 35 km/h', explanation: 'Se reduce la velocidad y la demanda energética estimada.' },
      { id: 'sensor_backup', label: 'Priorizar sensores', detail: 'Más CPU para percepción', explanation: 'El SO da prioridad al procesamiento de sensores y registra la redundancia.' },
      { id: 'ignore', label: 'Mantener velocidad', detail: 'Riesgo sostenido', explanation: 'Se conserva la velocidad y el sistema registra la decisión.' },
    ],
  },
  {
    id: 'sandbox', title: 'Laboratorio libre', icon: '🛠️', description: 'Crea condiciones propias y combina fallos en tiempo real.',
    cause: 'Las condiciones se modifican mediante los controles del usuario.', risk: 'Variable', battery: 85, speed: 55, weather: 'soleado',
    options: [
      { id: 'power_save', label: 'Modo ahorro', detail: 'Preservar recursos', explanation: 'El SO suspende carga no esencial y activa la política de ahorro.' },
      { id: 'prioritize', label: 'Prioridad crítica', detail: 'Programar con prioridad', explanation: 'El sistema cambia al algoritmo de prioridad apropiativa.' },
      { id: 'suspend_media', label: 'Suspender multimedia', detail: 'Aliviar CPU y memoria', explanation: 'Las tareas de entretenimiento dejan de ejecutarse.' },
    ],
  },
];

export function scenarioById(id: ScenarioId): ScenarioDefinition {
  return SCENARIOS.find((item) => item.id === id) || SCENARIOS[0];
}
