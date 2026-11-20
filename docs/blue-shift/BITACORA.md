# Bitácora de cambios y decisiones — AutoOS Blue Shift

| Etapa | Estado | Cambios principales | Verificación y Pruebas | Limitaciones y Resguardo |
|---|---|---|---|---|
| **0. Análisis de Arquitectura** | Completado | Mapeo de la convivencia dual Streamlit–HTML–React (`app.py`, `Auto/autoos_unified.html` y `web/src/App.tsx`). | Inspección de flujos, variables globales y postMessage. | Los entornos desacoplados requieren sincronización explícita de estado. |
| **1. Tema Blue Shift** | Completado | Definición de paleta automotriz oscura de alto contraste (#030712, cian, cobalto). | Compilación CSS y previsualización en Streamlit/Vite. | Variables CSS deben coexistir con Tailwind v4 sin colisiones. |
| **2. Menú Cinematográfico** | Completado | Componente interactivo `CinematicMenu.tsx` y escenas de presentación de módulos. | Navegación por teclado (flechas, Enter) y clics de mouse. | No interfiere con el motor de simulación subyacente. |
| **3. Usabilidad, Audio y UTF-8** | Completado | Corrección de tildes/caracteres corruptos, control centralizado de audio ambiental vs Spotify. | Prueba en navegador de eventos de audio y decodificación UTF-8. | Autoplay restringido por políticas de seguridad del navegador. |
| **4. Explorador de Conducción V4** | Completado | `CockpitExplorerV4.tsx`: guía interactiva de 8 subsistemas para evaluación docente. | Prueba de recorrido interactivo y conmutación de subsistemas. | No reemplaza la vista técnica detallada de cada sensor. |
| **5. Tema Claro, RBAC y Ancho V5** | Completado | Corrección del iframe colapsado a 450px (`width: 100%`), modo Claro y sincronización RBAC. | Cambio dinámico de rol (Mecánico/Conductor/Pasajero) y tema. | Permisos denegados en iframe se notifican vía postMessage. |
| **6. Corrección Estructural V6** | Completado | Eliminación de pestañas redundantes, aislamiento en `CockpitToolSceneV6.tsx`. | Inspección visual en pantallas completas sin scroll doble. | Mantiene compatibilidad con el bundle unificado de Streamlit. |
| **7. Contraste Visual V7** | Completado | Arreglo de contraste en inputs de texto de Spotify y títulos cinematográficos en modo claro. | Pruebas de accesibilidad WCAG en modo claro y oscuro. | Mantiene fidelidad estilística automotriz sin saturación. |
| **8. Estabilización y Entrega V8** | Completado | Empaquetado de estilos en `production-v8.css` y puente de producción `cockpit-production-v8.js`. | Pruebas integradas de navegación sin fugas de eventos. | Se preserva la arquitectura sin agregar dependencias pesadas. |
| **9. Simulación de Recursos SO V9** | Completado | `OSResourceMonitor.tsx` y `simulation/resources.ts`: telemetría unificada de CPU, RAM y bus CAN. | Escenarios de carga aplicados sobre una sola instancia React. | Telemetría didáctica orientada a simulación de SO automotriz. |
| **10. Kernel Bridge Python <-> React** | Completado | Puente IPC bidireccional (`kernel_bridge.py`, `kernelBridge.ts`) entre React y el kernel Python. | Envío y recepción de ticks de CPU, despacho y estados PCB. | Requiere servidor local o componente Streamlit activo. |
| **11. Arquitectura y Sustentación V11** | Completado | `AutoOSModulesV11.tsx`, `Auto/v11_cloud_bridge.py`, reportes técnicos de evaluación. | Suite de pruebas unitarias (`test_full_integration.py`). | Documenta claramente el alcance didáctico del simulador. |
| **12. Cabina, Bluetooth y Rendimiento** | Completado | Botón BLE, integración de streaming multimedia con bajo retardo y telemetría reactiva. | `test_bluetooth_v12.cjs` ejecutado exitosamente con Node.js. | El emparejamiento BLE usa simulación Web Bluetooth API. |
| **13. Confirmación Eventos Supabase** | Completado | Protocolo con `requestId` y `cloud.ack` para evitar falsos timeouts en inserciones. | Inserción y confirmación verificada en `public.eventos`. | Dependiente de conexión a Internet para persistencia remota. |
| **14. Caja Negra Sincronizada** | Completado | `blackboxSync.ts` y `blackbox_cloud_sync.py`: cola de eventos en batches con desduplicación. | 24 eventos confirmados en Supabase (`caja_negra_autoos`). | Eventos rutinarios de ruta se muestrean para no saturar la BD. |
| **15. Telemetría Reactiva RAM/CPU** | Completado | Sincronización en tiempo real del uso de memoria RAM y CPU ante procesos, fallas y calibración. | Validación sintáctica `node --check` y pruebas dinámicas en UI. | RAM modelada sobre base determinística ASIL-D de 4096 MB. |

---

## Registros Detallados de Decisiones y Cambios por Etapa

### Etapa 0: Análisis de Arquitectura y Coexistencia Dual
- **Fecha:** 2026-11-05
- **Autor/es:** Integrante 4 (Integración) & Integrante 3 (Seguridad)
- **Commit / PR:** `init-architecture-analysis`
- **Archivos tocados:** `app.py`, `Auto/app.py`, `Auto/autoos_unified.html`, `web/src/App.tsx`.
- **Objetivo:** Comprender la estructura del proyecto y la relación entre la versión Streamlit Cloud y la interfaz React local.
- **Cómo funciona:** `app.py` en la raíz actúa como lanzador universal que redirecciona a `Auto/app.py`, el cual incrusta mediante `st.components.v1.html` el archivo consolidado `Auto/autoos_unified.html` con un iframe reactivo.
- **Decisiones técnicas:** Mantener sincronizados el bundle HTML base64 y el código fuente React en `web/src/` para garantizar despliegue consistente.
- **Qué NO se modificó:** La lógica del kernel Python en `AutoOS_1/` ni los esquemas SQL de Supabase.
- **Comandos de prueba + resultado:** `python -m py_compile app.py` -> Exitoso (código 0).
- **Problemas encontrados y solución:** Discrepancias entre rutas relativas resueltas usando `Path(__file__).resolve()`.
- **Explicación breve para la exposición:** Se diseñó una arquitectura desacoplada donde el frontend interactivo funciona tanto en local como dentro de la nube de Streamlit.

---

### Etapa 1: Tema Visual Automotriz «Blue Shift»
- **Fecha:** 2026-11-08
- **Autor/es:** Integrante 4 (Interfaz e Integración)
- **Commit / PR:** `feat/blue-shift-theme`
- **Archivos tocados:** `web/src/blue-shift.css`, `Auto/styles/blue_shift_streamlit.css`, `Auto/styles/blue_shift_cockpit.css`.
- **Objetivo:** Reemplazar el esquema visual genérico por una interfaz automotriz inmersiva de alto impacto estético y legibilidad técnica.
- **Cómo funciona:** Inyección de tokens de diseño: fondos oscuro obsidiana (`#030712`, `#0b1528`), acentos cian eléctrico (`#06b6d4`), cobalto ASIL (`#3b82f6`) y alertas ámbar/rojo normalizadas.
- **Decisiones técnicas:** Utilizar variables CSS para soporte simultáneo de modo Claro y modo Oscuro sin duplicar clases de maquetación.
- **Qué NO se modificó:** Algoritmos de planificación ni estructuras de datos de procesos.
- **Comandos de prueba + resultado:** Verificación en navegadores Chrome y Edge con emulación de temas del sistema.
- **Problemas encontrados y solución:** Conflictos de contraste en títulos resueltos asignando variables `--text-primary` y `--text-muted` explícitas.
- **Explicación breve para la exposición:** Blue Shift otorga una identidad visual automotriz profesional, cumpliendo con estándares de contraste ergonómico para cabinas vehiculares.

---

### Etapa 2: Escenas Cinematográficas y Menú Inmersivo
- **Fecha:** 2026-11-10
- **Autor/es:** Integrante 4 (Interfaz)
- **Commit / PR:** `feat/cinematic-menu`
- **Archivos tocados:** `web/src/components/CinematicMenu.tsx`, `web/src/components/ModuleScene.tsx`, `web/src/cinematic-menu.css`.
- **Objetivo:** Proporcionar una pantalla de entrada impactante donde el profesor pueda seleccionar y explorar los módulos principales (Conducción, Simulación, Planificador).
- **Cómo funciona:** Menú con animaciones fluidas basadas en CSS transforms y aceleración por GPU, operable tanto con ratón como con teclado (flechas de navegación y tecla Enter).
- **Decisiones técnicas:** Aislar la presentación en `CinematicMenu.tsx` para no acoplar la navegación con la lógica interna de despacho de CPU.
- **Qué NO se modificó:** Estado global de simulación ni conexiones a Supabase.
- **Comandos de prueba + resultado:** Navegación por teclado validada en `npm run dev`.
- **Problemas encontrados y solución:** Parpadeos en transiciones corregidos aplicando `backface-visibility: hidden` y `will-change: transform`.
- **Explicación breve para la exposición:** Permite introducir la sustentación con un menú de cabina cinemática que guía al evaluador por los tres pilares del sistema.

---

### Etapa 3: Usabilidad, Gestión de Audio y Normalización UTF-8
- **Fecha:** 2026-11-11
- **Autor/es:** Integrante 4 (Interfaz) & Integrante 1 (Procesos)
- **Commit / PR:** `fix/audio-utf8-polish`
- **Archivos tocados:** `web/src/App.tsx`, `Auto/autoos_interactive.html`, `web/src/module-polish-v3.css`.
- **Objetivo:** Eliminar caracteres corruptos (mojibake como `MecÃ¡nico`) y coordinar el audio ambiental del menú con el reproductor multimedia.
- **Cómo funciona:** Normalización estricta de archivos a codificación UTF-8 sin BOM y control de silenciamiento inteligente que suspende efectos ambientales al iniciar Spotify.
- **Decisiones técnicas:** Respetar la política de navegadores que exige interacción previa del usuario antes de reproducir audio.
- **Qué NO se modificó:** Rutas de navegación ni permisos RBAC.
- **Comandos de prueba + resultado:** Verificación de cadenas de texto y renderizado de caracteres acentuados en consola y UI.
- **Problemas encontrados y solución:** Audio bloqueado por autoplay corregido añadiendo estado `audioUnlocked` tras el primer clic del usuario.
- **Explicación breve para la exposición:** Asegura una experiencia libre de errores ortográficos visuales y con control ergonómico de sonido en cabina.

---

### Etapa 4: Explorador de Conducción Vehicular V4
- **Fecha:** 2026-11-12
- **Autor/es:** Integrante 3 (Seguridad y Dispositivos) & Integrante 4 (Interfaz)
- **Commit / PR:** `feat/cockpit-explorer-v4`
- **Archivos tocados:** `web/src/components/CockpitExplorerV4.tsx`, `web/src/cockpit-bridge-v4.js`, `web/src/experience-v4.css`.
- **Objetivo:** Reemplazar la grilla plana de 8 tarjetas por un explorador guiado con contexto operativo de cada subsistema (GPS, ADAS, LiDAR, 5G, HVAC, CAN).
- **Cómo funciona:** Tarjetas dinámicas con descripciones técnicas, estado de conexión en tiempo real y botón de acceso directo a la herramienta de diagnóstico de cada sensor.
- **Decisiones técnicas:** Inyección de puente `cockpit-bridge-v4.js` para comunicar clics del explorador con el iframe de cabina.
- **Qué NO se modificó:** Controladores físicos ni controladores de bus CAN emulados.
- **Comandos de prueba + resultado:** Recorrido completo de los 8 subsistemas con activación visual verificada.
- **Problemas encontrados y solución:** Ambigüedad en qué subsistema probar primero resuelta destacando el radar LiDAR y navegación GPS como recomendados.
- **Explicación breve para la exposición:** Facilita la demostración docente mostrando claramente la función y el estado de cada sensor automotriz.

---

### Etapa 5: Adaptabilidad de Pantalla, Modo Claro y Soporte RBAC V5
- **Fecha:** 2026-11-12
- **Autor/es:** Integrante 3 (Seguridad) & Integrante 4 (Integración)
- **Commit / PR:** `fix/theme-rbac-v5`
- **Archivos tocados:** `web/src/components/CockpitWorkspaceV5.tsx`, `web/src/cockpit-theme-v5.css`, `web/src/experience-v5.css`.
- **Objetivo:** Corregir el ancho del iframe colapsado a 450px y sincronizar el rol activo (Mecánico/Conductor/Pasajero) y el tema entre React y el Cockpit.
- **Cómo funciona:** Asignación de `width: 100%` con flex-grow en el contenedor de cabina y despacho de mensajes `postMessage` (`AUTOOS_SET_ROLE`, `AUTOOS_SET_THEME`).
- **Decisiones técnicas:** Unificar el selector de rol en la barra superior de AutoOS como única fuente de verdad RBAC para todo el sistema.
- **Qué NO se modificó:** Políticas de Row Level Security (RLS) en base de datos.
- **Comandos de prueba + resultado:** Cambio a rol «Pasajero» oculta controles críticos y restringe acciones; modo Claro aplica fondo marfil legible.
- **Problemas encontrados y solución:** Retrasos de sincronización inicial resueltos enviando mensajes a los 60ms, 200ms y 500ms tras la carga del iframe.
- **Explicación breve para la exposición:** Demuestra la separación de privilegios (Autenticación != Autorización) y diseño responsivo en pantalla completa.

---

### Etapa 6: Corrección Estructural del Cockpit V6
- **Fecha:** 2026-11-13
- **Autor/es:** Integrante 4 (Interfaz e Integración)
- **Commit / PR:** `refactor/cockpit-structure-v6`
- **Archivos tocados:** `web/src/components/CockpitToolSceneV6.tsx`, `web/src/cockpit-v6-embedded.js`, `web/src/cockpit-v6-embedded.css`.
- **Objetivo:** Eliminar barras de navegación redundantes y barras de desplazamiento anidadas dentro de la vista de Conducción.
- **Cómo funciona:** Oculta encabezados internos duplicados del iframe mediante CSS scoped y redirige directamente a la escena de herramienta solicitada.
- **Decisiones técnicas:** Encapsular el iframe dentro de un contenedor controlado que intercepta scrollbars internas indeseadas.
- **Qué NO se modificó:** Datos de telemetría ni lógica de sensores.
- **Comandos de prueba + resultado:** Inspección visual en resolución 1920x1080 y 1366x768 sin scrollbars duplicadas.
- **Problemas encontrados y solución:** Enlaces internos que recargaban el frame corregidos comunicando comandos por eventos postMessage.
- **Explicación breve para la exposición:** Garantiza una experiencia visual unificada y limpia, sin la apariencia de «una página metida dentro de otra».

---

### Etapa 7: Calibración de Contraste y Accesibilidad V7
- **Fecha:** 2026-11-13
- **Autor/es:** Integrante 4 (Interfaz)
- **Commit / PR:** `fix/contrast-inputs-v7`
- **Archivos tocados:** `web/src/experience-v7-contrast.css`, `web/src/cockpit-v7-contrast.css`.
- **Objetivo:** Subsanar problemas de legibilidad donde campos de texto en Spotify y modales aparecían blancos sobre fondo blanco en modo oscuro o claro.
- **Cómo funciona:** Reglas CSS con selectores de alta especificidad para inputs (`background: rgba(15, 23, 42, 0.85); color: #f8fafc; border: 1px solid #334155`).
- **Decisiones técnicas:** Asegurar un ratio de contraste superior a 4.5:1 acorde con las directrices de accesibilidad automotriz.
- **Qué NO se modificó:** Controladores de audio ni lógica de playlist.
- **Comandos de prueba + resultado:** Validación visual en tema claro y oscuro con herramientas de contraste del navegador.
- **Problemas encontrados y solución:** Estilos heredados de Tailwind sobreescritos con directivas CSS scoped al contenedor de AutoOS.
- **Explicación breve para la exposición:** Cumple con criterios ergonómicos de visibilidad en condiciones de alta y baja luminosidad de cabina.

---

### Etapa 8: Estabilización de Entrega y Producción V8
- **Fecha:** 2026-11-13
- **Autor/es:** Integrante 4 (Integración) & Integrante 1 (Procesos)
- **Commit / PR:** `release/v8-production`
- **Archivos tocados:** `web/src/production-v8.css`, `web/src/cockpit-production-v8.js`, `docs/blue-shift/ENTREGA_FINAL_V8.md`.
- **Objetivo:** Consolidar todos los parches visuales y puentes de eventos en un bundle único de producción sin archivos redundantes.
- **Cómo funciona:** Carga secuencial optimizada de scripts de soporte y estilos definitivos para el entorno de sustentación.
- **Decisiones técnicas:** Congelar dependencias en `package.json` y verificar compilación limpia con Vite y TypeScript.
- **Qué NO se modificó:** Núcleo de simulación de algoritmos FCFS/RR/Prioridad.
- **Comandos de prueba + resultado:** `npm run build` genera `dist/` en 3.4 segundos sin advertencias críticas.
- **Problemas encontrados y solución:** Fugas de listeners de eventos solucionadas removiendo manejadores en el desmontaje de componentes (`useEffect cleanup`).
- **Explicación breve para la exposición:** Versión de alta estabilidad lista para la sustentación presencial y remota.

---

### Etapa 9: Simulación Integrada de Recursos del Sistema Operativo V9
- **Fecha:** 2026-11-14
- **Autor/es:** Integrante 1 (CPU/Procesos) & Integrante 2 (Memoria)
- **Commit / PR:** `feat/os-resource-monitor-v9`
- **Archivos tocados:** `web/src/components/OSResourceMonitor.tsx`, `web/src/simulation/resources.ts`, `web/src/os-resource-monitor.css`.
- **Objetivo:** Unificar el consumo de recursos de modo que un escenario de falla en Simulación afecte de forma inmediata los indicadores de CPU, RAM y bus CAN en todo el sistema.
- **Cómo funciona:** Gestor centralizado en `resources.ts` que computa la carga total solicitada por procesos en cola (`LISTO`), activos (`EJECUTANDO`) y memoria residente vs suspendida.
- **Decisiones técnicas:** La telemetría no lee los recursos de la máquina física del estudiante, sino que modela fielmente las restricciones de una ECU automotriz de 2048 MB / 4096 MB.
- **Qué NO se modificó:** Base de datos Supabase ni autenticación.
- **Comandos de prueba + resultado:** Ejecución de `node tests/run.cjs` pasando las 12 pruebas de cálculo de carga y memoria.
- **Problemas encontrados y solución:** Desconexión entre paneles de métricas resuelta enlazando un mismo estado compartido en `App.tsx`.
- **Explicación breve para la exposición:** Demuestra cómo las fallas vehiculares impactan directamente en la disponibilidad de memoria y ciclos de procesador del sistema operativo.

---

### Etapa 10: Puente de Kernel Python <-> React
- **Fecha:** 2026-11-15
- **Autor/es:** Integrante 1 (CPU) & Integrante 3 (Seguridad)
- **Commit / PR:** `feat/kernel-bridge-v10`
- **Archivos tocados:** `Auto/kernel_bridge.py`, `Auto/bridge_react_kernel.py`, `web/src/kernelBridge.ts`, `web/src/kernel-bridge-v10.css`.
- **Objetivo:** Conectar el motor formal del kernel en Python (`AutoOS_1/src/core/kernel.py`) con la interfaz visual interactiva en React.
- **Cómo funciona:** `kernel_bridge.py` serializa el estado del despachador, eventos de context switch y estados de la PCB a formato JSON para consumo en el frontend.
- **Decisiones técnicas:** Fallback automático a motor de simulación en navegador si el kernel de Python no se encuentra en ejecución activa.
- **Qué NO se modificó:** Algoritmos de planificación preexistentes en `schedulerEngine.ts`.
- **Comandos de prueba + resultado:** `python AutoOS_1/tests/test_react_kernel_bridge.py` -> 100% exitoso.
- **Problemas encontrados y solución:** Formatos de fecha y time ticks dispares homologados a enteros determinísticos en segundos.
- **Explicación breve para la exposición:** Evidencia la correlación técnica entre la implementación backend del kernel en Python y la visualización gráfica en React.

---

### Etapa 11: Arquitectura y Sustentación V11
- **Fecha:** 2026-11-15
- **Autor/es:** Equipo AutoOS (Integrantes 1, 2, 3 y 4)
- **Commit / PR:** `feat/v11-architecture-reports`
- **Archivos tocados:** `web/src/components/AutoOSModulesV11.tsx`, `Auto/v11_cloud_bridge.py`, `docs/blue-shift/V11_ARQUITECTURA_Y_SUSTENTACION.md`.
- **Objetivo:** Consolidar el módulo V11 de recarga y preparación de escenarios para la defensa ante el docente.
- **Cómo funciona:** Panel que permite inyectar escenarios preconfigurados (Sobrecarga de CPU, Pérdida de Enlace 5G, Fallo de Radar) y contrastar la respuesta de seguridad ASIL-D.
- **Decisiones técnicas:** Incorporar panel explicativo que recuerda que AutoOS es un simulador pedagógico de sistema operativo vehicular, no software de producción automotriz real.
- **Qué NO se modificó:** Estructura de tablas en Supabase.
- **Comandos de prueba + resultado:** `python AutoOS_1/tests/test_v11_cloud_report.py` -> Todos los tests superados.
- **Problemas encontrados y solución:** Tiempos de respuesta inconsistentes en la nube mitigados con reintentos exponenciales locales.
- **Explicación breve para la exposición:** Guía rápida para demostrar en vivo el comportamiento de tolerancia a fallos ante el jurado evaluador.

---

### Etapa 12: Cabina, Conectividad Bluetooth y Rendimiento
- **Fecha:** 2026-11-16
- **Autor/es:** Integrante 4 (Interfaz) & Integrante 3 (Dispositivos)
- **Commit / PR:** `feat/cabin-bluetooth-v12`
- **Archivos tocados:** `tools/test_bluetooth_v12.cjs`, `tools/validar_v12.ps1`, `docs/blue-shift/ETAPA_12_CABINA_BLUETOOTH_RENDIMIENTO.md`.
- **Objetivo:** Optimizar la experiencia de infoentretenimiento en cabina, asegurando interacción responsiva del botón BLE y control de latencia en el reproductor.
- **Cómo funciona:** Emulación del handshake Bluetooth Low Energy (BLE) y actualización del estado del DSP de audio en la matriz de hardware.
- **Decisiones técnicas:** Mantener la simulación de hardware desacoplada de la reproducción real de Spotify a través de un bus de eventos personalizado.
- **Qué NO se modificó:** Algoritmos de planificación ni bases de datos.
- **Comandos de prueba + resultado:** `node tools/test_bluetooth_v12.cjs` -> Comprobación de eventos BLE exitosa.
- **Problemas encontrados y solución:** Retardo en respuesta visual corregido mediante actualización inmediata optimista en la interfaz.
- **Explicación breve para la exposición:** Simula la conexión de dispositivos móviles de los pasajeros y su impacto en los recursos de la cabina.

---

### Etapa 13: Confirmación Robusta de Eventos en Supabase Cloud
- **Fecha:** 2026-11-18
- **Autor/es:** Integrante 3 (Seguridad y Cloud) & Integrante 4 (Integración)
- **Commit / PR:** `fix/supabase-events-ack-v13`
- **Archivos tocados:** `docs/ETAPA_13_CONFIRMACION_EVENTOS_SUPABASE.md`, `Auto/config.py`, `Auto/bridge_component/index.html`.
- **Objetivo:** Eliminar falsos timeouts y estados ambiguos al enviar eventos desde React a través de Streamlit hacia la tabla `public.eventos` de Supabase.
- **Cómo funciona:** Cada evento enviado genera un `requestId` único. La interfaz solo marca el evento como **CONFIRMADO** cuando recibe un acuse `cloud.ack === requestId` verificado desde Python.
- **Decisiones técnicas:** No asumir éxito ni fallo por tiempo transcurrido; clasificar explícitamente en: `CONFIRMADO`, `OPERACIÓN RECHAZADA` o `SIN CONFIRMACIÓN`.
- **Qué NO se modificó:** Políticas de Row Level Security (RLS) en PostgreSQL ni claves públicas de API.
- **Comandos de prueba + resultado:** Inserción manual de evento verificada con éxito directamente en el dashboard de Supabase.
- **Problemas encontrados y solución:** Bloqueos por timeout falso resueltos con canal asíncrono y acuse de recibo explícito.
- **Explicación breve para la exposición:** Demuestra integridad y trazabilidad en la auditoría de eventos en la nube sin inconsistencias de red.

---

### Etapa 14: Caja Negra Vehicular Sincronizada con Supabase Cloud
- **Fecha:** 2026-11-19
- **Autor/es:** Integrante 3 (Seguridad) & Integrante 1 (CPU/Procesos)
- **Commit / PR:** `feat/blackbox-cloud-sync-v14`
- **Archivos tocados:** `web/src/cloud/blackboxSync.ts`, `Auto/blackbox_cloud_sync.py`, `docs/ETAPA_14_CAJA_NEGRA_SUPABASE.md`, `AutoOS_1/tests/test_v14_blackbox_cloud_sync.py`.
- **Objetivo:** Implementar la sincronización continua del historial de Caja Negra (eventos `DISPATCH`, `COMPLETION`, `CRITICAL_INJECT`, `GPS`) hacia Supabase sin saturar la cuota de la base de datos.
- **Cómo funciona:** Cola en el navegador que despacha lotes de hasta 6 eventos cada 3.5 segundos. En Python, `blackbox_cloud_sync.py` desduplica mediante `detalles.autoos_id` antes de realizar el `INSERT`.
- **Decisiones técnicas:** Filtrado de eventos rutinarios (un registro de ruta GPS cada 5 ticks) manteniendo el 100% de las alertas y fallas críticas.
- **Qué NO se modificó:** Estructura de la tabla `public.eventos`.
- **Comandos de prueba + resultado:** `python AutoOS_1/tests/test_v14_blackbox_cloud_sync.py` -> 24 eventos confirmados en Supabase (0 pendientes).
- **Problemas encontrados y solución:** Riesgo de duplicidad por reintentos de red evitado verificando la clave `detalles.autoos_id` en la base de datos.
- **Explicación breve para la exposición:** Simula la caja negra de telemetría forense requerida por normativas de seguridad vehicular autónoma.

---

### Etapa 15: Telemetría Reactiva Unificada de RAM/CPU y Calibración OBD-II
- **Fecha:** 2026-11-20
- **Autor/es:** Equipo AutoOS (Integración Integral)
- **Commit / PR:** `fix/reactive-telemetry-obd2`
- **Archivos tocados:** `Auto/autoos_interactive.html`, `Auto/autoos_unified.html`, `web/public/autoos_interactive.html`, `tools/update_memory_telemetry.py`.
- **Objetivo:** Hacer que los tacómetros circulares de memoria RAM y CPU en el Cockpit y en el planificador RTOS reflejen dinámicamente y en tiempo real cualquier cambio en los procesos, reproducción musical o inyección de fallas.
- **Cómo funciona:** Efecto reactivo centralizado en el kernel que calcula el uso de RAM sobre una base ASIL-D de 4096 MB:
  - Procesos activos (`EJECUTANDO`): memoria base + working-set dinámico (+36 MB a +54 MB).
  - Procesos pausados (`ESPERA`): liberación del 75% a memoria de intercambio (swap).
  - Procesos finalizados (`SIGKILL`): liberación del 100% de la carga de memoria y CPU.
  - Escenarios de ataque DoS CAN o fallas de hardware: aumento de buffers de red y reservas de diagnóstico.
  - Botón de calibración OBD-II habilitado para restablecer sensores defectuosos a estado 100% nominal.
- **Decisiones técnicas:** Mantener sincronizada la cadena base64 en `autoos_unified.html` para que tanto Streamlit Cloud como el frontend local muestren la misma reactividad.
- **Qué NO se modificó:** Parámetros de conexión a Supabase ni estructura de tablas.
- **Comandos de prueba + resultado:** Validación sintáctica `node --check` en ambos scripts y prueba interactiva de pausas y calibración.
- **Problemas encontrados y solución:** Valores fijos en `syncMediaState` sustituidos por un modelo reactivo dependiente de `[f, ie, u]`.
- **Explicación breve para la exposición:** Demuestra de forma visual e inmediata los conceptos de asignación de memoria, cambio de contexto y liberación de recursos en un sistema operativo en tiempo real.
