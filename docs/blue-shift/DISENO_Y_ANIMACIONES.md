# Especificación del menú animado AutoOS

## Meta visual

Una pantalla de acceso inmersiva inspirada en la experiencia del menú de Persona 3 Reload: jerarquía tipográfica marcada, selección diagonal, capas acuáticas, tipografía dinámica y transiciones coreografiadas.

No será una capa azul sobre el antiguo dashboard. La **pantalla principal cambia de estructura**, pero los módulos existentes se mantienen accesibles.

## Navegación conceptual

```text
Pantalla principal / Blue Shift
   ├── Arranque y kernel          (Streamlit/Python)
   ├── Procesos y CPU             (Streamlit/Python; React, cuando aplique)
   ├── Planificador               (Streamlit y React)
   ├── Memoria y archivos         (Streamlit/Python)
   ├── Centro de simulación       (React)
   ├── Cockpit                    (HTML independiente o React)
   └── Diagnóstico y seguridad    (Streamlit/Python)
```

**Pendiente de implementar:** el salto entre una entrada React y las pestañas Python de Streamlit necesitará un enlace de navegación real (no solo un cambio de texto), con un mecanismo compatible con el iframe y la sesión. No presentar estos enlaces como completos hasta probarlos.

## Estados previstos de la animación

| Estado | Comportamiento | Cómo se verifica |
|---|---|---|
| `ENTERING` | Fondo, título y opciones aparecen en capas escalonadas | Se ve al abrir el menú |
| `IDLE` | Ondas y partículas suaves, sin movimiento excesivo | Permanece legible en reposo |
| `FOCUSED` | Selector diagonal se desplaza a la opción activa | Flechas, ratón y tabulador |
| `SELECTING` | Opción elegida se destaca; las demás salen | Clic/Enter inicia transición |
| `TRANSITION` | Se abre el módulo seleccionado | Sin perder datos ni estado |
| `RETURNING` | Retorno al menú con posición conservada | Botón Volver/Escape cuando aplique |

## Requisitos de interacción

1. Navegación por ratón y teclado; Enter confirma y Escape vuelve cuando sea apropiado.
2. El foco visible nunca debe desaparecer; evitar selectores que no permitan leer el texto.
3. Las acciones sensibles respetan las restricciones existentes de `mecanico`, `conductor` y `pasajero`.
4. La preferencia `prefers-reduced-motion` reduce o elimina movimiento decorativo.
5. Animaciones transform/opacity para evitar redibujos innecesarios.
6. El audio se inicia solo después de la primera interacción del usuario; debe tener control de volumen y botón de silencio, y no causar fallos si falta el archivo.
7. Si la descarga del audio o una fuente falla, el menú sigue siendo navegable.
8. El objetivo visual se verifica tanto en el prototipo React como en la presentación real de Streamlit.

## Recursos del futuro diseño

```text
web/public/
  audio/          (selección, confirmar, volver; archivos que se puedan distribuir)
  fonts/          (archivos de fuentes que se puedan publicar)
  images/         (ilustraciones y fondos permitidos)
```

La ruta exacta y el empaquetado final pueden cambiar. Un HTML integrado en Streamlit con `srcdoc` no puede presuponer que `/audio/...` o `/fonts/...` funcionen; el empaquetador tendrá que incluir los recursos o definir un origen accesible.

## Separación del código

- `BlueShiftMenu.tsx` — interacción del menú y callbacks de navegación, **no** simulación de CPU.
- `blue-shift-menu.css` — máscaras, diagonales, efectos, animaciones y tema.
- `audio.ts` — sonidos y estado de mute, sin modificar el kernel.
- Componentes existentes de `App.tsx` — algoritmos y controles funcionales actuales.

Estos son **nombres propuestos**, no archivos que ya existan. Se crearán de forma incremental y con pruebas.
