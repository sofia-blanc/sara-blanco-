# Menú cinematográfico de AutoOS — Diseño, funcionamiento y presentación

## Objetivo
Reemplazar la entrada visual estilo *dashboard* por un menú de pantalla completa inspirado en la composición dinámica de los videojuegos, sin reemplazar los motores operativos existentes. **No afirma que el motor React sea el mismo kernel Python.**

## Arquitectura (flujo de ejecución)

```text
Streamlit Cloud -> app.py -> Auto/app.py
                            |
                            +-- Vista cinematográfica (predeterminada)
                            |    -> Auto/autoos_unified.html (compilado de Vite)
                            |       -> web/src/main.tsx
                            |          -> web/src/App.tsx
                            |             -> CinematicMenu.tsx
                            |                 | Conducción -> Cockpit HTML
                            |                 | Simulación -> SimulationCenter
                            |                 ` Planificador -> Scheduler y Hardware
                            |
                            `-- Panel RTOS completo (botón visible)
                                 -> Dashboard Python de nueve módulos
                                 -> Kernel, VFS, RAM, Supabase y RBAC Python
```

**Límite técnico importante:** React y Python gestionan estados distintos. Cambiar de rol dentro de la pantalla React no cambia automáticamente el rol Python del Panel RTOS; este utiliza su propio control de acceso. No presentar los estados como si estuvieran sincronizados entre ambos motores.

## Archivos nuevos

- `web/src/components/CinematicMenu.tsx`: estructura, selección por teclado y ratón, permisos de la UI, sonidos originales sintetizados.
- `web/src/cinematic-menu.css`: composición del menú, transiciones, movimiento acuático y diseño adaptable.
- `tools/apply_cinematic_menu_v1.py`: parche reproducible, se niega a editar cuando el código base difiere de lo esperado, ejecutable varias veces.
- `tools/build_streamlit_bundle.py`: integra CSS, JavaScript y Cockpit en un HTML autocontenido a partir de `web/dist`.

## Archivos existentes modificados (por el instalador)

- `web/src/App.tsx`: `showCinematicMenu` decide qué escena se muestra. `onNavigate` mapea las opciones a las pestañas funcionales existentes. El botón MENÚ vuelve a la portada y pausa la reproducción automática de ticks, sin reiniciar la simulación.
- `web/src/main.tsx`: importa la nueva hoja de estilos.
- `Auto/app.py`: muestra primero el HTML cinematográfico y ofrece un botón para entrar al dashboard Streamlit original. El código original de las nueve pestañas no se elimina.

## Animaciones: cómo funcionan

| Efecto | Técnica | Propósito |
|---|---|---|
| Entrada inicial | `@keyframes autoos-cine-appear` | Aparición de escena |
| Filas inclinadas | `skewX(-12deg)` + `transform` | Navegación dinámica |
| Selección resaltada | `background`, `box-shadow` rosa | Identificar opción activa |
| Olas decorativas | `border-radius`, `transform`, `filter` | Movimiento ambiental |
| Franjas diagonales | `repeating-linear-gradient` | Sensación de velocidad |
| Salida a un módulo | `autoos-cine-exit`, temporizador 420 ms | Transición previa al cambio de estado |
| Cambio de descripción | React `key={current.key}` | Reiniciar entrada del texto de la opción |

Las animaciones se desactivan mediante `prefers-reduced-motion`. El movimiento no modifica los cálculos de simulación.

## Sonido

Los sonidos de mover, confirmar y rechazar se sintetizan mediante **Web Audio API** (`OscillatorNode` y `GainNode`). No se incorporan archivos musicales ni recursos comerciales al repositorio. Funcionan solo después de una interacción permitida por el navegador y pueden silenciarse con el botón SONIDO.

## Accesibilidad y permisos

- Flechas ↑/↓: cambian la opción seleccionada.
- Enter o espacio: confirman.
- Teclas 1–3: seleccionan opciones rápidamente (no las abren).
- Ratón: `onMouseEnter` cambia la selección y `onClick` confirma.
- Rol Conductor/Pasajero: no puede abrir el Planificador. El botón sigue visible para comunicar la restricción.
- Menú React: la restricción es de interfaz, **no reemplaza la autorización del kernel Python**.

## Publicación real

1. `python tools/apply_cinematic_menu_v1.py`
2. `cd web` y `npm ci`
3. `npm run lint` y `npm run test:sim`
4. `npm run build`
5. `cd ..` y `python tools/build_streamlit_bundle.py`
6. `python -m streamlit run app.py`
7. Verificar Cockpit, Simulación y Planificador dentro de Streamlit.
8. Ejecutar las pruebas Python (`unittest`) y revisar `git diff`.
9. Publicar en rama de funcionalidad con PR a `main`, que es el origen del despliegue Streamlit.

**Advertencia:** modificar `web/src/App.tsx` sin ejecutar los pasos 4–5 NO actualiza la página de Streamlit Cloud: esta carga `Auto/autoos_unified.html`.

## Guion de exposición para el equipo

- **Diseño:** "El menú está dividido en un componente React y un CSS animado; el diseño no interviene en los algoritmos del sistema".
- **Navegación:** "`onNavigate` comunica el módulo elegido a `App.tsx`. No creamos simuladores nuevos: reutilizamos los existentes".
- **Rol:** "El menú muestra permisos básicos, mientras el kernel Python mantiene su propio control de acceso".
- **Despliegue:** "Vite empaqueta React en HTML autocontenido que Streamlit inserta en un iframe. Conservamos el panel Python completo como vista técnica".
- **Pruebas:** "Comprobamos frontend con `lint`, `test:sim`, `build` y el núcleo con 130 pruebas Python. Nunca debemos asegurar que pasan si no hemos ejecutado esos comandos en la versión actual".
