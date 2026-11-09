// SimulationContext.tsx – central state for cockpit updates
import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { SchedulerMetrics, GPSTelemetry, VehicleDevice, UserRole } from '../types/scheduler';
import { SimulationState } from '../utils/schedulerEngine';

export interface SimulationContextProps {
  metrics: SchedulerMetrics | null;
  gps: GPSTelemetry | null;
  devices: VehicleDevice[];
  setMetrics: (m: SchedulerMetrics) => void;
  setGPS: (g: GPSTelemetry) => void;
  setDevices: (d: VehicleDevice[]) => void;
  userRole: UserRole;
  setUserRole: (r: UserRole) => void;
}

const SimulationContext = createContext<SimulationContextProps | undefined>(undefined);

export const SimulationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [metrics, setMetrics] = useState<SchedulerMetrics | null>(null);
  const [gps, setGPS] = useState<GPSTelemetry | null>(null);
  const [devices, setDevices] = useState<VehicleDevice[]>([]);
  const [userRole, setUserRole] = useState<UserRole>('mecanico');

  // Expose setters through callbacks so children can call them safely
  const updateMetrics = useCallback((m: SchedulerMetrics) => setMetrics(m), []);
  const updateGPS = useCallback((g: GPSTelemetry) => setGPS(g), []);
  const updateDevices = useCallback((d: VehicleDevice[]) => setDevices(d), []);

  // Notify the cockpit iframe whenever metrics or GPS change
  const iframe = document.getElementById('cockpit-iframe') as HTMLIFrameElement | null;
  useEffect(() => {
    if (iframe?.contentWindow) {
      iframe.contentWindow.postMessage({ type: 'AUTOOS_UPDATE_METRICS', metrics }, '*');
    }
  }, [metrics]);
  useEffect(() => {
    if (iframe?.contentWindow) {
      iframe.contentWindow.postMessage({ type: 'AUTOOS_UPDATE_GPS', gps }, '*');
    }
  }, [gps]);

  return (
    <SimulationContext.Provider
      value={{
        metrics,
        gps,
        devices,
        setMetrics: updateMetrics,
        setGPS: updateGPS,
        setDevices: updateDevices,
        userRole,
        setUserRole,
      }}
    >
      {children}
    </SimulationContext.Provider>
  );
};

export const useSimulation = () => {
  const ctx = useContext(SimulationContext);
  if (!ctx) throw new Error('useSimulation must be used within SimulationProvider');
  return ctx;
};
