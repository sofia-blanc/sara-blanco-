# AutoOS — V5: interacción real, modo claro y Cockpit ancho

## Problema observado

El iframe del Cockpit se reducía a aproximadamente 450 px aunque existiera
espacio horizontal. En CSS, `.autoos-v4-workspace` tenía margen horizontal `auto`
y `max-width`, pero carecía de un `width: 100%` explícito, permitiendo que el
contenedor flex se ajustase al ancho intrínseco del iframe.

## Solución

- `experience-v5.css` obliga al workspace y al iframe a ocupar el 100 % del
  ancho disponible y conserva la medición dinámica de altura V4.
- El modo claro combina contenido de alto contraste con una portada azul noche.
  Evita titulares blancos sobre fondo blanco o celeste claro.
- `CockpitOverviewV5` usa el estado `battery` y `devices` ya presente en
  `App.tsx`; no inventa telemetría.
- `CockpitSecurityV5` convierte las tarjetas de perfiles en botones con
  `aria-pressed` y utiliza `setUserRole`, existente en `App.tsx`.
- Los permisos que se muestran son una guía de demostración. Los controles
  originales siguen validando los permisos; esta pantalla no sustituye RBAC.
- La vista de eventos opera sobre `simState.events` de React. No es la
  auditoría persistente de la base de datos. El acceso a la auditoría original
  permanece disponible mediante el iframe del Cockpit.
- Los archivos `autoos_interactive.html` reciben CSS V5 en su cabecera.
  El tema se sigue transmitiendo desde React mediante el puente anterior.

## Flujo de usuario

1. Menú cinematográfico → Conducción → Explorador.
2. «Ver resumen de conducción» → vista React nativa, con indicadores reales.
3. «Abrir GPS» → iframe Cockpit heredado, pero con ancho completo.
4. «Seguridad» → pantalla V5 con cambio real del perfil de demostración.
5. «Ver auditoría del Cockpit» → vista original con su histórico y filtros.

## Dónde está el código

- `web/src/components/CockpitWorkspaceV5.tsx`: vistas React y comentarios.
- `web/src/experience-v5.css`: tema oscuro y claro, contraste y layout.
- `web/src/cockpit-theme-v5.css`: tema del HTML heredado (otro documento).
- `web/src/App.tsx`: conexión con estados, callbacks y iframe original.
- `tools/apply_experience_v5.py`: instalador validado e idempotente.
- `tools/build_streamlit_bundle.py`: empaqueta la versión React para Streamlit.

## Preguntas para la exposición

**¿Por qué no reescribir el motor del Cockpit?** La lógica y controles técnicos
ya funcionan. V5 añade pantallas de presentación y delega en el Cockpit existente.

**¿Cómo se conservan los roles?** El estado `userRole` está en `App.tsx`; los
botones V5 solo cambian el rol de demostración y los módulos originales aplican
sus restricciones. No es un sistema de autenticación nuevo.

**¿Cómo llega a Streamlit Cloud?** Se compila React con Vite, se convierte con
`build_streamlit_bundle.py` a `Auto/autoos_unified.html` y el `Auto/app.py`
de Streamlit usa ese HTML. No basta con modificar solo `App.tsx`.

**¿Por qué los dos temas usan una cabecera oscura?** Es una decisión visual de
contraste: la portada sigue siendo reconocible y se evita perder el título
blanco sobre fondo claro. Los contenidos sí cambian con el tema.
