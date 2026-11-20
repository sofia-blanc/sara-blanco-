# AutoOS Blue Shift — documentación del rediseño

> **Estado:** planificación y documentación inicial, a partir del ZIP `sara-blanco--main (3).zip`. Este paquete **no modifica el funcionamiento de AutoOS** ni implementa aún el nuevo menú animado.

## Objetivo

Transformar la presentación visual de AutoOS en una experiencia de navegación con menús diagonales, animaciones, profundidad, fondo dinámico y respuesta de audio, **sin sustituir la lógica académica del sistema operativo**. La referencia estética principal es el menú de Persona 3 Reload; el contenido y las funciones serán propios de AutoOS.

## Cómo leer la documentación

1. [ARQUITECTURA.md](ARQUITECTURA.md): descubre cómo se conectan Streamlit, React, Cockpit y los módulos del sistema.
2. [DISENO_Y_ANIMACIONES.md](DISENO_Y_ANIMACIONES.md): especifica estados, transiciones, audio, tipografías y accesibilidad.
3. [ESTANDAR_COMENTARIOS.md](ESTANDAR_COMENTARIOS.md): explica cómo documentaremos cada archivo y función nueva.
4. [GUIA_PRESENTACION.md](GUIA_PRESENTACION.md): guion y preguntas frecuentes para que cualquiera del equipo presente.
5. [BITACORA.md](BITACORA.md): registro de decisiones técnicas, pruebas y cambios por etapas.

## Regla de trabajo

**Interfaz ≠ motor del sistema.** Un botón del nuevo menú navega a una función ya existente; no debe inventar resultados de CPU, estados de sensores ni simular una conexión real a Supabase. Una animación nunca puede conferir permisos que el control RBAC niega.

## Forma de colaborar en GitHub

- Crear rama propia desde la versión actual de `main` y registrar los cambios mediante commits enfocados.
- Abrir Pull Request y usar `.github/pull_request_template.md`.
- Adjuntar capturas o GIFs de antes y después, comandos de prueba y explicación de riesgos.
- **No fusionar** hasta validar tanto la interfaz como la publicación que usa Streamlit Cloud.

## Recursos visuales y sonoros

Probar recursos instalados en Windows no equivale a tenerlos disponibles para otros usuarios. Para la aplicación pública, las fuentes y los sonidos deben estar incluidos como archivos web y en el HTML integrado (o tener URL disponible), respetando las licencias aplicables. Mantendremos efectos originales o recursos utilizables cuando corresponda, sin bloquear el trabajo de prototipado.
