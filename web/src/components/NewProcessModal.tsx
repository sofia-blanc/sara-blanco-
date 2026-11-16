import React, { useState } from 'react';
import { Process, ProcessCategory, ProcessPriority } from '../types/scheduler';
import { PlusCircle, X, Cpu, ShieldAlert } from 'lucide-react';

interface NewProcessModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAddProcess: (proc: Omit<Process, 'waitingTime' | 'turnaroundTime'>) => void;
  currentTime: number;
}

const COLOR_PALETTE = [
  '#BF40FA', // Hyper Magenta
  '#4928C2', // Ultrasonic Blue
  '#06b6d4', // Cyan
  '#ec4899', // Pink
  '#22c55e', // Green
  '#f59e0b', // Amber
  '#ef4444', // Red
];

export const NewProcessModal: React.FC<NewProcessModalProps> = ({
  isOpen,
  onClose,
  onAddProcess,
  currentTime,
}) => {
  const [name, setName] = useState('');
  const [burstTime, setBurstTime] = useState(4);
  const [arrivalTime, setArrivalTime] = useState(currentTime);
  const [priority, setPriority] = useState<ProcessPriority>(3);
  const [category, setCategory] = useState<ProcessCategory>('control');
  const [critical, setCritical] = useState(false);
  const [color, setColor] = useState(COLOR_PALETTE[0]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    const newProc: Omit<Process, 'waitingTime' | 'turnaroundTime'> = {
      pid: Math.floor(Math.random() * 800) + 150,
      name: name.trim(),
      category,
      arrivalTime: Number(arrivalTime),
      burstTime: Number(burstTime),
      remainingTime: Number(burstTime),
      priority: critical ? 1 : priority,
      critical,
      color,
      state: 'NUEVO',
      powerConsumptionWatts: 30,
      cpuUsagePct: 15,
      memoryMb: 128,
    };

    onAddProcess(newProc);
    setName('');
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-md autoos-card rounded-3xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-[var(--border-color)] autoos-surface">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-[var(--accent-primary)]/15 text-[var(--accent-primary)] border border-[var(--accent-primary)]/30">
              <PlusCircle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-serif font-bold text-[var(--text-primary)]">Crear Nuevo Proceso</h3>
              <p className="text-[11px] text-[var(--text-muted)]">Bloque de Control de Proceso (PCB)</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-[var(--text-muted)] hover:text-[var(--text-primary)] autoos-surface transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4 text-xs font-mono">
          <div>
            <label className="block text-[var(--text-primary)] font-semibold mb-1">Nombre del Proceso</label>
            <input
              type="text"
              required
              placeholder="Ej. Sensor Punto Ciego BSD"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3.5 py-2.5 autoos-surface rounded-xl text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-primary)]"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[var(--text-primary)] font-semibold mb-1">Ráfaga CPU (BT)</label>
              <input
                type="number"
                min="1"
                max="20"
                value={burstTime}
                onChange={(e) => setBurstTime(Number(e.target.value))}
                className="w-full px-3.5 py-2.5 autoos-surface rounded-xl text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-primary)]"
              />
            </div>
            <div>
              <label className="block text-[var(--text-primary)] font-semibold mb-1">Llegada (AT)</label>
              <input
                type="number"
                min="0"
                max="50"
                value={arrivalTime}
                onChange={(e) => setArrivalTime(Number(e.target.value))}
                className="w-full px-3.5 py-2.5 autoos-surface rounded-xl text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-primary)]"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[var(--text-primary)] font-semibold mb-1">Prioridad</label>
              <select
                value={priority}
                disabled={critical}
                onChange={(e) => setPriority(Number(e.target.value) as ProcessPriority)}
                className="w-full px-3.5 py-2.5 autoos-surface rounded-xl text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-primary)] disabled:opacity-50 cursor-pointer"
              >
                <option value={1} className="text-black dark:text-white dark:bg-[#180E24]">1 - Crítica (ASIL-D)</option>
                <option value={2} className="text-black dark:text-white dark:bg-[#180E24]">2 - Alta (Sensores)</option>
                <option value={3} className="text-black dark:text-white dark:bg-[#180E24]">3 - Media (Control)</option>
                <option value={4} className="text-black dark:text-white dark:bg-[#180E24]">4 - Baja (Confort)</option>
                <option value={5} className="text-black dark:text-white dark:bg-[#180E24]">5 - Muy Baja (Multimedia)</option>
              </select>
            </div>
            <div>
              <label className="block text-[var(--text-primary)] font-semibold mb-1">Categoría</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value as ProcessCategory)}
                className="w-full px-3.5 py-2.5 autoos-surface rounded-xl text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent-primary)] cursor-pointer"
              >
                <option value="control" className="text-black dark:text-white dark:bg-[#180E24]">Control de Tracción</option>
                <option value="seguridad" className="text-black dark:text-white dark:bg-[#180E24]">Seguridad ASIL-D</option>
                <option value="sensor" className="text-black dark:text-white dark:bg-[#180E24]">Sensor LiDAR/Radar</option>
                <option value="confort" className="text-black dark:text-white dark:bg-[#180E24]">Confort Clima</option>
                <option value="multimedia" className="text-black dark:text-white dark:bg-[#180E24]">Infoentretenimiento</option>
              </select>
            </div>
          </div>

          {/* Critical toggle */}
          <div className="flex items-center gap-2.5 p-3 bg-red-500/10 border border-red-500/30 rounded-xl">
            <input
              type="checkbox"
              id="criticalCheck"
              checked={critical}
              onChange={(e) => {
                setCritical(e.target.checked);
                if (e.target.checked) setPriority(1);
              }}
              className="accent-red-500 w-4 h-4 rounded cursor-pointer"
            />
            <label htmlFor="criticalCheck" className="text-red-500 font-semibold flex items-center gap-2 cursor-pointer">
              <ShieldAlert className="w-4 h-4 text-red-500" />
              Proceso Crítico de Seguridad (Fuerza Prioridad 1)
            </label>
          </div>

          {/* Color Selector */}
          <div>
            <label className="block text-[var(--text-primary)] font-semibold mb-2">Color del Bloque</label>
            <div className="flex items-center gap-2.5">
              {COLOR_PALETTE.map((c) => (
                <button
                  type="button"
                  key={c}
                  onClick={() => setColor(c)}
                  style={{ backgroundColor: c }}
                  className={`w-7 h-7 rounded-full transition transform ${
                    color === c ? 'ring-2 ring-[var(--accent-primary)] scale-110 shadow-lg' : 'opacity-70 hover:opacity-100'
                  }`}
                />
              ))}
            </div>
          </div>

          {/* Submit */}
          <div className="pt-2 flex justify-end gap-2.5">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl autoos-surface text-[var(--text-muted)] hover:text-[var(--text-primary)]"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl bg-[var(--accent-primary)] text-white font-bold flex items-center gap-2 shadow-sm hover:opacity-90"
            >
              <Cpu className="w-4 h-4" />
              Crear Proceso
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
