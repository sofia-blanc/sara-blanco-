# AutoOS — Centro de Simulación (versión web React)

## Para abrirlo en Windows (la opción más sencilla)

1. Descomprime el ZIP completo.
2. Instala **Node.js 20 o superior** si aún no lo tienes (https://nodejs.org/).
3. Haz doble clic en **`LEVANTAR_AUTOOS.bat`** (la primera vez requiere Internet para descargar librerías).
4. Si el navegador no se abre solo, visita **http://localhost:3000**.
5. En la barra superior, entra en **Centro de Simulación**.

**IMPORTANTE:** No ejecutes `streamlit run app.py` para probar esta nueva función. Ese lanzador antiguo abre un HTML precompilado distinto. La nueva sección está integrada en la versión web `web/src/App.tsx`.

## Alternativa en terminal de IntelliJ IDEA / VS Code / PowerShell

```powershell
cd web
npm install
npm run dev
```

La dirección habitual es `http://localhost:3000`.

## Pasos para demostrar al profesor

1. Abre **Centro de Simulación**.
2. Escoge **Sobrecarga de CPU** y pulsa **Iniciar simulación**.
3. Comprueba que aparece un proceso de carga en el panel de CPU y en la bitácora.
4. Pulsa **Suspender multimedia**; la cola y la memoria utilizada cambian.
5. Pulsa **Priorizar seguridad**; el planificador cambia a `PRIORITY_PREEMPTIVE`.
6. Cambia a **Planificador & Simuladores** y verifica que la cola, los procesos y los eventos reflejan los cambios.
7. Regresa al **Centro de Simulación**, pulsa **Finalizar y generar informe** y **Descargar informe .txt**.
8. Prueba **Pérdida de GPS**, selecciona **Reiniciar módulo GPS** y comprueba que el dispositivo vuelve a operativo.
9. Prueba **Laboratorio libre**: cambia clima, batería e inyecta una falla manualmente.

## Qué se implementó

- **8 modos** (7 escenarios guiados + laboratorio libre).
- **Conducción virtual 2D** con velocidad, tiempo, distancia, clima y consumo simulado de energía.
- **Diagnóstico dinámico** de riesgo, batería, dispositivos y demanda de CPU.
- **Acciones reales sobre el motor de estado React**: cambios en batería, fallas de dispositivos, creación/suspensión/prioridad de procesos y eventos.
- **Historial de informes** guardado en `localStorage` de este navegador (hasta 20), exportables como `.txt`.
- El **Cockpit** y el **Planificador** siguen accesibles en sus pestañas.

## Arquitectura / archivos

- `web/src/components/SimulationCenter.tsx`: interfaz de simulación, conducción, diagnóstico, controles, informes.
- `web/src/simulation/scenarios.ts`: biblioteca de casos y decisiones.
- `web/src/simulation/engine.ts`: motor de efectos sobre el planificador y los dispositivos.
- `web/src/simulation/report.ts`: instantáneas, evaluación y exportación.
- `web/src/App.tsx`: estado compartido, navegación, interacción con Cockpit.
- `web/tests/scenarios.test.ts`: pruebas automatizadas.

## Validaciones en un equipo con Node instalado

```powershell
cd web
npm run test:sim
npm run lint
npm run build
```

**Limitaciones importantes:** es una simulación educativa (no kernel, GPS ni vehículo físico). La carga CPU indicada es la **demanda agregada estimada de procesos activos**, no medición real del procesador. El historial se guarda **en este navegador**, todavía **no** en Supabase; es un pendiente de integración del backend cuando tengan las credenciales y políticas de seguridad del proyecto. La versión Streamlit antigua no incorpora automáticamente estas modificaciones sin regenerar su bundle.
