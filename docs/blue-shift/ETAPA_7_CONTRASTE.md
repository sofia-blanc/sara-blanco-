# Etapa 7 — Contraste visual en los dos temas

## Problemas reportados

1. Los dos campos de texto del reproductor de Spotify aparecían blancos con texto blanco, especialmente en modo oscuro.
2. Al activar modo claro, el título cinematográfico blanco podía quedar sobre una cabecera demasiado luminosa.

## Arquitectura del arreglo

- `web/src/experience-v7-contrast.css`: trabaja sobre `ModuleScene.tsx` (React). Usa el atributo `data-autoos-theme`, alimentado desde el estado de `App.tsx`, para dejar el encabezado azul profundo en modo claro. Solo se modifica la presentación.
- `web/src/cockpit-v7-contrast.css`: estilos del Cockpit HTML independiente. Se inyecta **dentro de ese documento** porque los CSS del React padre no cruzan un iframe. Diferencia `html.dark` del modo claro; así fondo, texto, cursor y placeholder siempre pertenecen al mismo esquema.
- `tools/apply_contrast_v7.py`: instala de forma idempotente la importación React y los estilos en ambas copias del Cockpit (`web/public` y `Auto`).
- `tools/build_streamlit_bundle.py`: después de `npm run build`, empaqueta los archivos en `Auto/autoos_unified.html`, que es lo que carga Streamlit en la interfaz cinematográfica.

## Lo que NO cambia

- Reproductor, lista de música, URLs y controles de Spotify.
- Supabase, roles RBAC, lógica de simulaciones o kernel.
- Flujo de navegación entre módulos.

## Pruebas manuales para la exposición

1. En modo oscuro, entra en Conducción > Multimedia, busca los campos «Título opcional» y «Enlace Spotify» y escribe algo. El contenido debe verse blanco sobre azul oscuro.
2. Cambia a modo claro. Los campos deben ser blancos con texto azul oscuro. El encabezado debe seguir azul noche y el título CONDUCCIÓN blanco, claramente visible.
3. Cambia entre GPS y Multimedia, alterna el tema dos veces, vuelve al menú y confirma que la selección y las funciones siguen activas.
4. Prueba `npm run lint`, `npm run test:sim`, `npm run build` y `python tools/build_streamlit_bundle.py`.

## Para explicarlo al profesor

> Las interfaces React y el Cockpit están separadas por un iframe. Se corrigieron sus estilos en capas distintas y se sincronizan con el tema activo. Así garantizamos contraste sin alterar la funcionalidad del sistema operativo ni los permisos de los usuarios.
