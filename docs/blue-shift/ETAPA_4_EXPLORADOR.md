# AutoOS Blue Shift — Etapa V4: explorador de conducción

## Por qué se realizó este cambio

La vista original de Conducción mostraba ocho tarjetas uniformes (GPS, ADAS,
LiDAR, 5G, HVAC, audio, chat y CAN), sin explicar qué hacer primero. En una
presentación, el profesor necesitaba descubrir manualmente cada función.

**Objetivo:** pasar de «ver muchas tarjetas» a «elegir qué quiero consultar».
La interfaz V4 presenta una sola herramienta en primer plano, con propósito,
resultado esperado y una acción principal.

## Flujo de eventos

```text
CinematicMenu (menú inicial)
    │ onNavigate('COCKPIT')
    ▼
App.tsx (estado cockpitWorkspace=false)
    │
    ▼
CockpitExplorerV4 (selección de subsistema)
    │ onOpen('gps' | 'camera' | ...)
    ▼
App.tsx (cockpitWorkspace=true, cockpitFeature=id)
    │ iframe onLoad + postMessage('AUTOOS_V4_OPEN_FEATURE')
    ▼
Cockpit bridge V4 (HTML independiente)
    │ clic en pestañas existentes
    ▼
Cockpit React heredado (mantiene estado, handlers y RBAC)
```

El explorador NO contiene mediciones simuladas: `FEATURES` es un catálogo de
textos pedagógicos. Las métricas y acciones reales siguen en el Cockpit.

## Código y responsabilidades

- `web/src/components/CockpitExplorerV4.tsx`: catálogo, selección, navegación,
  texto accesible y llamada `onOpen`.
- `web/src/experience-v4.css`: estilos oblicuos, escena activa, animaciones,
  accesibilidad y variantes claro/oscuro.
- `web/src/App.tsx`: estado de vista y puente del iframe (`postMessage`).
- `web/src/cockpit-bridge-v4.js`: recibe intención de abrir subsistema y
  hace clic en pestañas existentes, sin alterar sus permisos.
- `web/src/cockpit-light-v4.css`: tema claro/oscuro del Cockpit heredado,
  que usa colores literales de Tailwind.
- `web/src/components/CinematicMenu.tsx`: permite cambiar tema antes de entrar.
- `web/src/components/ModuleOrientationV3.tsx`: abre guía de tres pasos en
  Simulación y Planificador, mientras que Conducción usa su nuevo explorador.

## Por qué el iframe no se elimina

El Cockpit es una página HTML independiente con lógica propia, incluso con
reproductor de Spotify. Si lo reescribiéramos desde cero perderíamos funciones
y validaciones que ya implementó el equipo. V4 solo lo abre cuando se necesita.

## Cómo se evita el recorte de pantalla

El iframe del Cockpit informa su altura al padre React a través del mensaje
`AUTOOS_V4_COCKPIT_HEIGHT` (validado, límites 480–15000 px). El React padre
ajusta la altura del iframe; su propio `iframeResize.ts` puede informar la
altura general a Streamlit. Si el host no admite cambios automáticos, todavía
podría aparecer scroll externo: verificar al desplegar.

## Modo claro y oscuro

React persiste la preferencia en `localStorage` (`autoos_theme`). El botón de
modo claro/oscuro aparece en el menú inicial y la cabecera de módulos. El tema
se propaga al Cockpit mediante `AUTOOS_SET_THEME`; los dos estilos de Cockpit
se ajustan de acuerdo con la clase `dark` del documento interno.

**Limitación:** el pequeño encabezado que dibuja Streamlit sigue siendo un
contenedor de la aplicación y no cambia dinámicamente con la selección interna
de React. El contenido principal sí debe cambiar de tema.

## Lista de demostración para el profesor

1. Elegir Conducción y explicar la diferencia entre herramienta y sistema.
2. Seleccionar GPS: leer propósito y resultado esperado; pulsar «Abrir GPS».
3. Consultar las coordenadas y trayectoria en la herramienta original.
4. Regresar a «Explorar otro sistema» y abrir Multimedia o Seguridad.
5. Probar el modo claro y oscuro desde el menú, y nuevamente dentro del módulo.
6. Abrir Simulación y seguir sus tres pasos; concluir con un informe.
7. Abrir Planificador como Mecánico; ejecutar RR y explicar Gantt.
8. Mostrar que el Pasajero no puede abrir acciones restringidas.

## Pruebas necesarias antes de publicar

Desde `AutoOS/web`:

```powershell
npm run lint
npm run test:sim
npm run build
```

Volver a `AutoOS`:

```powershell
python .\tools\build_streamlit_bundle.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Revisar visualmente a 1920x1080 y 1366x768. Hacer clic real en cada una de las
ocho herramientas. Probar roles, tema, navegación de regreso, audio y Spotify.

Las 130 pruebas Python verifican el núcleo, pero NO verifican estas interacciones
de navegador. Tampoco prueban acceso real a Supabase en Streamlit Cloud.

## GitHub y reversión

Guardar este trabajo en una rama `feature/`, no directamente en `main`.
En el Pull Request adjuntar capturas de los dos temas y describir los cambios.
Si se presenta algún error en producción, revertir el commit de V4 o usar
las copias de seguridad del instalador guardadas en `%USERPROFILE%\.autoos-v4-backups`.
No agregar estas copias al repositorio.
