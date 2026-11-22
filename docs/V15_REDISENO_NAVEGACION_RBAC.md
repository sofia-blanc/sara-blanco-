# AutoOS V15 — Rediseño operativo de Navegación, Inicio y permisos

> **Alcance:** mejora de experiencia y modelo educativo sobre V14. No reemplaza el kernel Python, Supabase ni los sensores simulados originales. Compatible con la sincronización automática de Caja Negra V14.

## 1. Cambios solicitados en la revisión del profesor

1. **Inicio sin fondo vacío infinito.** Contenedor de anchura máxima y composición de dos columnas; no se desplazan ilustraciones verticalmente. La imagen del automóvil es un SVG original, inmóvil y embebido en React.
2. **Navegación como misión interactiva.** Se sustituye la pantalla GPS anterior por una escena de vehículo, ruta didáctica, decisiones y salud de periféricos semaforizada.
3. **Permisos diferenciados.** Se separan *Administrador*, *Mecánico*, *Conductor* y *Pasajero*. Dejar claro que el selector React es únicamente un **perfil de demostración**.
4. **Trazabilidad.** Las decisiones importantes utilizan `recordMissionEvent`, que alimenta Caja Negra. El mecanismo V14 envía y confirma los eventos con Supabase cuando está disponible.

## 2. Archivos de código

| Archivo | Responsabilidad |
| --- | --- |
| `web/src/components/VehicleArtworkV15.tsx` | Ilustración SVG estática, original y reutilizable en el menú y la misión |
| `web/src/components/NavigationMissionV15.tsx` | Escena de misión, salud de periféricos, selección de destinos y decisiones |
| `web/src/simulation/missionDecisionsV15.ts` | Catálogo tipado y explicaciones de las decisiones |
| `web/src/simulation/accessPolicyV15.ts` | Matriz central de visibilidad de módulos y acciones |
| `web/src/App.tsx` | Propietario único del estado, aplicador de decisiones y eventos, guardas de navegación |
| `web/src/components/CinematicMenu.tsx` | Portada con automóvil estático, cambios de perfil y botones con bloqueo |
| `web/src/components/ModuleScene.tsx` | Barra de módulos con guardas, selector de cuatro roles |
| `web/src/components/AutoOSModulesV11.tsx` | Enruta la página `GPS` a `NavigationMissionV15` sin duplicar estado |
| `web/src/components/CockpitWorkspaceV5.tsx` | Roles, descripción y auditoría administrativa de demostración |
| `web/src/v15-final.css` | Diseño responsivo del menú y misión; paletas claras/oscuras; control de ancho |
| `web/tests/v15.test.cjs` | Pruebas de roles, permisos, denegación por defecto y decisiones |

## 3. Modelo de autorización V15

**Administrador (demostración):** todos los módulos; diagnósticos cloud, gestión técnica, auditoría y escenarios.

**Mecánico:** mantenimiento, simulación técnica, planificador, recuperación y prueba de sensores, lectura de eventos. Sin administración de credenciales ni diagnóstico Cloud administrativo.

**Conductor:** Inicio, Navegación, Cabina, Caja Negra de lectura; iniciar/detener ruta, moderar velocidad, ahorrar energía, reruta, inspeccionar e ignorar con registro. No inyecta fallas ni configura el planificador.

**Pasajero:** Inicio y Cabina, con acceso a funciones de confort/multimedia/asistente; no Navegación operativa, Simulación, Planificador, Caja Negra ni Supabase.

### Advertencia de seguridad

Las opciones de React **no autentican al usuario**. Al cambiar el selector no se concede acceso administrativo real en `AutoOS_1/modules/auth_security.py` ni en la base de datos. En una solución productiva, los perfiles se obtendrían de una sesión de identidad validada por Python/Supabase Auth, y **cada operación sensible debe comprobarse otra vez en el servidor**. El backend existente sigue validando sus operaciones; la V15 no lo modifica ni declara que se haya implantado una autenticación nueva.

