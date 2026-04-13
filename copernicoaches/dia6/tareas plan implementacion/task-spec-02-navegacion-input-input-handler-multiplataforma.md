# SPEC-02 | NAVEGACION | INPUT | Captura de teclado multiplataforma (input_handler.py)

## Metadatos

| Campo | Valor |
|-------|-------|
| **ID** | task-SPEC-02-navegacion-input-input-handler-multiplataforma |
| **CÃ³digo de plan** | SPEC-02 |
| **Ã‰pica** | NAVEGACION â€” LÃ³gica de navegaciÃ³n |
| **Feature** | INPUT â€” Captura de events de teclado |
| **Tipo** | Tarea tÃ©cnica â€” Infraestructura de entrada |
| **Prioridad** | Alta |
| **EstimaciÃ³n** | 3 h |

---

## DescripciÃ³n tÃ©cnica

Implementar `read_key() -> str` en `ui/input_handler.py`. Captura una tecla en modo raw (sin Enter) y la normaliza a un identificador de string agnÃ³stico de plataforma.

### Tabla de mapeo de teclas

| Tecla fÃ­sica | String devuelto |
|-------------|----------------|
| Flecha arriba | `"up"` |
| Flecha abajo | `"down"` |
| Flecha izquierda | `"left"` |
| Flecha derecha | `"right"` |
| Escape | `"escape"` |
| Ctrl+C | Propagar `KeyboardInterrupt` (nunca capturar) |
| Cualquier otra | `"unknown"` |

### ImplementaciÃ³n Windows (`sys.platform == "win32"`)

```python
import msvcrt

def read_key() -> str:
    ch = msvcrt.getwch()
    if ch == "\xe0":           # prefijo de teclas especiales
        ch2 = msvcrt.getwch()
        return {"\x48": "up", "\x50": "down",
                "\x4b": "left", "\x4d": "right"}.get(ch2, "unknown")
    if ch == "\x1b": return "escape"
    if ch == "\x03": raise KeyboardInterrupt
    return "unknown"
```

### ImplementaciÃ³n Linux/macOS (`termios` + `tty`)

```python
import sys, tty, termios

def read_key() -> str:
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            seq = sys.stdin.read(2)
            return {"\x1b[A": "up", "\x1b[B": "down",
                    "\x1b[D": "left", "\x1b[C": "right"}.get("\x1b" + seq, "escape")
        if ch == "\x03": raise KeyboardInterrupt
        return "unknown"
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
```

La implementaciÃ³n selecciona la rama segÃºn `sys.platform`. El bloque `finally` garantiza que el terminal queda en modo normal incluso ante excepciones inesperadas.

---

## Objetivo arquitectÃ³nico

Encapsular toda la interacciÃ³n con el terminal en modo raw en un Ãºnico mÃ³dulo. El `Navigator` y el bucle principal solo reciben strings normalizados, haciendo posible reemplazar o mockear el input en tests sin modificar lÃ³gica de negocio.

---

## Criterios de aceptaciÃ³n

| # | Criterio |
|---|---------|
| CA-1 | `read_key()` devuelve `"up"`, `"down"`, `"left"`, `"right"` para las flechas |
| CA-2 | `read_key()` devuelve `"escape"` para la tecla Escape |
| CA-3 | `read_key()` propaga `KeyboardInterrupt` para Ctrl+C (no lo captura) |
| CA-4 | El terminal queda en estado normal despuÃ©s de cada llamada (bloque `finally`) |
| CA-5 | Compila y ejecuta en Windows sin importar `termios` |
| CA-6 | Compila y ejecuta en Linux/macOS sin importar `msvcrt` |
| CA-7 | No importa de `state`, `navigation` ni `filesystem` |

---

## Artefactos y entregables

- `src/miller/ui/input_handler.py` con `read_key()` para ambas plataformas

---

## Dependencias

| Tipo | DescripciÃ³n |
|------|-------------|
| **Interna** | SPEC-00-INFRA-SETUP (paquete `ui/` existe) |
| **Bloquea** | SPEC-04-INTEGRACION-MAIN (bucle principal llama `read_key()`) |
| **Bloquea** | SPEC-02-NAVEGACION-TESTING |

---

## Riesgos

| Riesgo | MitigaciÃ³n |
|--------|-----------|
| Terminal en raw mode no restaurado si hay excepciÃ³n | `finally` en Unix; `msvcrt` no requiere restauraciÃ³n en Windows |
| Tests de `read_key` difÃ­ciles de automatizar | Mockear `msvcrt.getwch` / `sys.stdin.read` en tests |
| Secuencias de escape varÃ­an entre emuladores | Cubrir solo ANSI estÃ¡ndar; documentar limitaciÃ³n |


