# SPEC-02 | NAVEGACION | NAVIGATOR | Implementar clase Navigator

## Metadatos

| Campo | Valor |
|-------|-------|
| **ID** | task-SPEC-02-navegacion-navigator-clase-navigator |
| **CÃ³digo de plan** | SPEC-02 |
| **Ã‰pica** | NAVEGACION â€” LÃ³gica de navegaciÃ³n |
| **Feature** | NAVIGATOR â€” Motor de transiciones de estado (Capa 2) |
| **Tipo** | Tarea tÃ©cnica â€” Capa de aplicaciÃ³n/dominio |
| **Prioridad** | CrÃ­tica |
| **EstimaciÃ³n** | 5 h |

---

## DescripciÃ³n tÃ©cnica

Implementar la clase `Navigator` en `navigation/navigator.py`. Es el **motor de la aplicaciÃ³n**: recibe eventos de teclado y produce un nuevo `AppState`. No contiene cÃ³digo de visualizaciÃ³n ni accede directamente al SO â€” opera a travÃ©s de `fs_reader` inyectado.

### Interfaz pÃºblica

```python
class Navigator:
    def __init__(self, fs_reader) -> None: ...
    def initialize(self) -> AppState: ...
    def move_up(self, state: AppState) -> AppState: ...
    def move_down(self, state: AppState) -> AppState: ...
    def enter_directory(self, state: AppState) -> AppState: ...
    def go_parent(self, state: AppState) -> AppState: ...
    def refresh(self, state: AppState) -> AppState: ...
```

### Reglas de negocio

#### `initialize()`
- Obtener unidades via `fs_reader.list_drives()`.
- Estado inicial: `current_dir=Path("/drives")`, `parent_dir=None`, `is_at_drives=True`, `selected_index=0`.

#### `move_up` / `move_down`
- Ajustar `selected_index` en `[0, len-1]` sin comportamiento circular.
- Si `selected_index == -1` (vacÃ­o): no hacer nada.
- Limpiar `error_message` en cualquier movimiento exitoso.
- Usar `dataclasses.replace(state, ...)` para crear copia modificada (no mutar in-place).

#### `enter_directory(state)`
- Si elemento no es directorio o `selected_index == -1`: devolver estado sin cambios.
- Si directorio: actualizar `current_dir`, `parent_dir`, `current_contents`, `selected_index` (0 si tiene hijos, -1 si vacÃ­o), `is_at_drives=False`.
- Si `PermissionError`: establecer `error_message`, no cambiar `current_dir`.

#### `go_parent(state)`
- Si `is_at_drives == True`: devolver estado sin cambios.
- Si `parent_dir is None` (raÃ­z de unidad): volver al nivel de unidades (`is_at_drives=True`, seleccionar la unidad actual).
- En otro caso: navegar al padre restaurando `selected_index` al Ã­ndice del directorio del que se regresÃ³.

#### `refresh(state)`
- Llamar `fs_reader.detect_changes(state.current_dir, state.current_contents)`.
- Si hay cambios: releer directorio y ajustar `selected_index` con `min(idx, len-1)`.
- Si el directorio ya no existe: llamar a `go_parent(state)`.

---

## Objetivo arquitectÃ³nico

La inyecciÃ³n de `fs_reader` en el constructor aplica el principio de **inversiÃ³n de dependencias (DIP)**: `Navigator` depende de una abstracciÃ³n del filesystem, no de su implementaciÃ³n concreta. Esto hace posible el testing completo con mocks sin tocar el disco.

---

## Criterios de aceptaciÃ³n

| # | Criterio |
|---|---------|
| CA-1 | `initialize()` retorna estado con `is_at_drives=True` y unidades en `current_contents` |
| CA-2 | `move_up` no baja de Ã­ndice 0; `move_down` no supera `len-1` |
| CA-3 | `enter_directory` sobre archivo no modifica el estado |
| CA-4 | `enter_directory` con `PermissionError` establece `error_message` y NO cambia `current_dir` |
| CA-5 | `go_parent` desde raÃ­z de unidad retorna al nivel de unidades (`is_at_drives=True`) |
| CA-6 | `go_parent` en nivel de unidades no hace nada |
| CA-7 | `go_parent` restaura `selected_index` al directorio de origen (o 0 si fue eliminado) |
| CA-8 | NavegaciÃ³n exitosa (move/enter/go_parent) limpia `error_message` |
| CA-9 | `refresh` ajusta `selected_index` sin superar el nuevo lÃ­mite |
| CA-10 | `Navigator` no importa de `ui` |

---

## Artefactos y entregables

- `src/miller/navigation/navigator.py`
- `tests/test_navigator.py` (ver SPEC-02-NAVEGACION-TESTING)

---

## Dependencias

| Tipo | DescripciÃ³n |
|------|-------------|
| **Interna** | SPEC-01-DOMINIO-MODELO (`AppState`, `FileEntry` definidos) |
| **Interna** | SPEC-01-DOMINIO-FILESYSTEM (interfaz del `fs_reader` definida) |
| **Bloquea** | SPEC-02-NAVEGACION-TESTING |
| **Bloquea** | SPEC-04-INTEGRACION-MAIN |

---

## Riesgos

| Riesgo | MitigaciÃ³n |
|--------|-----------|
| MutaciÃ³n accidental del `AppState` recibido | Usar `dataclasses.replace(state, ...)` para todas las modificaciones |
| `selected_index` desincronizado tras refresh | Aplicar siempre `min(idx, max(0, len(contents)-1))` al actualizar contenidos |
| `go_parent` en Windows desde `C:\` â†’ `Path("C:\\") == Path("C:\\").parent` | Detectar este caso en `get_parent` con `path == path.parent` |


