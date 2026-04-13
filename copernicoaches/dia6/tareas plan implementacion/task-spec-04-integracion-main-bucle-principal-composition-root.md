# SPEC-04 | INTEGRACION | MAIN | Bucle principal y composition root (__main__.py)

## Metadatos

| Campo | Valor |
|-------|-------|
| **ID** | task-SPEC-04-integracion-main-bucle-principal-composition-root |
| **CÃ³digo de plan** | SPEC-04 |
| **Ã‰pica** | INTEGRACION â€” IntegraciÃ³n, bucle principal y validaciÃ³n final |
| **Feature** | MAIN â€” Punto de entrada y ensamblaje de capas |
| **Tipo** | Tarea tÃ©cnica â€” IntegraciÃ³n |
| **Prioridad** | CrÃ­tica |
| **EstimaciÃ³n** | 4 h |

---

## DescripciÃ³n tÃ©cnica

Implementar `__main__.py` como el **composition root** de la aplicaciÃ³n: Ãºnico mÃ³dulo que instancia todas las capas y las conecta. El bucle principal orquesta el ciclo `render â†’ refresh â†’ read_key â†’ dispatch`.

### Estructura del `main()`

```python
def main(fs_reader=None, navigator=None, key_reader=None):
    fs_reader  = fs_reader  or FilesystemReader()
    navigator  = navigator  or Navigator(fs_reader)
    key_reader = key_reader or read_key

    console  = Console()
    renderer = Renderer(console)
    state    = navigator.initialize()

    try:
        with console.screen(hide_cursor=True):
            while True:
                console.clear()
                renderer.render(state)
                state = navigator.refresh(state)
                key   = key_reader()
                match key:
                    case "up":     state = navigator.move_up(state)
                    case "down":   state = navigator.move_down(state)
                    case "right":  state = navigator.enter_directory(state)
                    case "left":   state = navigator.go_parent(state)
                    case "escape": break
    except KeyboardInterrupt:
        pass   # salida limpia sin traceback
    finally:
        _restore_terminal()
```

### Pantalla alternativa

- `with console.screen(hide_cursor=True):` ejecuta el bucle en el buffer alternativo del terminal.
- Al salir del context manager, Rich restaura automÃ¡ticamente el buffer principal y el cursor.

### `_restore_terminal()`

- Salvaguarda en `finally` adicional al context manager de Rich.
- En Unix: restaurar atributos de `termios` si quedaron en raw mode.
- En Windows: no requiere acciÃ³n especÃ­fica adicional.

### DetecciÃ³n automÃ¡tica de cambios

- `navigator.refresh(state)` se llama **antes** del render en cada iteraciÃ³n.
- Si el directorio actual fue eliminado: `refresh` navega al padre automÃ¡ticamente.

### InyecciÃ³n de dependencias

- `main()` acepta `fs_reader`, `navigator` y `key_reader` como parÃ¡metros opcionales.
- Permite tests de integraciÃ³n sin acceder al disco ni al teclado real.

---

## Objetivo arquitectÃ³nico

El composition root implementa el principio de que **las capas no se conocen entre sÃ­** â€” solo el punto de entrada las conecta. La inyecciÃ³n de dependencias hace que el bucle sea tan testeable como cualquier unidad de negocio, sin mockear partes del sistema de producciÃ³n.

---

## Criterios de aceptaciÃ³n

| # | Criterio |
|---|---------|
| CA-1 | `python -m miller` arranca y muestra la interfaz de Miller Columns |
| CA-2 | El bucle corre en el buffer alternativo (sin dejar historial en terminal) |
| CA-3 | Esc cierra la aplicaciÃ³n limpiamente y restaura el terminal |
| CA-4 | Ctrl+C cierra sin stack trace |
| CA-5 | Terminal queda en estado normal al salir (cursor visible, modo normal) |
| CA-6 | Cambios externos en filesystem se reflejan en la prÃ³xima iteraciÃ³n |
| CA-7 | `fs_reader`, `navigator`, `key_reader` son inyectables para tests |
| CA-8 | `main()` no accede al filesystem ni al teclado directamente |

---

## Artefactos y entregables

- `src/miller/__main__.py` completamente implementado
- `tests/test_integration.py` (ver SPEC-04-INTEGRACION-TESTING)

---

## Dependencias

| Tipo | DescripciÃ³n |
|------|-------------|
| **Interna** | SPEC-01 completo (modelo y filesystem) |
| **Interna** | SPEC-02 completo (navigator e input handler) |
| **Interna** | SPEC-03 completo (renderer con scroll) |
| **Bloquea** | SPEC-04-INTEGRACION-TESTING |
| **Bloquea** | SPEC-04-INTEGRACION-VALIDACION |

---

## Riesgos

| Riesgo | MitigaciÃ³n |
|--------|-----------|
| `console.screen()` no soportado en algunos terminales | `try/except` para continuar sin buffer alternativo como fallback |
| `_restore_terminal` falla si `termios` no disponible en Windows | Proteger con `if sys.platform != "win32":` |
| Polling de `refresh` en cada frame ralentiza UI en directorios de red | Documentar como limitaciÃ³n del MVP; no optimizar en este paso |


