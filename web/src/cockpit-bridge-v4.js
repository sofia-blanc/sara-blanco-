/*
 * AUTOOS V4 — Puente para el Cockpit HTML heredado.
 *
 * ¿Por qué existe? El cockpit se ejecuta en un iframe independiente y mantiene
 * sus propios estados y eventos. React le envía una INTENCIÓN de navegación.
 * Este puente utiliza los controles existentes: no sustituye validaciones RBAC.
 *
 * También informa a React su altura real para evitar scroll doble y footer
 * cortado. No lee cookies, claves ni información de Supabase.
 */
(function () {
  'use strict';
  var lastHeight = 0;
  var scheduled = false;

  function measure() {
    scheduled = false;
    var root = document.getElementById('root');
    if (!root || !root.getBoundingClientRect().width) return;
    var height = Math.ceil(Math.max(root.scrollHeight, root.getBoundingClientRect().height, document.body.scrollHeight));
    height = Math.min(15000, Math.max(480, height + 20));
    if (Math.abs(lastHeight - height) < 10) return;
    lastHeight = height;
    window.parent.postMessage({ type: 'AUTOOS_V4_COCKPIT_HEIGHT', height: height }, '*');
  }
  function requestMeasure() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(measure);
  }

  function clickButton(exactLabels) {
    var buttons = Array.prototype.slice.call(document.querySelectorAll('button'));
    // Comparación por texto visible; se evita un selector CSS frágil del build.
    for (var i = 0; i < exactLabels.length; i++) {
      var wanted = exactLabels[i].toLocaleLowerCase('es').trim();
      var found = buttons.find(function (button) {
        return button.textContent && button.textContent.toLocaleLowerCase('es').replace(/\s+/g, ' ').trim() === wanted;
      });
      if (found) { found.click(); return true; }
    }
    return false;
  }
  function openFeature(feature, attempts) {
    attempts = attempts || 0;
    var nav = {
      gps: { tab: ['Subsistemas Vehiculares'], sub: ['GPS y Ruta'] },
      camera: { tab: ['Subsistemas Vehiculares'], sub: ['Cámara ADAS'] },
      lidar: { tab: ['Subsistemas Vehiculares'], sub: ['LiDAR 360°'] },
      network: { tab: ['Subsistemas Vehiculares'], sub: ['Telemetría 5G', 'Bus CAN Gateway'] },
      climate: { tab: ['Subsistemas Vehiculares'], sub: ['Climatización HVAC'] },
      media: { tab: ['Multimedia'] },
      chat: { tab: ['Subsistemas Vehiculares'], sub: ['Chat de Cabina'] },
      security: { tab: ['Seguridad y Roles RBAC'] },
      overview: { tab: ['Panel Principal'] },
    };
    if (!Object.prototype.hasOwnProperty.call(nav, feature)) return;
    var destination = nav[feature];
    // El bundle React puede tardar en montar los botones después de cargar el iframe.
    if (!clickButton(destination.tab)) {
      if (attempts < 16) setTimeout(function () { openFeature(feature, attempts + 1); }, 190);
      return;
    }
    if (destination.sub) {
      // El cambio de pestaña React necesita un render antes de mostrar submenú.
      setTimeout(function () { clickButton(destination.sub); requestMeasure(); }, 180);
    }
    setTimeout(requestMeasure, 350);
  }

  window.addEventListener('message', function (event) {
    if (event.source !== window.parent || !event.data) return;
    if (event.data.type === 'AUTOOS_V4_OPEN_FEATURE') openFeature(event.data.feature);
    if (event.data.type === 'AUTOOS_V4_MEASURE') requestMeasure();
  });

  function boot() {
    var root = document.getElementById('root');
    if (!root) return;
    if ('ResizeObserver' in window) new ResizeObserver(requestMeasure).observe(root);
    if ('MutationObserver' in window) {
      new MutationObserver(requestMeasure).observe(root, { childList:true, subtree:true });
    }
    window.addEventListener('resize', requestMeasure);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(requestMeasure).catch(function () {});
    requestMeasure();
    setTimeout(requestMeasure, 500);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once:true });
  else boot();
})();
