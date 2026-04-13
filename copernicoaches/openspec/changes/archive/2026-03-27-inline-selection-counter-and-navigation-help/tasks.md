## 1. Header And Footer Layout Update

- [x] 1.1 Ajustar `render()` para eliminar el contador `[n/N]` del bloque de `footer_parts`.
- [x] 1.2 Extender `_build_header()` para aceptar datos de posición y componer estado inline con ruta/contexto + `[n/N]`.
- [x] 1.3 Asegurar truncado de cabecera preservando el contador visible en la misma línea cuando el ancho sea limitado.

## 2. Navigation Hint Consistency

- [x] 2.1 Consolidar el texto de ayuda en renderer con el literal requerido: `up/down mover . -> entrar . <- volver . Esc salir`.
- [x] 2.2 Verificar que el footer mantenga ayuda + error (si existe) sin reintroducir línea separada de contador.

## 3. Test Coverage

- [x] 3.1 Agregar/actualizar tests de renderer para validar que `[n/N]` aparece en la misma línea de estado.
- [x] 3.2 Agregar/actualizar tests que fallen si existe una línea independiente con solo `[n/N]` en footer.
- [x] 3.3 Validar con tests que la ayuda de navegación exacta permanece visible en estados normal y con error.

## 4. Verification

- [x] 4.1 Ejecutar suite de pruebas relevante (`tests/test_renderer.py` y pruebas de integración relacionadas).
- [x] 4.2 Revisar salida manual en terminal Windows para confirmar legibilidad y ausencia de saltos no deseados.
