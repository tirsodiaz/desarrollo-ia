# Paso 2 — Lógica de navegación

## Objetivo

Implementar la capa de **lógica de navegación** que gestiona los eventos de teclado, actualiza el estado y controla las transiciones entre directorios. Esta capa no contiene código de visualización ni accede directamente al sistema de archivos — usa las funciones del paso anterior.

---

## 1. Navegador (`navigation/navigator.py`)

### 1.1 Clase `Navigator`

Orquesta las acciones de navegación recibiendo eventos y actualizando el `AppState`.

```python
class Navigator:
    """Gestiona la navegación y actualiza el estado de la aplicación."""

    def __init__(self, fs_reader):
        """Recibe la capa de filesystem como dependencia (desacoplamiento)."""
        ...

    def initialize(self) -> AppState:
        """Crea el estado inicial desde la raíz del sistema."""
        ...

    def move_up(self, state: AppState) -> AppState:
        """Mueve la selección al elemento anterior."""
        ...

    def move_down(self, state: AppState) -> AppState:
        """Mueve la selección al elemento siguiente."""
        ...

    def enter_directory(self, state: AppState) -> AppState:
        """Entra en el directorio seleccionado (flecha derecha)."""
        ...

    def go_parent(self, state: AppState) -> AppState:
        """Retorna al directorio padre (flecha izquierda)."""
        ...

    def refresh(self, state: AppState) -> AppState:
        """Refresca el estado detectando cambios en el filesystem."""
        ...
```

---

## 2. Reglas de navegación

### 2.1 Inicialización (`initialize`) — Actualizado en iteración 2

- **Nivel inicial:** Nivel de unidades de disco (no un directorio específico).
  - **Windows:** obtener lista de unidades activas (C:, D:, E:, etc.) via `list_drives()`
  - **Linux/macOS:** mostrar solo "/" como unidad
- `is_at_drives` = `True` (indicador de estar en nivel de unidades)
- Seleccionar la primera unidad (índice 0).
- `parent_dir` = `None` (no hay padre del nivel de unidades).
- `current_contents` = lista de unidades disponi bles.

### 2.2 Mover arriba (`move_up`)

- Si `selected_index > 0`: decrementar `selected_index`.
- Si `selected_index == 0`: no hacer nada (no circular).
- Si directorio vacío (`selected_index == -1`): no hacer nada.
- Limpiar `error_message` al navegar.

### 2.3 Mover abajo (`move_down`)

- Si `selected_index < len(current_contents) - 1`: incrementar `selected_index`.
- Si ya es el último: no hacer nada (no circular).
- Si directorio vacío: no hacer nada.
- Limpiar `error_message` al navegar.

### 2.4 Entrar en directorio (`enter_directory`)

- Si no hay selección: no hacer nada.
- Si el elemento seleccionado es un **archivo**: no hacer nada (CA04).
- Si es un **directorio**:
  1. El directorio seleccionado pasa a ser `current_dir`.
  2. `parent_dir` = antiguo `current_dir`.
  3. Leer contenido del nuevo directorio.
  4. `selected_index` = 0 si hay contenido, -1 si vacío.
  5. Si hay error de lectura: actualizar `error_message`, no cambiar directorio.

### 2.5 Ir al padre (`go_parent`) — Actualizado en iteración 2

- Si `is_at_drives == True` (estamos en nivel de unidades): no hacer nada.
- Si `parent_dir` es `None` (estamos en raíz de una unidad):
  1. Volver al nivel de unidades.
  2. `is_at_drives` = `True`.
  3. `current_dir` = virtual "/drives" (solo para identificar que estamos en unidades).
  4. `current_contents` = lista de unidades (via `list_drives()`).
  5. `selected_index` = índice de la unidad actual (para mantener selección).
- En otro caso (directorio padre normal):
  1. `current_dir` = `parent_dir`.
  2. Recalcular `parent_dir` del nuevo directorio.
  3. Leer contenido del nuevo directorio actual.
  4. `selected_index` = índice del directorio desde el que se regresó (CA05).
  5. Si no se encuentra (fue borrado): seleccionar el primero.

### 2.6 Refrescar (`refresh`)

- Comparar el contenido actual del directorio con `current_contents`.
- Si hay cambios: actualizar `current_contents`.
- Ajustar `selected_index` si el elemento seleccionado desapareció.
- Manejar el caso de que el directorio actual ya no exista (navegar al padre).

---

## 3. Captura de teclas (`ui/input_handler.py`)

### 3.1 Función `read_key() -> str`

Captura una tecla del teclado y devuelve un identificador normalizado.

