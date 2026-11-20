# AutoOS — Guía de entrega y exposición (V8)

## Arquitectura que debe comprender el equipo

```text
GitHub main -> app.py -> Auto/app.py (Streamlit) ->
  Auto/autoos_unified.html -> React (web/src/App.tsx) ->
    Menú cinematográfico / Simulador / Planificador / Cockpit (iframe)
```

El HTML de Streamlit se obtiene con `npm run build` y después `python tools/build_streamlit_bundle.py`. **No basta editar React y hacer push**: `Auto/autoos_unified.html` debe estar actualizado y versionado. La consola de Streamlit no compila automáticamente el frontend.

### Archivos de presentación

- `web/src/components/CinematicMenu.tsx`: menú animado y navegación por teclado.
- `web/src/components/ModuleScene.tsx`: cabecera de cada módulo y selector de tema.
- `web/src/components/CockpitToolSceneV6.tsx`: selector contextual de instrumentos.
- `web/src/production-v8.css`: capa FINAL de colores/contraste de React. Corrige la cascada CSS de la cabecera.
- `web/src/cockpit-production-v8.css`: tamaño legible de inputs y botones del Cockpit.
- `web/src/cockpit-production-v8.js`: añade atributos de presentación a controles reales del Cockpit. No sustituye sus callbacks.
- `tools/instalar_v8.py`: instala V8 y crea respaldo temporal.
- `tools/finalizar_autoos.ps1`: verifica TypeScript, escenarios, compilación, HTML Streamlit y pruebas Python.

### Causa de los bugs corregidos

**Título invisible en tema claro.** La regla `#root > div > header` aplicaba un fondo claro a cualquier header con una especificidad mayor que los selectores `.autoos-stage`. V8 evita que el selector genérico capture el encabezado escénico, y establece contrastes explícitos por módulo.

**Campos mínimos de Spotify.** El Cockpit original usa una fila `flex` y `max-w-lg` para *Título opcional*, *Enlace Spotify* y *Cargar y guardar*. A 1080p el enlace se encogía hasta casi desaparecer. V8 usa tres columnas flexibles, con una versión vertical en pantallas estrechas. El botón conserva su `onClick` original.

**Botones invisibles.** Varias clases declaraban texto blanco y fondo blanco simultáneamente al alternar el tema. V8 marca únicamente los botones originales de Bluetooth/Spotify y establece pares explícitos de color y fondo.

**Alcance.** Los formularios, Spotify y Bluetooth siguen sujetos a permisos del navegador, disponibilidad de Internet y servicios externos. El botón global SONIDO OFF del menú puede detener el iframe de Spotify; no controla una sesión externa abierta en otra aplicación.

## Pasos únicos para generar la versión publicable

Desde PowerShell, en la raíz del proyecto:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\finalizar_autoos.ps1
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Revisar en `http://localhost:8501` ambas modalidades de tema y los tres módulos, primero como mecánico, luego como conductor y pasajero. No introducir claves privadas en GitHub.

## Guion de demostración para cualquier integrante

1. **Menú inicial:** cambiar tema y entrar a Conducción; explicar selección animada y eventos de teclado.
2. **GPS:** explicar el propósito de la telemetría y mostrar mapa e indicadores sin recortar la pantalla.
3. **Multimedia:** demostrar que los campos *Título opcional* y *Enlace Spotify* son legibles; cargar un enlace válido y explicar límites del reproductor externo.
4. **Simulación:** seleccionar una falla, ejecutarla, leer diagnóstico, tomar decisiones y restablecer.
5. **Planificador:** cambiar a mecánico, comparar FCFS/RR/Prioridades, ejecutar ticks y leer Gantt.
6. **Seguridad:** cambiar perfil y demostrar que el control de acceso es funcional, no solo cosmético.
7. **Arquitectura:** explicar cómo Streamlit sirve el bundle React y cómo el iframe mantiene intactas las herramientas originales.

## Publicación en GitHub y Streamlit

Trabajar en rama `feature/`. Confirmar que el PR incluye el HTML generado `Auto/autoos_unified.html` y las dos copias del Cockpit. No fusionar sin pruebas locales. La aplicación pública se actualiza cuando se integra en la rama conectada a Streamlit; comprobar el enlace público y la versión visible antes de la exposición.

## Límites de comprobación

Las pruebas automáticas no demuestran que haya conexión real a Supabase, que Web Bluetooth disponga de dispositivos o que Spotify pueda reproducir audio en todos los equipos. Esos tres servicios requieren comprobación en el navegador de la exposición. Los controles gráficos son de un proyecto académico; no equivalen a certificación de seguridad vehicular real.