Los instrumentos del Cockpit HTML heredado conservan su seguridad interna. La V15 limita el acceso desde el explorador y no confunde eso con autorización de backend.

## 4. Flujo de una decisión de misión

```text
Usuario selecciona ACCIÓN
       |
       v
accessPolicyV15.canExecute(rol, accion) ---- denegado -> mensaje RBAC
       |
       v
App.navigationDecision(accion)
       |
       +-- missionStart / missionStop / missionSpeed / handleSimulatorAction
       +-- setBattery -> makeBattery (ahorro)
       +-- recordMissionEvent(rol, accion, efectos previstos)
       |
       +--> misión, CPU/RAM/energía y dispositivos comunes en App.tsx
       +--> Caja Negra -> cola V14 -> Streamlit/Python -> Supabase
```

**Un reloj:** el movimiento virtual usa el intervalo existente de `missionTick`; entrar y salir de Navegación no crea otro temporizador. Al avanzar manualmente un minuto se ejecuta un tick adicional de forma voluntaria. Los consumos son estimaciones educativas del vehículo virtual, no mediciones del computador físico.

### Efectos de decisiones

- **Iniciar:** activa la ruta virtual.
- **Continuar 1 min:** ejecuta un ciclo y descuenta energía según el modelo existente.
- **Reducir velocidad:** fija 25 km/h; afecta el término de potencia de tracción en los siguientes ciclos.
- **Ahorro:** habilita el modo de energía baja; el motor aplica su política de suspensión/prioridad si corresponde.
- **Reruta:** inicia el siguiente circuito alternativo (el progreso se reinicia y queda registrado).
- **Detener e inspeccionar:** detiene vehículo/ruta y registra decisión.
- **Recuperar GNSS:** acción técnica de recuperación del sensor.
- **Simular falla GNSS:** exclusivamente administrador/mecánico; inyecta fallo didáctico.
- **Ignorar advertencia:** solo registra elección; **no repara** el dispositivo.

## 5. Semáforo de salud

Los estados se leen de `devices`, **nunca** de colores aleatorios:

| Estado del dispositivo | Color | Significado |
| --- | --- | --- |
| `operativo` | Verde | Funciona en la simulación |
| `degradado` | Amarillo | Requiere atención |
| `falla` o `desconectado` | Rojo | Indisponible |

Los porcentajes se obtienen de `device.health`. Se muestra texto además de color para accesibilidad.

## 6. Validación local

En PowerShell, desde la raíz de AutoOS (después de aplicar el paquete):

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\validar_v12.ps1
cd web
node .\tests\v15.test.cjs
cd ..
.\.venv\Scripts\python.exe -m streamlit run app.py
```

**Pruebas manuales imprescindibles:**

1. Inicio: zoom 50%, 100%, 150%; confirmar márgenes, ilustración fija y ausencia de desbordamientos.
2. Tema claro/oscuro: comprobar contrastes en todas las opciones, vehículo y semáforos.
3. Conductor: iniciar ruta, reducir velocidad, ahorro, ruta alternativa, inspección y Caja Negra.
4. Mecánico: inyectar falla GNSS, observar rojo; recuperar sensor, observar verde.
5. Pasajero: negar Navegación, Planificador, Caja Negra y Supabase; permitir funciones de confort.
6. Administrador: navegación, planificador, simulación, nube y auditoría. Confirmar permisos reales Python por separado.
7. Supabase: ejecutar misión; abrir Caja Negra; comprobar confirmados/pendientes; consultar `public.eventos`.
8. Streamlit Cloud: configurar sus secretos de forma segura; verificar URL final luego de merge.

## 7. Despliegue

**No publicar directamente en `main` sin la revisión del equipo.** Crear rama V15, ejecutar validadores, hacer PR, revisar cambios. El HTML compilado que utiliza Streamlit debe regenerarse por `tools/build_streamlit_bundle.py` después de la compilación de Vite.

No incorporar `secrets.toml`, `.env`, claves privadas, carpetas `.autoos_*_backup`, ni assets protegidos del juego Persona 3 Reload.
