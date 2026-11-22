# AutoOS V18 — carro vectorial y consecuencias visibles

## Objetivo
Corregir los dos problemas detectados en la revisión de V17:

1. El carro de la simulación se percibía como un PNG puesto encima.
2. La opción de riesgo **"continuar sin cambios"** no generaba una consecuencia clara.

## Cambios aplicados

### 1) Vehículo dentro de la escena
- Se eliminó el uso del asset rasterizado dentro de la simulación.
- El vehículo vuelve a dibujarse con SVG, integrado al mismo escenario.
- En la portada también se sustituyó la vista previa por una ilustración vectorial coherente.

### 2) Consecuencia al no intervenir
- Si el usuario elige una opción de tipo **ignorar / mantener / sin cambios**, AutoOS:
  - detiene el vehículo,
  - lleva la velocidad virtual a `0 km/h`,
  - reduce un poco la batería,
  - deja un mensaje visible en la escena.
- La simulación ya no reanuda automáticamente después de esa decisión.

## Archivos modificados
- `web/src/components/MissionStageV17.tsx`
- `web/src/components/VehicleHeroV17.tsx`
- `web/src/components/SimulationCenter.tsx`
- `web/src/v18-polish.css`

## Archivos preservados
- Motor de CPU, RAM y batería.
- Caja Negra y Supabase.
- Permisos de roles ya existentes.
- Lógica base de checkpoints y rutas de V17.

## Validación esperada
1. Iniciar escenario **Batería crítica**.
2. Esperar la bifurcación.
3. Elegir **Continuar sin cambios**.
4. Verificar:
   - velocidad en `0 km/h`,
   - escena detenida,
   - mensaje de consecuencia visible.
5. Elegir otra ruta en una ejecución nueva y verificar que la misión continúe normalmente.
