# Convenciones para comentarios de código AutoOS

**Objetivo:** cualquier integrante debe poder responder: «¿Qué hace este componente?», «¿por qué se implementó así?» y «¿cómo se conecta con el sistema operativo?».

## TypeScript / React: TSDoc y notas de intención

```tsx
/**
 * Menú de entrada a AutoOS.
 *
 * RESPONSABILIDAD: dibujar las opciones y comunicar la elección del usuario.
 * NO HACE: modificar directamente procesos, memoria, roles o Supabase.
 *
 * @param onNavigate - Callback que solicita abrir un módulo existente.
 * @param reducedMotion - Preferencia del usuario para reducir animaciones.
 */
function BlueShiftMenu({ onNavigate, reducedMotion }: MenuProps) {
  // Estado visual: no representa ni altera el estado real del kernel.
  const [selectedIndex, setSelectedIndex] = useState(0);
  // ...
}
```

Cuando una función maneje un control del sistema, documentar **precondiciones**, **cambios de estado**, **validación RBAC** y **efectos secundarios**. Para transiciones CSS, explicar qué capa se mueve y por qué, no cada propiedad obvia.

## Python / Streamlit: docstrings

```python
def mostrar_pantalla_inicio(estado_kernel: dict) -> None:
    """Presenta la entrada visual usando el estado existente del kernel.

    No arranca ni detiene procesos. La ejecución real continúa en
    los controladores del dashboard y respeta los permisos actuales.

    Args:
        estado_kernel: instantánea de solo lectura del kernel Python.
    """
    # ...
```

## Comentario valioso vs. redundante

```tsx
// NO: Aumenta el índice en uno.
setSelectedIndex(i + 1);

// SÍ: Al volver del módulo mantenemos la selección previa para que el
// usuario no tenga que recorrer otra vez todo el menú.
setSelectedIndex(previousSelection);
```

## Reglas del equipo

- Comentarios y documentación **en español**, términos técnicos conservados cuando ayuden (`iframe`, `RBAC`, `postMessage`, `scheduler`).
- No afirmar «conectado a Supabase» únicamente porque existan variables de entorno; explicar la comprobación real.
- No dejar bloques enormes de código desactivado ni comentarios obsoletos.
- Funciones pequeñas, nombres explícitos y comentarios de intención en partes complejas.
- Ante una corrección, actualizar el comentario, las pruebas y la bitácora en el mismo Pull Request.
- Evitar copiar código externo sin atribución o sin revisar condiciones de uso.
