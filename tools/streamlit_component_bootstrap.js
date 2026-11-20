/*
 * AUTOOS V10 — componente bidireccional Streamlit (API V1).
 *
 * `components.html()` solo dibuja HTML. En cambio, la API de componentes
 * declarados permite que JavaScript devuelva un valor y reciba argumentos.
 * Se implementa el protocolo JSON mínimo; no requiere otro npm package.
 * https://docs.streamlit.io/develop/concepts/custom-components/components-v1/intro
 */
(function () {
  'use strict';
  var latest = null;
  var lastHeight = -1;
  function post(type, extra) {
    window.parent.postMessage(Object.assign({ isStreamlitMessage: true, type: type }, extra || {}), '*');
  }
  function reportHeight() {
    // Igualar el cálculo de iframeResize.ts para evitar alturas fluctuantes.
    var root = document.getElementById('root');
    var contentHeight = root ? Math.ceil(root.getBoundingClientRect().height) : document.body.scrollHeight;
    var height = Math.max(760, Math.min(12000, contentHeight + 12));
    if (height !== lastHeight) {
      lastHeight = height;
      post('streamlit:setFrameHeight', { height: height });
    }
  }
  function onMessage(event) {
    // Los mensajes de otros iframes, incluidos Spotify y Cockpit, NO se aceptan.
    if (event.source !== window.parent || !event.data || event.data.type !== 'streamlit:render') return;
    var next = event.data.args && event.data.args.kernel;
    if (next && typeof next.tick === 'number') {
      latest = next;
      window.__AUTOOS_KERNEL_COMPONENT__.latest = next;
      window.dispatchEvent(new CustomEvent('autoos:kernel-update', { detail: next }));
    }
    window.requestAnimationFrame(reportHeight);
  }
  window.__AUTOOS_KERNEL_COMPONENT__ = {
    latest: latest,
    send: function (message) {
      if (!message || !['autoos:kernel-sync','autoos:cloud-test','autoos:cloud-event','autoos:cloud-report','autoos:blackbox-batch'].includes(message.type) /* AUTOOS_V14_BLACKBOX_CLOUD */) return;
      post('streamlit:setComponentValue', { value: message, dataType: 'json' });
    }
  };
  window.addEventListener('message', onMessage);
  post('streamlit:componentReady', { apiVersion: 1 });
  window.addEventListener('load', reportHeight);
  if (typeof ResizeObserver !== 'undefined') {
    var watcher = new ResizeObserver(reportHeight);
    watcher.observe(document.documentElement);
  }
})();
