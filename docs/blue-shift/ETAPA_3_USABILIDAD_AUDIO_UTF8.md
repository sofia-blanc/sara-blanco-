# AutoOS / Blue Shift — Etapa 3: claridad, sonido y codificación

## Objetivo de la etapa

La presentación ya permite entrar a Conducción, Simulación y Planificador, pero
las pantallas interiores carecían de contexto. Además, la opción «Sonido OFF»
solo detenía los efectos del menú y no Spotify; varios literales de `App.tsx`
mostraban caracteres como `MecÃ¡nico`.

Esta etapa es una **mejora funcional y de accesibilidad**, no una sustitución del
kernel, de Supabase ni una recreación final del arte de Persona 3 Reload.

## Archivos y responsabilidades

| Archivo | Responsabilidad |
|---|---|
| `web/src/components/ModuleOrientationV3.tsx` | Explica el objetivo de cada módulo y sus tres pasos de uso. |
| `web/src/module-polish-v3.css` | Jerarquía editorial, contraste, tipografía y diagnóstico avanzado plegable. |
| `web/src/App.tsx` | Guarda el estado global `audioMuted`; enlaza controles y guías. |
| `web/src/components/CinematicMenu.tsx` | Usa el estado de audio global en lugar de un estado privado. |
| `web/src/components/ModuleScene.tsx` | Muestra el botón Sonido ON/OFF en todas las pantallas. |
| `web/public/autoos_interactive.html` | Recibe mensajes para detener/reiniciar la carga del embed de Spotify. |
| `Auto/autoos_interactive.html` | Copia del Cockpit para Streamlit, con el mismo puente de audio. |

## Cómo funciona el mute de Spotify

**Problema:** el menú React está en un documento distinto del Cockpit. Dentro
del Cockpit hay otro iframe servido por Spotify, de otro dominio. El código
JavaScript de AutoOS no puede entrar a cambiar su volumen directamente.

**Solución comprobable:**

1. El botón Sonido ON/OFF cambia `audioMuted` en `App.tsx`.
2. React envía `postMessage({type:'AUTOOS_SET_AUDIO_MUTED', muted})` a su iframe de Cockpit.
3. El código del Cockpit escucha **solo** los mensajes de su padre React.
4. Al silenciar, sustituye temporalmente la dirección del iframe de Spotify
   por `about:blank` (esto detiene la reproducción embebida).
5. Al reactivar, restaura la URL guardada. **Debe pulsarse Play otra vez**;
   AutoOS no fuerza reproducción automática.
6. Los efectos del menú se desactivan con el mismo estado.

Esto **no** detiene Spotify abierto en otra pestaña o aplicación externa.
No se altera la sincronización de Spotify de los otros componentes.

## Planificador: por qué cambió el orden

El objetivo central del módulo es estudiar **planificación de CPU y tiempo
real**. La antigua primera pantalla mostraba 11 tarjetas de hardware antes del
diagrama de Gantt, dificultando encontrar el experimento principal.

Ahora se ve primero:
1. Elección del algoritmo y controles de ejecución.
2. Métricas y Gantt (en qué orden atiende la CPU).
3. CPU y cola READY (qué está ejecutándose y qué espera).

La matriz de hardware sigue existiendo en «DIAGNÓSTICO AVANZADO», plegada por
defecto. **No se eliminó ningún botón de calibración o inyección de fallas.**

## Corrección de las tildes

Solo se repararon literales conocidos de `web/src/App.tsx` y se guardó como
UTF-8. El generador HTML integra el JavaScript nuevo al hacer el build. No se
usó una recodificación global que pudiera dañar nombres o identificadores.

## Prueba manual para la presentación

- [ ] Entrar a Conducción y abrir «¿Cómo se utiliza?».
- [ ] Abrir Multimedia, reproducir Spotify, cambiar pestaña y comprobar que continúa.
- [ ] Pulsar **SONIDO OFF**: debe detenerse el audio embebido.
- [ ] Pulsar **SONIDO ON**: recargar embed y pulsar Play para continuar.
- [ ] Entrar a Simulación y explicar selección, inicio y respuesta del SO.
- [ ] Entrar al Planificador como mecánico, elegir RR/quantum 2, pulsar Paso tres veces y observar Gantt/CPU.
- [ ] Abrir «DIAGNÓSTICO AVANZADO» y confirmar que los 11 dispositivos siguen allí.
- [ ] Cambiar a conductor: el Planificador debe seguir protegido por RBAC.
- [ ] Revisar visualmente «Mecánico», «Planificación», «Velocímetro» y «Cámaras».
- [ ] Revisar que las dos vistas de Streamlit siguen funcionando.

## Publicación

Un cambio en los archivos TSX no aparece por sí solo en Streamlit:

```powershell
cd web
npm run lint
npm run test:sim
npm run build
cd ..
python .\tools\build_streamlit_bundle.py
```

En GitHub, documentar en el PR: qué problema se resolvió, archivos cambiados,
resultado de pruebas y captura antes/después. No publicar aún sin probar la
interfaz embebida en Streamlit.
