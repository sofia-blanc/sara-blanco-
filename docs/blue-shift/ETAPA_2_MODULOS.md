# AutoOS Blue Shift — Etapa 2: escenas cinematográficas

## Por qué este cambio

Las capturas de Conducción, Simulación y Planificador mostraban 3 problemas:

1. La navegación interna parecía un dashboard administrativo y ocupaba muy poco espacio.
2. Los módulos usaban diferentes contenedores de ancho fijo y textos diminutos.
3. La interfaz React se incrustaba dentro de un iframe Streamlit de altura fija; el Cockpit, a su vez, contenía otro iframe.
4. Al cambiar al rol Conductor/Pasajero, React podía mantener el Cockpit visible debajo de Simulación, ya que su condición dependía del rol en vez del módulo activo.

## Arquitectura

```text
Streamlit: app.py → Auto/app.py
   │
   └── components.html(Auto/autoos_unified.html)
          │
          ├── React: web/src/App.tsx (estado, permisos, controladores)
          │      ├── CinematicMenu.tsx (menú principal)
          │      ├── ModuleScene.tsx (cabecera y navegación de módulos)
          │      ├── SimulationCenter.tsx (simulación)
          │      └── iframe cockpit (HTML separado)
          │
          └── iframeResize.ts ─postMessage→ Streamlit (altura solicitada)
```

## Detalles para exposición

- `ModuleScene.tsx`: decide QUÉ DIBUJAR, no QUÉ PUEDE HACER el kernel. Recibe `active`, `role`, `batteryLevel` y callbacks.
- `App.tsx`: conserva los `useState` existentes y el control RBAC; no se regeneran procesos ni dispositivos al navegar.
- `module-scenes-v2.css`: fuentes, transiciones, menús diagonales y ajuste de ancho. Respeta `prefers-reduced-motion`.
- `iframeResize.ts`: mide `#root`, no el documento. Eso permite reducir la altura al regresar al menú y evita barras de desplazamiento redundantes cuando Streamlit acepta el mensaje.
- `cockpit-inner-v2.css`: el cockpit carga un documento HTML propio, de modo que se inyecta su CSS dentro del `<head>` de ambas copias. Se evita alterar su JavaScript.
- `tools/apply_module_scenes_v2.py`: comprueba que existan las anclas. Aplica todos los cambios solo cuando son compatibles; si falta una, no escribe nada.
- `tools/build_streamlit_bundle.py`: vuelve a integrar el CSS y JS de producción con el cockpit para Streamlit.

## Pruebas recomendadas

1. `cd web; npm ci; npm run lint; npm run test:sim; npm run build; cd ..`
2. `python tools/build_streamlit_bundle.py`
3. `python -m py_compile Auto/app.py`
4. `python -m streamlit run app.py`
5. Entrar a los 3 módulos, cambiar rol y tema, volver al menú y comprobar que la simulación mantiene su estado.
6. Probar ventana de 1920×1080 y ventana más estrecha; comprobar scroll vertical del Cockpit.

## Limitaciones conscientes

- Es una **V2 visual**; los controles y la estructura interna del Cockpit HTML heredado siguen siendo su implementación original.
- El autoredimensionado del iframe depende del protocolo de componentes soportado por la versión de Streamlit; se mantiene `scrolling=True` como alternativa.
- Los botones de Simulación/Planificador siguen siendo funcionales, pero la siguiente etapa debe rediseñar sus tarjetas internas con jerarquía gráfica consistente.
- Las fuentes usadas son alternativas web. Fuentes y sonidos externos requieren permisos para distribuirlos en GitHub público.
