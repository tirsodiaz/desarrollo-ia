# Miller Columns — Gestor de archivos en consola

Explorador de archivos en terminal con navegación estilo Miller Columns.

## Ejecución

```bash
pip install -e .
python -m miller
```

## Teclas de funcionamiento

| Tecla | Acción |
|-------|--------|
| `↑` Flecha arriba | Mover la selección hacia arriba |
| `↓` Flecha abajo | Mover la selección hacia abajo |
| `→` Flecha derecha | Entrar en el directorio seleccionado |
| `←` Flecha izquierda | Subir al directorio padre |
| `Escape` | Salir de la aplicación |
| `Ctrl+C` | Finalizar la aplicación con salida limpia |

Leyenda en UI: `↑/↓ mover · → entrar · ← volver · Esc salir`


## Notas

- La navegación es exclusivamente con teclas de flecha; no se usa el ratón.
- Las teclas funcionan de forma idéntica en Windows (via `msvcrt`) y en Linux/macOS (via `termios`).
- Cualquier otra tecla pulsada se ignora y la aplicación continúa en espera.