```python
def read_key() -> str:
    """Lee una tecla y devuelve su identificador."""
    # Retorna: "up", "down", "left", "right", "escape"
    ...
```

**Implementación multiplataforma:**
- **Windows:** usar `msvcrt.getch()` / `msvcrt.getwch()`.
- **Linux/macOS:** usar `sys.stdin` con `termios` y `tty` para modo raw.
- Las secuencias de escape de flechas (`\x1b[A`, `\x1b[B`, etc.) se normalizan a los identificadores.

---

## 4. Tests de este paso

### Tests de navegación

| Test | Verificación |
|------|-------------|
| `test_initialize_root` | Estado inicial con raíz del sistema |
| `test_move_up_decrements` | Mover arriba decrementa `selected_index` |
| `test_move_up_at_top_stays` | En el primer elemento, no cambia |
| `test_move_down_increments` | Mover abajo incrementa `selected_index` |
| `test_move_down_at_bottom_stays` | En el último elemento, no cambia |
| `test_move_empty_directory` | En directorio vacío, arriba/abajo no hacen nada |
| `test_enter_directory` | Entrar en directorio actualiza `current_dir` y contenido |
| `test_enter_file_no_effect` | Flecha derecha sobre archivo no cambia estado |
| `test_go_parent` | Volver al padre restaura directorio anterior |
| `test_go_parent_selects_previous` | Al volver, la selección queda sobre el directorio de origen |
| `test_go_parent_at_root` | En raíz, flecha izquierda no cambia estado |
| `test_enter_empty_directory` | Entrar en directorio vacío pone `selected_index` a -1 |
| `test_enter_permission_error` | Error de acceso no cambia directorio, pone `error_message` |
| `test_refresh_detects_new_file` | Archivo nuevo aparece tras refresh |
| `test_refresh_deleted_selection` | Archivo seleccionado borrado ajusta índice |
| `test_navigation_clears_error` | Navegar limpia `error_message` |

### Tests de input_handler

| Test | Verificación |
|------|-------------|
| `test_arrow_keys_mapping` | Secuencias de escape se mapean a identificadores |

> **Nota:** Los tests de navegación deben usar un mock de la capa de filesystem para aislar la lógica.

---

## 5. Criterios de validación de este paso

| # | Verificación |
|---|-------------|
| V1 | El navegador inicializa el estado desde la raíz del sistema |
| V2 | `↑`/`↓` mueven la selección correctamente con límites |
| V3 | `→` entra en directorios, ignora archivos |
| V4 | `←` vuelve al padre con selección correcta |
| V5 | En raíz, `←` no hace nada |
| V6 | Directorio vacío se maneja sin errores |
| V7 | Errores de acceso generan `error_message` sin crash |
| V8 | `read_key` distingue flechas y Escape |
| V9 | Todos los tests pasan |

---

## Trazabilidad

| Criterio de aceptación | Cubierto por |
|------------------------|-------------|
| CA01 (arranque) | `initialize` |
| CA02 (↑/↓) | `move_up` / `move_down` |
| CA03 (→ directorio) | `enter_directory` |
| CA04 (→ archivo) | `enter_directory` (sin efecto) |
| CA05 (← con selección) | `go_parent` |
| CA06 (← en raíz) | `go_parent` (sin efecto) |
| CA17 (errores) | Manejo de excepciones en `enter_directory` |
| CA18 (Esc) | `read_key` devuelve "escape" |
| CA19 (vacío) | Manejo de `selected_index == -1` |
| CA20 (cambios) | `refresh` |

---

## ✅ Estado de implementación (23–27 de marzo de 2026)

**Completado exitosamente**

- ✅ `Navigator` clase completa con 6 métodos principales
- ✅ `initialize()`: arranca desde raíz (C:\ o /) con contenido inicial
- ✅ `move_up()` / `move_down()`: movimiento vertical con límites, limpia errores
- ✅ `enter_directory()`: acceso a subdirectorios, discrimina archivos vs directorios
- ✅ `go_parent()`: retorno al padre con selección del origen, sin efecto en raíz
- ✅ `refresh()`: detección automática de cambios, ajuste de selección si necesario
- ✅ `read_key()`: captura multiplataforma (Windows msvcrt, Unix termios)
- ✅ **27 tests de navegación pasados** + **5 tests integración**
- ✅ Manejo robusto de directorios vacíos, permisos, cambios externos
- ✅ Validación de no regresión tras cambios OpenSpec (27 de marzo)

**Cobertura de criterios de aceptación:** CA01, CA02, CA03, CA04, CA05, CA06, CA17, CA18, CA19, CA20
