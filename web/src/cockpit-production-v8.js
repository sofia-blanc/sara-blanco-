/**
 * AUTOOS V8 — reparador semántico de Multimedia.
 *
 * El Cockpit original es un HTML React ya compilado que contiene los callbacks
 * reales de Bluetooth y Spotify. No reemplazamos esas funciones. Solo agregamos
 * atributos a controles existentes para darles contraste y dimensiones correctas.
 *
 * MutationObserver detecta cambios legítimos de React (p.ej. al abrir Multimedia)
 * y no observa atributos, evitando dispararse por nuestras propias etiquetas.
 */
(function () {
  'use strict';
  var pending = false;
  function normalize(text) { return (text || '').replace(/\s+/g, ' ').trim().toLocaleLowerCase('es'); }
  function enhance() {
    pending = false;
    var root = document.getElementById('root');
    if (!root) return;
    var title = root.querySelector('input[placeholder^="Título opcional"]');
    var uri = root.querySelector('input[placeholder^="Enlace Spotify"]');
    if (title && uri && title.parentElement === uri.parentElement) {
      title.parentElement.classList.add('autoos-v8-spotify-form');
      title.setAttribute('aria-label', 'Nombre opcional para guardar la playlist');
      uri.setAttribute('aria-label', 'Enlace de Spotify de una canción o playlist');
    }
    var buttons = root.querySelectorAll('button');
    for (var i = 0; i < buttons.length; i++) {
      var button = buttons[i];
      var label = normalize(button.textContent);
      var action = '';
      if (label.indexOf('emparejar por bluetooth') !== -1 || label.indexOf('escaneando ble') !== -1) action='bluetooth';
      else if (label.indexOf('abrir en spotify web') !== -1) action='spotify-web';
      else if (label.indexOf('copiar enlace spotify') !== -1) action='spotify-copy';
      else if (label.indexOf('cargar y guardar') !== -1) action='spotify-load';
      if (action) button.setAttribute('data-autoos-v8-action', action);
    }
    var links = root.querySelectorAll('a[href*="open.spotify.com"]');
    for (var j = 0; j < links.length; j++) {
      if (normalize(links[j].textContent).indexOf('abrir en celular') !== -1) {
        links[j].setAttribute('data-autoos-v8-action', 'spotify-open');
      }
    }
  }
  function schedule() {
    if (pending) return;
    pending = true;
    window.requestAnimationFrame(enhance);
  }
  function boot() {
    var root = document.getElementById('root');
    if (!root) { window.setTimeout(boot, 100); return; }
    new MutationObserver(schedule).observe(root, {childList:true, subtree:true, characterData:true});
    window.addEventListener('resize', schedule);
    schedule();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, {once:true});
  else boot();
})();
