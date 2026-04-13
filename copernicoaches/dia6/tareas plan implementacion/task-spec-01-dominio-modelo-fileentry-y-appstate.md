# SPEC-01 | DOMINIO | MODELO | Implementar FileEntry y AppState

## Metadatos

| Campo | Valor |
|-------|-------|
| **ID** | task-SPEC-01-dominio-modelo-fileentry-y-appstate |
| **CÃ³digo de plan** | SPEC-01 |
| **Ã‰pica** | DOMINIO â€” Modelo de estado y capa de sistema de archivos |
| **Feature** | MODELO â€” Modelo de estado (Capa 1) |
| **Tipo** | Tarea tÃ©cnica â€” Capa de dominio |
| **Prioridad** | CrÃ­tica |
| **EstimaciÃ³n** | 2 h |

---

## DescripciÃ³n tÃ©cnica

Implementar las dos clases que conforman el modelo de estado en `state/model.py`:

### `FileEntry` â€” Value Object inmutable

```python
@dataclass(frozen=True)
class FileEntry:
    name: str
    path: Path
    is_dir: bool
```

- `frozen=True`: inmutabilidad garantizada; cualquier modificaciÃ³n lanza `FrozenInstanceError`.
- Representa un Ãºnico elemento del sistema de archivos visible en las columnas.
- Sin lÃ³gica de negocio ni referencias a capas superiores.

### `AppState` â€” Fuente Ãºnica de verdad

```python
@dataclass
class AppState:
    current_dir: Path
    parent_dir: Path | None
    current_contents: list[FileEntry]
    selected_index: int
    error_message: str | None = None
    is_at_drives: bool = False
```

Convenciones de estado:
- `selected_index = -1` â†’ directorio vacÃ­o (convenciÃ³n global de la aplicaciÃ³n)
- `parent_dir = None` â†’ raÃ­z de unidad o nivel de unidades de disco
- `is_at_drives = True` â†’ estamos en el nivel de selecciÃ³n de unidades (raÃ­z virtual)
- `error_message` â†’ se establece en errores de filesystem; se limpia en cada navegaciÃ³n exitosa

---

## Objetivo arquitectÃ³nico

Implementar la **Capa 1 (Estado)** como fuente Ãºnica de verdad. Todas las demÃ¡s capas leen `AppState` pero no lo mutan directamente. Solo el `Navigator` (Capa 2) produce nuevas instancias o actualiza el estado, garantizando flujo de datos unidireccional.

---

## Criterios de aceptaciÃ³n

| # | Criterio |
|---|---------|
| CA-1 | `FileEntry` se instancia con `name`, `path` (Path) e `is_dir` correctamente |
| CA-2 | Asignar `entry.name = "x"` lanza `FrozenInstanceError` |
| CA-3 | `AppState` con valores mÃ­nimos funciona; `error_message` e `is_at_drives` tienen defaults |
| CA-4 | `AppState` acepta mutaciÃ³n directa de campos (es mutable) |
| CA-5 | `state/model.py` no importa de ninguna otra capa del proyecto |
| CA-6 | Imports solo de `dataclasses` y `pathlib` |

---

## Artefactos y entregables

- `src/miller/state/model.py`
- `tests/test_model.py` con tests unitarios del modelo (ver SPEC-01-DOMINIO-TESTING)

---

## Dependencias

| Tipo | DescripciÃ³n |
|------|-------------|
| **Interna** | SPEC-00-INFRA-SETUP (estructura de paquetes creada) |
| **Bloquea** | SPEC-01-DOMINIO-FILESYSTEM (reader usa `FileEntry`) |
| **Bloquea** | SPEC-02-NAVEGACION-NAVIGATOR (navigator usa `AppState`) |
| **Bloquea** | SPEC-03-VISUALIZACION-RENDERER (renderer consume `AppState`) |


