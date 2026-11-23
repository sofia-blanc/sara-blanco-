# AutoOS V20 — conducción continua (corrige el minijuego V19)

## Qué cambia

Ya NO aparece la pantalla que pregunta «¿Qué camino tomas?» ni hay que dar clic para continuar. En los minutos virtuales 2, 7, 12 y 17 aparece una señal de los caminos próximos. El usuario se posiciona con ← o → y al cruzar los minutos 5, 10, 15 y 20 AutoOS aplica automáticamente la ruta correspondiente, mantiene la marcha y registra la decisión. Las colisiones y elecciones peligrosas aún pueden detener el vehículo como consecuencia del sistema operativo; los checkpoints ya no.

Con tres rutas, los carriles izquierdo/centro/derecho corresponden a las rutas 1/2/3. Con dos rutas, izquierda y centro eligen la primera, derecha elige la segunda. La interfaz muestra exactamente qué se seleccionará.

## Instalación en Windows (sobre el proyecto V19)

1. Extrae este ZIP directamente en la carpeta raíz donde están `app.py`, `web`, `Auto` y `tools` de AutoOS. **No borres ni reemplaces el proyecto completo.**
2. Abre PowerShell en esa carpeta y ejecuta:

```powershell
python .\tools\aplicar_v20.py
powershell -ExecutionPolicy Bypass -File .\tools\validar_v20.ps1
```

3. Si las validaciones terminan bien, prueba en el navegador:
   - Inicia Batería crítica como rol Mecánico/Administrador.
   - Conduce con ← → y ↑ ↓; no hace falta hacer clic en el área del juego.
   - Entre el minuto 2 y 5 posiciona el coche en otro carril.
   - En el minuto 5 debe ejecutarse la decisión **sin detener el reloj** ni abrir botones de rutas.
   - Esquiva un obstáculo y verifica la bitácora. Si chocas, el SO debe detenerte por seguridad y permitir recuperación (hasta 3 impactos).
   - Comprueba que después del minuto 5 siga llegando el minuto 10.
4. Antes de hacer merge/push, revisa los dos HTML recompilados con `git status`. Luego realiza commit y push:

```powershell
git status --short
git add web/src web/tests docs/V20_CONDUCCION_SIN_CLIC.md tools/aplicar_v20.py tools/validar_v20.ps1 Auto/autoos_unified.html Auto/bridge_component/index.html
git commit -m "feat: conducir bifurcaciones con flechas sin pausar minijuego"
git push
```

Si tienes la rama del PR V19 activa, `git push` actualiza esa rama; el despliegue público de Streamlit puede requerir fusionar el PR a la rama que use Streamlit.

## Límites

No se cambian `Auto/app.py`, el kernel Python, credenciales ni tablas Supabase. El motor de colisiones V19 sigue siendo el mismo. Estas modificaciones necesitan instalarse sobre un árbol V19 compatible; el instalador aborta antes de escribir si encuentra diferencias estructurales importantes. La compilación y el despliegue final se verifican ejecutando el validador en el proyecto real.
