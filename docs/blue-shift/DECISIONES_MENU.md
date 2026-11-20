# Registro de decisiones — Menú cinematográfico

## DC-01: separar vista y motores
**Decisión:** mantener `CinematicMenu.tsx` como componente de presentación. **Motivo:** el núcleo, la planificación y las simulaciones existentes ya tienen reglas y pruebas; mezclar la nueva animación con ellos aumentaría el riesgo de regresiones.

## DC-02: entrada predeterminada en Streamlit
**Decisión:** Streamlit inicia en la experiencia React integrada con `components.html`. **Motivo:** el profesor debe ver el menú cinematográfico en la URL pública, no solo en localhost:3000.

## DC-03: preservar el dashboard Python
**Decisión:** un botón «Panel RTOS completo» abre las nueve pestañas del dashboard original. **Motivo:** React no reemplaza el kernel, los logs, VFS ni el RBAC Python.

## DC-04: sonidos originales sintetizados
**Decisión:** usar Web Audio API tras interacción del usuario, con control para silenciar. **Motivo:** el menú debe responder de manera perceptible sin depender de archivos externos.

## DC-05: compilación reproducible
**Decisión:** generar `Auto/autoos_unified.html` desde `web/dist` con un empaquetador que localiza los assets de Vite por HTML y no por nombres fijos. **Motivo:** Vite cambia los hash de CSS/JS cuando cambia el código.

## Trabajo pendiente
- Revisar el aspecto real en Streamlit local y ajustar el diseño a diferentes resoluciones.
- Mejorar las pantallas interiores para que tengan la misma identidad, sin perder controles existentes.
- Probar construcción Vite y flujos manuales en el computador del equipo.
- Confirmar visualmente la publicación en `https://autoos.streamlit.app/autoos_interactive.html`.
- No declarar sincronización entre roles/estado del kernel Python y React hasta implementar una comunicación explícita.
