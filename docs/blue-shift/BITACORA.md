# Bitácora de cambios y decisiones — Blue Shift

| Etapa | Estado | Cambios | Pruebas | Limitaciones |
|---|---|---|---|---|
| 0. Análisis del ZIP | Revisado | Se identificaron dos interfaces y la relación Streamlit–HTML–React | El ZIP original fue inspeccionado | Aún no confirma el diseño final publicado |
| 1. Tema Blue Shift | Aplicación local reportada | CSS de colores en Streamlit/React/HTML | El usuario mostró Streamlit y ejecutó `py_compile` | No hay verificación publicada en Streamlit Cloud |
| 2. Menú inmersivo animado | Pendiente | Nuevo menú React; teclado y animaciones | Pendiente | No debe romper rol ni navegación |
| 3. Integración a Streamlit | Pendiente | Pantalla de entrada e integración HTML | Pendiente | React y Streamlit no comparten estado automáticamente |
| 4. Audio y fuentes | Pendiente | Recursos y controles de sonido | Pendiente | Navegador exige interacción; revisar licencia de distribución |
| 5. Validación final | Pendiente | Revisión de procesos, memoria, Cockpit y roles | Pendiente | Confirmar Supabase y página pública |

## Formato para cada cambio

```text
Fecha:
Autor/es:
Commit / PR:
Archivos tocados:
Objetivo:
Cómo funciona:
Decisiones técnicas:
Qué NO se modificó:
Comandos de prueba + resultado:
Captura/GIF de antes y después:
Problemas encontrados y solución:
Explicación breve para la exposición:
```

No marcar como «completo» algo que solamente funciona en `localhost` sin revisar la página pública.
