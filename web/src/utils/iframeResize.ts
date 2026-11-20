/**
 * AUTOOS / STREAMLIT — Adaptador opcional de altura del iframe.
 *
 * Streamlit inserta la aplicación React en components.html (iframe srcdoc).
 * Si el HTML interno crece y el iframe conserva una altura fija, aparecen
 * una segunda barra de desplazamiento y pantallas recortadas.
 *
 * Este módulo comunica la altura REAL del componente raíz mediante el
 * protocolo de componentes Streamlit V1: streamlit:setFrameHeight.
 * Si el host no escucha el mensaje, components.html sigue permitiendo scroll.
 *
 * OBSERVACIÓN: medimos #root, no body.scrollHeight, para poder REDUCIR
 * la altura al volver desde una pantalla larga al menú principal.
 */
export function startStreamlitAutoResize(): () => void {
  const root = document.getElementById('root');
  if (!root || window.parent === window) return () => {};

  let animationFrame = 0;
  let previousHeight = -1;
  const update = () => {
    animationFrame = 0;
    const actualHeight = Math.ceil(root.getBoundingClientRect().height);
    const height = Math.max(760, Math.min(12000, actualHeight + 12));
    if (Math.abs(height - previousHeight) < 5) return;
    previousHeight = height;
    window.parent.postMessage(
      { isStreamlitMessage: true, type: 'streamlit:setFrameHeight', height },
      '*',
    );
  };
  const schedule = () => {
    if (animationFrame === 0) animationFrame = requestAnimationFrame(update);
  };
  const resizeObserver = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(schedule) : null;
  resizeObserver?.observe(root);
  const mutationObserver = typeof MutationObserver !== 'undefined'
    ? new MutationObserver(schedule) : null;
  mutationObserver?.observe(root, { childList: true, subtree: true });
  window.addEventListener('resize', schedule);
  schedule();
  // Recalcular cuando termina la animación inicial o carga una fuente.
  const delayed = window.setTimeout(schedule, 700);
  return () => {
    window.removeEventListener('resize', schedule);
    window.clearTimeout(delayed);
    resizeObserver?.disconnect();
    mutationObserver?.disconnect();
    if (animationFrame) cancelAnimationFrame(animationFrame);
  };
}
