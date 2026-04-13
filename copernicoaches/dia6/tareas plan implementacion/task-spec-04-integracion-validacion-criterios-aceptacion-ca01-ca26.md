# SPEC-04 | INTEGRACION | VALIDACION | ValidaciÃ³n final: CA01â€“CA26

## Metadatos

| Campo | Valor |
|-------|-------|
| **ID** | task-SPEC-04-integracion-validacion-criterios-aceptacion-ca01-ca26 |
| **CÃ³digo de plan** | SPEC-04 |
| **Ã‰pica** | INTEGRACION â€” IntegraciÃ³n, bucle principal y validaciÃ³n final |
| **Feature** | VALIDACION â€” Checkpoint de calidad y entrega |
| **Tipo** | Tarea de validaciÃ³n â€” QA / Arquitectura |
| **Prioridad** | CrÃ­tica |
| **EstimaciÃ³n** | 3 h |

---

## DescripciÃ³n tÃ©cnica

Ejecutar la validaciÃ³n manual completa contra los 26 criterios de aceptaciÃ³n de la especificaciÃ³n funcional, y la validaciÃ³n automatizada del suite de tests con reporte de cobertura. Esta tarea es el **checkpoint final de arquitectura** antes de considerar la implementaciÃ³n entregable.

### Checklist de criterios de aceptaciÃ³n

