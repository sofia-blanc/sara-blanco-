# -*- coding: utf-8 -*-
"""
Script para actualizar la reactividad en tiempo real de la memoria RAM y CPU
tanto en Auto/autoos_interactive.html como en Auto/autoos_unified.html.
"""
import base64
import os
import shutil

# 1. Actualizar Auto/autoos_interactive.html
with open('Auto/autoos_interactive.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar el bloque syncMediaState
start_marker = '(0,_.useEffect)(()=>{\n  function syncMediaState(){'
end_marker = 'window.removeEventListener("autoos:bt_status",syncMediaState);\n  };\n},[]);'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print('ERROR: No se encontró el bloque syncMediaState en autoos_interactive.html')
    exit(1)

end_idx += len(end_marker)

new_media_and_telemetry_block = """(0,_.useEffect)(()=>{
  function syncMediaState(){
    let isPlaying=Boolean(window.__AUTOOS_SPOTIFY_PLAYING__);

    // Actualizar proceso RTOS de Audio e Infoentretenimiento (PID 1007)
    p(prev=>prev.map(item=>{
      if(item.codigo==="infotainment_media_player"||item.pid===1007){
        return{
          ...item,
          estado:isPlaying?"ejecucion":"espera",
          state:isPlaying?"ejecucion":"espera",
          memoria_mb:isPlaying?720:210,
          cpu_pct:isPlaying?7.8:0.4
        };
      }
      return item;
    }));

    // Actualizar dispositivo de hardware DEV_MEDIA_DSP
    d(prev=>prev.map(item=>{
      if(item.codigo==="DEV_MEDIA_DSP"){
        return{
          ...item,
          estado:"Operativo",
          detalle:isPlaying?"Streaming Activo (DSP 48kHz/24bit)":"DSP 12 Canales Surround (En Espera)"
        };
      }
      return item;
    }));
  }

  window.addEventListener("autoos:media_status",syncMediaState);
  window.addEventListener("autoos:bt_status",syncMediaState);
  syncMediaState();
  return()=>{
    window.removeEventListener("autoos:media_status",syncMediaState);
    window.removeEventListener("autoos:bt_status",syncMediaState);
  };
},[]);

// =========================================================================
// EFECTO REACTIVO DETERMINISTICO DE TELEMETRIA (RAM Y CPU)
// =========================================================================
(0,_.useEffect)(()=>{
  // Microkernel RTOS ASIL-D base (110 MB y 0.7% CPU de despacho)
  let baseRamMb = 110;
  let baseCpuPct = 0.7;

  let procRamMb = 0;
  let procCpuPct = 0;

  for (let proc of f) {
    if (proc.estado === "ejecucion" || proc.state === "ejecucion") {
      procRamMb += (proc.memoria_mb || 64);
      procCpuPct += (proc.cpu_pct || 1.0);
    } else {
      // Proceso pausado o en espera: conserva buffer estatico mínimo (25%) y CPU residual
      procRamMb += Math.round((proc.memoria_mb || 64) * 0.25);
      procCpuPct += 0.05;
    }
  }

  // Sobrecarga por escenarios de incidente
  let incRamMb = 0;
  let incCpuPct = 0;
  if (ie === "scen_can_attack") {
    incRamMb = 1180;
    incCpuPct = 54.8;
  } else if (ie === "scen_lidar" || ie === "fault_DEV_LIDAR_01") {
    incRamMb = 560;
    incCpuPct = 24.5;
  } else if (ie === "scen_bms_thermal" || ie === "fault_DEV_BATTERY_BMS") {
    incRamMb = 390;
    incCpuPct = 34.2;
  } else if (ie === "scen_telemetry_drop" || ie === "fault_DEV_GATEWAY_CAN" || ie === "fault_DEV_COM_5G") {
    incRamMb = 540;
    incCpuPct = 14.0;
  } else if (ie === "scen_camera_occlusion" || ie === "fault_DEV_CAM_FRONT") {
    incRamMb = 620;
    incCpuPct = 21.4;
  } else if (ie && typeof ie === "string" && ie.startsWith("fault_")) {
    incRamMb = 420;
    incCpuPct = 18.0;
  }

  // Buffer de hardware si hay dispositivos en falla
  let failedDevicesCount = u.filter(dev => dev.estado === "falla" || dev.estado === "degradado").length;
  let devBufferMb = failedDevicesCount * 75;

  let totalRamMb = baseRamMb + procRamMb + incRamMb + devBufferMb;
  let totalCpuPct = baseCpuPct + procCpuPct + incCpuPct;

  let calcRamPct = Math.min(98.5, Math.max(16.0, Math.round((totalRamMb / 4096 * 100) * 10) / 10));
  let calcCpuPct = Math.min(99.0, Math.max(4.0, Math.round(totalCpuPct * 10) / 10));

  l(prev => ({
    ...prev,
    ramUsage: calcRamPct,
    cpuUsage: calcCpuPct
  }));
},[f,ie,u]);"""

content = content[:start_idx] + new_media_and_telemetry_block + content[end_idx:]

# También actualizar fe para que todos los incidentes activen fallas y ae(e)
old_fe = "fe=(e,t)=>{de?(ae(e),s(`falla`),e===`scen_lidar`?(d(e=>e.map(e=>e.codigo===`DEV_LIDAR_01`?{...e,estado:`falla`,salud_porcentaje:24}:e)),l(e=>({...e,sensorHealthPct:81.2,sensorsOperational:15}))):e===`scen_bms_thermal`?(l(e=>({...e,batteryTemp:48.6,batterySoc:74,cpuUsage:68.4})),d(e=>e.map(e=>e.codigo===`DEV_BMS_01`?{...e,estado:`degradado`,salud_porcentaje:65}:e))):e===`scen_can_attack`&&l(e=>({...e,cpuUsage:89.2,ramUsage:78.4})),ue(`Simulación de Incidente: ${t}`,`advertencia`,`Disparo manual de escenario crítico de prueba`)):ue(`Intento no autorizado: ${t}`,`denegado`,`El rol ${h.rol} no tiene permisos de inyección de fallas`)}"

new_fe = "fe=(e,t)=>{de?(ae(e),s(`falla`),e===`scen_lidar`?(d(e=>e.map(e=>e.codigo===`DEV_LIDAR_01`?{...e,estado:`falla`,salud_porcentaje:24}:e)),l(e=>({...e,sensorHealthPct:81.2,sensorsOperational:15}))):e===`scen_bms_thermal`?(l(e=>({...e,batteryTemp:48.6,batterySoc:74})),d(e=>e.map(e=>e.codigo===`DEV_BMS_01`?{...e,estado:`degradado`,salud_porcentaje:65}:e))):e===`scen_can_attack`?d(e=>e.map(e=>e.codigo===`DEV_GATEWAY_CAN`?{...e,estado:`falla`,salud_porcentaje:18}:e)):e===`scen_telemetry_drop`?d(e=>e.map(e=>e.codigo===`DEV_COM_5G`||e.codigo===`DEV_GATEWAY_CAN`?{...e,estado:`degradado`,salud_porcentaje:35}:e)):e===`scen_camera_occlusion`&&d(e=>e.map(e=>e.codigo===`DEV_CAM_FRONT`?{...e,estado:`degradado`,salud_porcentaje:28}:e)),ue(`Simulación de Incidente: ${t}`,`advertencia`,`Disparo manual de escenario crítico de prueba`)):ue(`Intento no autorizado: ${t}`,`denegado`,`El rol ${h.rol} no tiene permisos de inyección de fallas`)}"

if old_fe in content:
    content = content.replace(old_fe, new_fe)
    print('OK: fe reemplazado correctamente.')
else:
    print('WARNING: old_fe no encontrado exactamente, buscando variaciones...')
    idx_fe = content.find('fe=(e,t)=>{de?(ae(e)')
    if idx_fe != -1:
        end_fe = content.find('El rol ${h.rol} no tiene permisos de inyección de fallas`)}', idx_fe)
        if end_fe != -1:
            end_fe += len('El rol ${h.rol} no tiene permisos de inyección de fallas`)}')
            content = content[:idx_fe] + new_fe + content[end_fe:]
            print('OK: fe reemplazado por rango.')

with open('Auto/autoos_interactive.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('OK: Auto/autoos_interactive.html guardado.')

# Copiar a web/public/autoos_interactive.html
shutil.copyfile('Auto/autoos_interactive.html', 'web/public/autoos_interactive.html')
print('OK: Copiado a web/public/autoos_interactive.html.')

# 2. Actualizar Auto/autoos_unified.html
with open('Auto/autoos_unified.html', 'r', encoding='utf-8') as f:
    u_content = f.read()

# Actualizar el cálculo de RAM en autoos_unified.html
old_ram_calc = """  var activeProcs = simState.processes.filter(function(p) { return p.state !== 'TERMINADO'; });
  var ramUsedMb = activeProcs.reduce(function(acc, p) { return acc + (p.memoryMb || 64); }, 128);
  var ramUsagePercent = Math.min(100, Math.round((ramUsedMb / 2048) * 100));"""

new_ram_calc = """  var activeProcs = simState.processes.filter(function(p) { return p.state === 'EJECUTANDO' || p.state === 'LISTO' || p.state === 'BLOQUEADO'; });
  var ramUsedMb = simState.processes.reduce(function(acc, p) {
    if (p.state === 'TERMINADO') return acc;
    if (p.state === 'SUSPENDIDO') {
      return acc + Math.round((p.memoryMb || 64) * 0.15);
    }
    if (p.state === 'EJECUTANDO') {
      var dynamicWorkingSet = Math.round(36 + 18 * Math.sin(simState.currentTime * 2.1 + (p.pid % 5)));
      return acc + (p.memoryMb || 64) + dynamicWorkingSet;
    }
    if (p.state === 'NUEVO') {
      return acc + Math.round((p.memoryMb || 64) * 0.35);
    }
    return acc + (p.memoryMb || 64);
  }, 180 + (devices && devices.some(function(d){ return d.status === 'falla'; }) ? 180 : 0));
  var ramUsagePercent = Math.min(99, Math.max(16, Math.round((ramUsedMb / 2048) * 100)));"""

if old_ram_calc in u_content:
    u_content = u_content.replace(old_ram_calc, new_ram_calc)
    print('OK: Cálculo de RAM reemplazado en autoos_unified.html.')
else:
    print('WARNING: old_ram_calc no encontrado directamente, buscando por subcadena...')
    idx_rc = u_content.find("var activeProcs = simState.processes.filter(function(p) { return p.state !== 'TERMINADO'; });")
    if idx_rc != -1:
        end_rc = u_content.find("var ramUsagePercent = Math.min(100, Math.round((ramUsedMb / 2048) * 100));", idx_rc)
        if end_rc != -1:
            end_rc += len("var ramUsagePercent = Math.min(100, Math.round((ramUsedMb / 2048) * 100));")
            u_content = u_content[:idx_rc] + new_ram_calc + u_content[end_rc:]
            print('OK: Cálculo de RAM reemplazado por rango en autoos_unified.html.')

# Actualizar el texto del card de RAM para mostrar porcentaje y MB
old_ram_text = "children: `${ramUsagePercent}%`"
new_ram_text = "children: `${ramUsagePercent}% (${ramUsedMb} MB)`"
if old_ram_text in u_content:
    u_content = u_content.replace(old_ram_text, new_ram_text, 1)
    print('OK: Card de RAM actualizado a porcentaje y MB.')

# 3. Sincronizar el Base64 en Auto/autoos_unified.html
with open('Auto/autoos_interactive.html', 'rb') as f:
    interactive_bytes = f.read()

new_b64 = base64.b64encode(interactive_bytes).decode('ascii')
b64_start_token = 'var b64 = "'
b64_start = u_content.find(b64_start_token)
if b64_start != -1:
    b64_val_start = b64_start + len(b64_start_token)
    b64_end = u_content.find('";', b64_val_start)
    if b64_end != -1:
        u_content = u_content[:b64_val_start] + new_b64 + u_content[b64_end:]
        print('OK: Base64 sincronizado exitosamente en Auto/autoos_unified.html.')
    else:
        print('ERROR: No se encontró el final del base64 en autoos_unified.html.')
else:
    print('ERROR: No se encontró var b64 = en autoos_unified.html.')

with open('Auto/autoos_unified.html', 'w', encoding='utf-8') as f:
    f.write(u_content)
print('OK: Auto/autoos_unified.html guardado.')
