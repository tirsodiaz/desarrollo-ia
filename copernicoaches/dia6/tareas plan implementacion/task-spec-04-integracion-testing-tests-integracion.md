# SPEC-04 | INTEGRACION | TESTING | Tests de integraciÃ³n del bucle principal

## Metadatos

| Campo | Valor |
|-------|-------|
| **ID** | task-SPEC-04-integracion-testing-tests-integracion |
| **CÃ³digo de plan** | SPEC-04 |
| **Ã‰pica** | INTEGRACION â€” IntegraciÃ³n, bucle principal y validaciÃ³n final |
| **Feature** | TESTING â€” Suite de tests de integraciÃ³n end-to-end |
| **Tipo** | Tarea tÃ©cnica â€” Testing de integraciÃ³n |
| **Prioridad** | Alta |
| **EstimaciÃ³n** | 4 h |

---

## DescripciÃ³n tÃ©cnica

Implementar los tests de integraciÃ³n que verifican el comportamiento end-to-end del bucle principal. Usan capas reales de dominio pero con `key_reader` falso (secuencia predefinida) y `Renderer` que escribe en `StringIO`.

### Estrategia: fake key reader

```python
def make_key_sequence(*keys):
    """Genera un key_reader que devuelve las teclas en orden y luego escape."""
    q = list(keys) + ["escape"]
    def reader():
        return q.pop(0)
    return reader
```

### Tests (`tests/test_integration.py`)

| ID | Nombre | VerificaciÃ³n |
|----|--------|-------------|
| TI-01 | `test_full_navigation_flow` | Secuencia `down Ã— 2 â†’ right â†’ up â†’ left â†’ escape`. El bucle termina sin excepciÃ³n y `current_dir` == directorio de inicio |
| TI-02 | `test_escape_exits` | Inyectar `["escape"]`. El bucle termina en la primera iteraciÃ³n |
| TI-03 | `test_ctrl_c_clean_exit` | `key_reader` que lanza `KeyboardInterrupt`. `main()` termina sin propagar la excepciÃ³n |
| TI-04 | `test_render_after_navigation` | Inyectar `down + escape`. El renderer se invoca â‰¥2 veces; en la segunda llamada `selected_index` es diferente al inicial |
| TI-05 | `test_filesystem_change_detected` | Crear archivo en `tmp_path` durante ejecuciÃ³n; inyectar `"unknown" + escape`. El estado final `current_contents` incluye el nuevo archivo |

### Fixture de directorio de integraciÃ³n

```python
@pytest.fixture
def app_tmpdir(tmp_path):
    """Estructura mÃ­nima para tests de integraciÃ³n."""
    (tmp_path / "dirA").mkdir()
    (tmp_path / "dirB").mkdir()
    (tmp_path / "dirA" / "sub").mkdir()
    (tmp_path / "file.txt").write_text("contenido")
    return tmp_path
```

---

## Objetivo arquitectÃ³nico

Los tests de integraciÃ³n validan que todas las capas colaboran correctamente. Son la Ãºltima lÃ­nea de defensa automatizada antes de la validaciÃ³n manual, y detectan incompatibilidades de interfaz entre capas que los tests unitarios aislados no pueden encontrar.

---

## Criterios de aceptaciÃ³n

| # | Criterio |
|---|---------|
| CA-1 | Los 5 tests de integraciÃ³n pasan |
| CA-2 | Los tests no requieren terminal real ni teclado fÃ­sico |
| CA-3 | Suite de integraciÃ³n completa en < 15 segundos |
| CA-4 | TI-03 confirma que `KeyboardInterrupt` no se propaga fuera de `main()` |
| CA-5 | TI-05 confirma que el auto-refresh detecta cambios externos |
| CA-6 | `pytest` completo (unitarios + integraciÃ³n) ejecutable con un solo comando |

---

## Artefactos y entregables

- `tests/test_integration.py` con 5 tests
- `tests/conftest.py` actualizado con `app_tmpdir` y `make_key_sequence`

---

## Dependencias

| Tipo | DescripciÃ³n |
|------|-------------|
| **Interna** | SPEC-04-INTEGRACION-MAIN (`main()` con inyecciÃ³n de dependencias) |
| **Interna** | Todos los tests unitarios de SPEC-01, SPEC-02, SPEC-03 pasando |
| **Bloquea** | SPEC-04-INTEGRACION-VALIDACION |

---

## Riesgos

| Riesgo | MitigaciÃ³n |
|--------|-----------|
| TI-05 tiene race condition por timing | Usar `navigator.refresh()` explÃ­cito en el test, no depender del timing del bucle |
| TI-01 falla si `tmp_path` no tiene subdirectorios navegables | Fixture `app_tmpdir` crea estructura mÃ­nima con nesting |
| Tests mÃ¡s lentos en CI por filesystem real | Aceptable; si supera 30s, convertir a mocks parciales |

---

## Actualizacion OpenSpec 2026-03-27

### Nuevo test de integracion

- `test_header_remains_visible_during_vertical_scroll`: ejecutar secuencia de navegacion larga hacia abajo y arriba y verificar que la ruta activa permanece en el output de cada frame.

### Cobertura esperada

- Validar cabecera fija + bloques dinamicos visibles sin alterar semantica de flechas.



