# Guía para presentar AutoOS ante el profesor

**Meta:** una exposición coherente aunque el profesor escoja al azar a un integrante.

## Explicación de 60–90 segundos

> AutoOS es un simulador académico de sistema operativo vehicular. Su núcleo administra procesos, prioridades, CPU y memoria; el dashboard muestra lo que ocurre. El rediseño Blue Shift cambia la forma de navegar y visualizar el sistema, pero no sustituye los algoritmos. Tenemos un dashboard Streamlit para las funciones Python y una interfaz React para simulaciones y Cockpit. Para que React llegue al sitio público, compilamos y empaquetamos su salida en un HTML que Streamlit puede mostrar. Las acciones se mantienen bajo las restricciones de los roles del sistema.

## Recorrido recomendado

1. **Entrada:** explicar la navegación y qué módulo representa cada opción del menú.
2. **Arranque:** iniciar kernel y observar cambio de estado.
3. **Procesos:** crear o mostrar tareas, ver lista de estados, explicar PID y prioridad.
4. **Planificador:** demostrar FCFS / RR / prioridad según los controles disponibles y el diagrama de Gantt.
5. **Memoria:** mostrar particiones y paginación; explicar por qué hay diferencias entre RAM física y virtual.
6. **Contingencia:** activar un escenario y observar qué cambia en el sistema, sin confundir efectos gráficos con lógica real.
7. **Roles:** demostrar que no todos pueden calibrar o inyectar fallas.
8. **Cierre:** mostrar la bitácora y explicar cómo se documentaron y probaron los cambios.

No prometer demostrar un escenario si todavía no se ha comprobado en la versión final publicada.

## Preguntas posibles y respuestas breves

**¿Por qué usaron React y Streamlit?** Streamlit presenta módulos Python y el kernel; React construye experiencias interactivas. El enlace se hace mediante un HTML integrado. Son dos tecnologías con estados distintos.

**¿Cambiar el menú cambia el algoritmo?** No. Las animaciones y el diseño no modifican FCFS, RR, prioridades, procesos o memoria.

**¿Qué sucede si el usuario es pasajero?** La interfaz debe respetar las restricciones RBAC existentes; la apariencia no concede privilegios.

**¿Qué pasa si el navegador no reproduce un sonido?** La interfaz debe seguir funcionando sin audio y permitir activarlo tras interactuar.

**¿Se ejecutan realmente todas las acciones del React sobre Python?** No necesariamente. La integración se debe verificar acción por acción; un `iframe` no sincroniza automáticamente los dos entornos.

**¿Cómo saben que no dañaron el proyecto?** Pruebas Python del kernel, comprobación TypeScript, pruebas de simulación frontend, compilación, revisión manual y verificación en el despliegue.

## Reparto de preparación

Todos los integrantes deben practicar el recorrido completo. Cada PR debe explicar qué componente cambió, qué decisión tomó y cómo probarlo. Nadie depende de que solamente el autor del código sepa responder.
