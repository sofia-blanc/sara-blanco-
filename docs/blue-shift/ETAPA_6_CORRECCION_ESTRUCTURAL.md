# AutoOS · Etapa 6 — Corrección estructural del Cockpit

## Problema observado (capturas del equipo)

1. La V5 daba la impresión de que Conducción no había cambiado: el botón **Abrir vista técnica** llevaba al `Panel Principal` del Cockpit antiguo, con 8 tarjetas repetidas.
2. Al entrar a GPS o Seguridad seguían apareciendo dos barras de pestañas: la navegación de AutoOS y la del Cockpit incrustado.
3. En modo claro había una portada casi blanca con títulos blancos; los estilos se resolvían por diferentes reglas de CSS.

## Solución V6

- El botón del resumen ya no abre la portada técnica antigua: abre **GPS real** dentro de un lienzo guiado.
- `CockpitToolSceneV6.tsx` dibuja el contexto, una lista de herramientas, instrucciones de uso y un contenedor ancho para el iframe original.
- `App.tsx` sigue siendo dueño de `cockpitFeature`, el rol, la batería y la conexión del iframe. El cambio de herramienta reenvía el mensaje `AUTOOS_V4_OPEN_FEATURE` **sin desmontar el iframe**, conservando su estado.
- `cockpit-v6-embedded.js` oculta solamente la barra de pestañas duplicada **cuando recibe la señal de navegación de la aplicación principal**. La vista HTML independiente se conserva.
- `experience-v6.css` consume el atributo `data-autoos-theme` que envía React. La cabecera mantiene fondo azul noche de alto contraste en ambos temas; la superficie del modo claro es luminosa.

## Archivos modificados

- `web/src/App.tsx`: envuelve el iframe funcional, sincroniza cambios de herramientas y declara el tema de manera explícita.
- `web/src/components/ModuleScene.tsx`: añade `data-autoos-theme` para aplicar la paleta elegida.
- `web/src/components/CockpitWorkspaceV5.tsx`: botón del resumen abre una herramienta real en vez del dashboard viejo.
- `web/src/main.tsx`: importa `experience-v6.css` al final, sobreponiéndose a estilos históricos.
- `web/public/autoos_interactive.html` y `Auto/autoos_interactive.html`: puente mínimo para esconder navegación duplicada.

## Archivos nuevos

- `web/src/components/CockpitToolSceneV6.tsx`: escena de trabajo para la herramienta técnica.
- `web/src/experience-v6.css`: reglas responsivas, escenas y modo claro/oscuro.
- `web/src/cockpit-v6-embedded.js` y `.css`: presentación interna del Cockpit original.

## Seguridad y conservación de funciones

No se alteran los roles, las reglas RBAC, el kernel, el planificador o Supabase. La barra del iframe antiguo se oculta a nivel visual; sus botones siguen montados en React y el puente V4 puede usarlos. Las operaciones reales y las validaciones siguen siendo las originales.

## Comprobar antes de presentar

1. Entrar a Conducción: ver explorador de herramientas en lugar de ocho tarjetas.
2. Elegir GPS y pulsar abrir: ver título grande, navegación izquierda y módulo GPS funcional debajo.
3. Cambiar de GPS a Cámara desde la barra nueva: se abre Cámara **sin recargar toda la página**.
4. Volver al resumen; comprobar que la antigua cuadrícula no aparece como portada.
5. Alternar claro/oscuro dos veces: la cabecera no pierde contraste, las opciones son legibles.
6. En Seguridad comprobar que los perfiles y la auditoría respetan el rol.
7. Ejecutar `npm run lint`, `npm run test:sim`, `npm run build`, el empaquetador y las pruebas Python.

## Cómo explicarlo al profesor

> Separamos la navegación de la lógica del Cockpit. React mantiene el estado del módulo activo y el perfil. La escena contextual muestra instrucciones comprensibles y envía mensajes al Cockpit incrustado; este conserva sus sensores y validaciones. El atributo de tema se establece desde React para que claro y oscuro no dependan de estilos heredados inconsistentes.

## Limitaciones honestas

La V6 elimina la entrada repetitiva y la navegación duplicada, y refuerza el contraste del modo claro. Las **herramientas técnicas dentro del iframe** conservan parte de su aspecto antiguo. Reemplazarlas por pantallas React totalmente nuevas exigiría migrar su lógica y sus estados funcionales uno a uno; no debe hacerse simplemente ocultando el iframe. La V6 no es una copia terminada de la interfaz de Persona 3 Reload.