| # | DescripciÃ³n | CÃ³mo validar | âœ“ |
|---|-------------|-------------|---|
| CA01 | Tres columnas con contenido de raÃ­z | Arrancar la app, verificar layout | â˜ |
| CA02 | â†‘/â†“ cambian selecciÃ³n y actualizan preview | Navegar en directorio con varios elementos | â˜ |
| CA03 | â†’ entra en directorio, columnas se desplazan | Entrar en â‰¥3 niveles de profundidad | â˜ |
| CA04 | â†’ sobre archivo no hace nada | Seleccionar archivo y pulsar â†’ | â˜ |
| CA05 | â† vuelve al padre con selecciÃ³n previa | Entrar y salir de un directorio | â˜ |
| CA06 | â† en raÃ­z de unidad vuelve al nivel de unidades | Pulsar â† desde `C:\` | â˜ |
| CA07 | Directorios y archivos se distinguen visualmente | Verificar colores/estilos | â˜ |
| CA08 | SelecciÃ³n claramente identificable | Verificar inversiÃ³n de color | â˜ |
| CA09 | Ruta absoluta en cabecera y siempre visible durante scroll vertical | Navegar y desplazarse en listados largos verificando persistencia de cabecera | â˜ |
| CA10 | Directorios primero, alfabÃ©tico case-insensitive | Directorio con mix de archivos y dirs | â˜ |
| CA11 | Archivos ocultos no se muestran | Dotfiles (Linux) o atributo hidden (Windows) | â˜ |
| CA12 | Symlinks no se muestran | Directorio con enlaces simbÃ³licos | â˜ |
| CA13 | Truncamiento con `â€¦` | Archivo con nombre largo (>40 chars) | â˜ |
| CA14 | Scroll automÃ¡tico con â–²/â–¼ y bloques dinÃ¡micos visibles | Directorio con 20+ entradas, navegar hacia abajo y arriba | â˜ |
| CA15 | Archivo de texto: contenido completo en columna derecha | Seleccionar `.txt` o `.py` | â˜ |
| CA16 | Preview binario: solo nombre | Seleccionar `.exe` o `.zip` | â˜ |
| CA17 | Error en barra de estado | Navegar a directorio sin permisos | â˜ |
| CA18 | Esc cierra la app | Pulsar Esc desde cualquier nivel | â˜ |
| CA19 | Directorio vacÃ­o: sin selecciÃ³n, preview vacÃ­a | Navegar a directorio vacÃ­o | â˜ |
| CA20 | Cambios reflejados automÃ¡ticamente | Crear/borrar archivo con la app abierta | â˜ |
| CA21 | AdaptaciÃ³n al redimensionar terminal | Cambiar tamaÃ±o de ventana en ejecuciÃ³n | â˜ |
| CA22 | Modo degradado sin colores | Ejecutar con `NO_COLOR=1` | â˜ |
| CA23 | Separadores verticales visibles | Verificar lÃ­neas entre columnas | â˜ |
| CA24 | TamaÃ±o visible por entrada | Sufijos de tamaÃ±o en listas | â˜ |
| CA25 | LÃ­nea de ayuda visible con contador inline `[n/N]` | Verificar que el contador aparece en la misma lÃ­nea (sin salto adicional) | â˜ |
| CA26 | SelecciÃ³n de archivo: columna derecha con contenido, izquierda con contexto | Seleccionar archivo y verificar ambas columnas | â˜ |

### ValidaciÃ³n de suite de tests

| Comando | Resultado esperado |
|---------|-------------------|
| `pytest tests/test_model.py -v` | 3 passed |
| `pytest tests/test_reader.py -v` | â‰¥13 passed |
| `pytest tests/test_navigator.py -v` | 16 passed |
| `pytest tests/test_renderer.py -v` | 10 passed |
| `pytest tests/test_integration.py -v` | 5 passed |
| `pytest --cov=miller --cov-report=term-missing` | Cobertura global â‰¥ 80% |

### ValidaciÃ³n arquitectÃ³nica

| Aspecto | VerificaciÃ³n |
|---------|-------------|
| Sin importaciones cruzadas | `state` no importa de `ui`; `navigation` no importa de `filesystem` directamente |
| Composition root | Solo `__main__.py` instancia y conecta las capas |
| Portabilidad | La app arranca en Windows y Linux/macOS |

---

## Objetivo arquitectÃ³nico

Cerrar formalmente el ciclo de implementaciÃ³n con evidencia objetiva del cumplimiento de requisitos. La validaciÃ³n arquitectÃ³nica final confirma que los principios de diseÃ±o se mantienen en el cÃ³digo entregado.

---

## Criterios de aceptaciÃ³n

| # | Criterio |
|---|---------|
| CA-1 | Los 26 CA funcionales verificados y registrados con resultado |
| CA-2 | Suite completa de tests pasa sin fallos ni errores |
| CA-3 | Cobertura global â‰¥ 80% |
| CA-4 | Sin importaciones cruzadas entre capas |
| CA-5 | Composition root Ãºnico en `__main__.py` |
| CA-6 | App funcional en Windows y Linux/macOS |
| CA-7 | Resultado documentado en `docs/validation-report.md` o en el PR |

---

## Artefactos y entregables

- `docs/validation-report.md` con tabla de resultados (26 casillas marcadas)
- Captura de pantalla o grabaciÃ³n de la app funcionando
- Output de `pytest --cov` con cobertura final

---

## Dependencias

| Tipo | DescripciÃ³n |
|------|-------------|
| **Interna** | SPEC-04-INTEGRACION-MAIN y SPEC-04-INTEGRACION-TESTING completados y pasando |
| **Interna** | Toda la suite de tests unitarios pasando |

---

## Riesgos

| Riesgo | MitigaciÃ³n |
|--------|-----------|
| CA12 y CA17 difÃ­ciles de reproducir en Windows | Validar en Linux; documentar comportamiento esperado en Windows |
| CA22 requiere configuraciÃ³n especial | Usar `NO_COLOR=1` como variable de entorno estÃ¡ndar |
| CA20 y CA21 no automatizables | SesiÃ³n de validaciÃ³n manual dedicada |

---

## Actualizacion OpenSpec 2026-03-27

### Verificaciones adicionales obligatorias

- Confirmar que la cabecera no desaparece en scroll descendente.
- Confirmar que la cabecera no desaparece al recuperar bloques previos con scroll ascendente.
- Confirmar no regresion en comportamiento de `↑`, `↓`, `→`, `←` tras ajustes de layout.

### Evidencia recomendada

- Captura o grabacion corta de navegacion en directorio largo (down/up) mostrando cabecera fija.



