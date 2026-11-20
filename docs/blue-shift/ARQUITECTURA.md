# Arquitectura real de AutoOS

> Este documento describe **lo observado** en el ZIP del proyecto. No presupone que Streamlit y React compartan automáticamente los mismos estados.

```text
GitHub (rama publicada)
    |
    +--> app.py (raíz)                   Inicia Auto/app.py mediante runpy
             |
             +--> Auto/app.py           Dashboard Python de Streamlit
                     |                   9 pestañas: boot, procesos, scheduler,
                     |                   RAM, virtual, VFS, terminal, cockpit, seguridad
                     |
                     +--> Auto/kernel_bridge.py    Estado del kernel Python
                     +--> Auto/config.py           Supabase Python/fallback local
                     +--> Auto/modules/*           Autenticación, sensores, telemetría...
                     |
                     +--> Pestaña «Tablero y Sensores»
                            |
                            +--> Auto/autoos_interactive.html
                            |      Cockpit independiente (opción inicial)
                            |
                            +--> Auto/autoos_unified.html
                                   React empaquetado (opción alternativa)

web/src/App.tsx -> npm run build -> web/dist -> tools/build_streamlit_bundle.py
                                                   -> Auto/autoos_unified.html
```

## Entradas del proyecto

- **`app.py` en la raíz:** cambia el directorio de trabajo a `Auto/` e inicia `Auto/app.py`.
- **`Auto/app.py`:** dashboard Streamlit; define nueve pestañas, la barra lateral y los controles Python.
- **`Auto/modules/ui_components.py`:** estilos y componentes visuales del dashboard Streamlit.
- **`web/src/App.tsx`:** pantalla de React con las vistas `SCHEDULER`, `SIMULATOR` y `COCKPIT`.
- **`web/src/components/SimulationCenter.tsx`:** interfaz de escenarios y decisiones del simulador React.
- **`web/src/simulation/engine.ts`:** operaciones de estado sobre los escenarios; separadas de la apariencia.
- **`web/src/types/scheduler.ts`:** contratos de tipos de procesos, roles y métricas.
- **`web/src/supabaseClient.ts`:** cliente de acceso a Supabase usado por el frontend, distinto del cliente Python.
- **`Auto/autoos_unified.html`:** archivo generado que Streamlit muestra con `components.html(...)`.

## El estado no es global entre las dos tecnologías

El dashboard de Streamlit utiliza estado Python (`st.session_state`, `kernel_bridge`). La aplicación React maneja estado con React y comunica algunos eventos al Cockpit HTML por `postMessage`. La mera inclusión en un iframe **no sincroniza** estado de procesos, rol, telemetría o conexión a la nube con el kernel Python.

**Regla:** cuando una característica deba cruzar Streamlit ↔ React, escribir un contrato explícito de mensajes o una API antes de afirmar que están sincronizados. Si la comunicación no existe, documentar claramente esa limitación.

## Derechos y responsabilidades del rediseño

| Capa | Cambios permitidos | Precaución |
|---|---|---|
| React / CSS | Menú, pantallas, animaciones, textos | Mantener callbacks y lógica ya conectada |
| HTML de Cockpit | Presentación y recursos | Conservar controles, eventos y mensajes existentes |
| Streamlit | Pantalla de entrada, diseño y estructura de navegación | No romper las nueve pestañas académicas ni el estado Python |
| Kernel | Sin cambios de lógica en la primera etapa | Conservar procesos, RAM, algoritmos y eventos |
| Supabase | Sin modificaciones iniciales | No tocar secretos, RLS, claves ni conexiones de Julián |
| Empaquetador | Generación reproducible desde `web/dist` | Verificar que incluya CSS, JS, Cockpit y recursos de audio/fuentes |

## Comandos de comprobación (PowerShell, raíz `AutoOS`)

```powershell
# Python: versión del dashboard y pruebas del sistema
.\.venv\Scripts\python.exe -m py_compile Autopp.py
Push-Location .\AutoOS_1
..\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
Pop-Location

# React: análisis de tipos, pruebas y compilación
Push-Location .\web
npm ci
npm run lint
npm run test:sim
npm run build
Pop-Location

# Integración para Streamlit (archivo creado en la primera etapa Blue Shift)
python .	oolsuild_streamlit_bundle.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

El script `tools/build_streamlit_bundle.py` corresponde a la etapa Blue Shift previamente suministrada; no está en el ZIP original. La validación debe hacerse sobre la copia local real. `npm run build` por sí solo **no publica** la vista React dentro de Streamlit.
