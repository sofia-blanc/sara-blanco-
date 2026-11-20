/**
 * AutoOS V6: puente de presentación dentro del Cockpit HTML independiente.
 *
 * Este documento contiene un React compilado que no debe desmontarse porque
 * perderíamos sus controles (GPS, ADAS, Spotify y auditoría). Cuando el padre
 * abre una herramienta por el puente V4, ocultamos SOLAMENTE la barra de
 * pestañas duplicada. El puente V4 sigue pudiendo pulsar esos botones con JS.
 *
 * IMPORTANTE: La vista HTML independiente se conserva sin cambios cuando
 * no recibe el mensaje de navegación desde la aplicación AutoOS.
 */
(function () {
  'use strict';
  var active = false;
  var scheduled = false;
  function collapseRedundantNavigation() {
    scheduled = false;
    if (!active) return;
    var buttons = document.querySelectorAll('#root button');
    for (var i = 0; i < buttons.length; i++) {
      var button = buttons[i];
      var text = (button.textContent || '').replace(/\s+/g, ' ').trim();
      if (text !== 'Panel Principal') continue;
      var row = button.parentElement;
      if (row && row.querySelectorAll('button').length >= 3) {
        row.dataset.autoosV6DuplicateNav = 'true';
      }
      break;
    }
  }
  function schedule() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(collapseRedundantNavigation);
  }
  window.addEventListener('message', function (event) {
    if (event.source !== window.parent || !event.data) return;
    if (event.data.type !== 'AUTOOS_V4_OPEN_FEATURE') return;
    active = true;
    document.documentElement.dataset.autoosV6Embedded = 'true';
    schedule();
  });
  function boot() {
    var root = document.getElementById('root');
    if (!root) return;
    new MutationObserver(schedule).observe(root, { childList: true, subtree: true });
    schedule();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();
})();
