# Backlog de implementación — Miller Columns

## Nomenclatura de tareas

```
task-step-{xx}-{epica}-{feature}-{titulo-tarea}.md
```

| Segmento | Descripción | Ejemplo |
|----------|-------------|---------|
| `task-step-xx` | Código del paso del plan de implementación | `task-step-02` |
| `epica` | Agrupación temática de alto nivel | `navegacion` |
| `feature` | Sub-funcionalidad dentro de la épica | `navigator` |
| `titulo-tarea` | Descripción corta de la tarea | `clase-navigator` |

---

## Índice por épica

### STEP-00 — INFRA (Configuración del proyecto y estructura)

| Archivo | Feature | Estimación |
|---------|---------|-----------|
| [task-step-00-infra-setup-crear-pyproject-y-estructura.md](task-step-00-infra-setup-crear-pyproject-y-estructura.md) | SETUP | 2 h |
| [task-step-00-infra-adr-arquitectura-cuatro-capas.md](task-step-00-infra-adr-arquitectura-cuatro-capas.md) | ADR | 1 h |
| [task-step-00-infra-verificacion-instalacion-y-arranque.md](task-step-00-infra-verificacion-instalacion-y-arranque.md) | VERIFICACION | 1 h |

**Subtotal: 4 h**

---

### STEP-01 — DOMINIO (Modelo de estado y capa de sistema de archivos)

| Archivo | Feature | Estimación |
|---------|---------|-----------|
| [task-step-01-dominio-modelo-fileentry-y-appstate.md](task-step-01-dominio-modelo-fileentry-y-appstate.md) | MODELO | 2 h |
| [task-step-01-dominio-filesystem-reader-funciones.md](task-step-01-dominio-filesystem-reader-funciones.md) | FILESYSTEM | 4 h |
| [task-step-01-dominio-testing-tests-unitarios-modelo-filesystem.md](task-step-01-dominio-testing-tests-unitarios-modelo-filesystem.md) | TESTING | 3 h |

**Subtotal: 9 h**

---

### STEP-02 — NAVEGACION (Lógica de navegación)

| Archivo | Feature | Estimación |
|---------|---------|-----------|
| [task-step-02-navegacion-navigator-clase-navigator.md](task-step-02-navegacion-navigator-clase-navigator.md) | NAVIGATOR | 5 h |
| [task-step-02-navegacion-input-input-handler-multiplataforma.md](task-step-02-navegacion-input-input-handler-multiplataforma.md) | INPUT | 3 h |
| [task-step-02-navegacion-testing-tests-unitarios-navegacion.md](task-step-02-navegacion-testing-tests-unitarios-navegacion.md) | TESTING | 4 h |

**Subtotal: 12 h**

---

### STEP-03 — VISUALIZACION (Visualización con Rich)

| Archivo | Feature | Estimación |
|---------|---------|-----------|
| [task-step-03-visualizacion-renderer-renderizador-principal.md](task-step-03-visualizacion-renderer-renderizador-principal.md) | RENDERER | 6 h |
| [task-step-03-visualizacion-scroll-scroll-y-truncamiento.md](task-step-03-visualizacion-scroll-scroll-y-truncamiento.md) | SCROLL | 3 h |
| [task-step-03-visualizacion-testing-tests-renderizador.md](task-step-03-visualizacion-testing-tests-renderizador.md) | TESTING | 3 h |

**Subtotal: 12 h**

---

### STEP-04 — INTEGRACION (Integración, bucle principal y validación final)

| Archivo | Feature | Estimación |
|---------|---------|-----------|
| [task-step-04-integracion-main-bucle-principal-composition-root.md](task-step-04-integracion-main-bucle-principal-composition-root.md) | MAIN | 4 h |
| [task-step-04-integracion-testing-tests-integracion.md](task-step-04-integracion-testing-tests-integracion.md) | TESTING | 4 h |
| [task-step-04-integracion-validacion-criterios-aceptacion-ca01-ca26.md](task-step-04-integracion-validacion-criterios-aceptacion-ca01-ca26.md) | VALIDACION | 3 h |

**Subtotal: 11 h**

---

## Resumen de estimaciones

| Épica | Tareas | Horas |
|-------|--------|-------|
| INFRA | 3 | 4 h |
| DOMINIO | 3 | 9 h |
| NAVEGACION | 3 | 12 h |
| VISUALIZACION | 3 | 12 h |
| INTEGRACION | 3 | 11 h |
| **TOTAL** | **15** | **48 h** |

---

## Actualizacion OpenSpec (27-03-2026)

Se incorpora en STEP-03 y STEP-04 el ajuste de especificacion para:

- Cabecera de ruta fija y siempre visible durante scroll vertical.
- Region desplazable limitada al cuerpo de columnas.
- Scroll por bloques dinamicos visibles en navegacion descendente/ascendente.
- Verificacion explicita de no regresion de navegacion con flechas.

---

## ✅ PROYECTO COMPLETADO (27 de marzo de 2026)

### Estado final de ejecución

**Todas las tareas completadas exitosamente**

| Métrica | Resultado |
|---------|-----------|
| **Total tareas planificadas** | 15 |
| **Tareas completadas** | 15 ✅ |
| **Tests totales** | 77 |
| **Tests pasados** | 75 ✅ |
| **Tests omitidos** | 2 (limitaciones Windows) |
| **Fallos** | 0 |
| **Criterios de aceptación (CA)** | 26 (23 automatizados, 3 para validación manual) |
| **Criterios validados** | 23 ✅ + 3 listos |
| **Tiempo estimado** | 48 h |

### Entregables

✅ **Especificación funcional v3** — Documento completo con decisiones y requisitos  
✅ **Guía de arquitectura** — Diseño de 4 capas desacopladas  
✅ **Plan de implementación** — 5 pasos detallados (STEP-00 a STEP-04)  
✅ **Suite de pruebas** — 77 tests automatizados con cobertura de capas  
✅ **Código ejecutable** — Aplicación Miller Columns funcional en `explorer/src/miller/`  
✅ **OpenSpec change archivado** — `2026-03-27-inline-selection-counter-and-navigation-help` con delta specs sincronizadas  

### Características implementadas

✅ Navegación Miller Columns (3 columnas: padre, actual, preview)  
✅ Control con teclado (↑ ↓ → ← Esc Ctrl+C)  
✅ Inicio desde nivel de unidades de disco  
✅ Estilos Rich (colores, highlight, truncamiento, scroll indicators)  
✅ Cabecera de ruta fija durante scroll vertical  
✅ Detección automática de cambios en filesystem  
✅ Modo degradado sin colores (accesibilidad)  
✅ Multiplataforma (Windows, Linux, macOS)  
✅ Pantalla alternativa (sin acumulación visual)  
✅ Manejo robusto de errores  
✅ Línea de ayuda con contador inline `[n/N]` (sin salto de línea)  

### Iteraciones de desarrollo

1. ✅ Setup y arquitectura (23-03-2026)
2. ✅ Modelo y filesystem (23-03-2026)
3. ✅ Navegación e input (23-03-2026)
4. ✅ Visualización con Rich (23-24-03-2026)
5. ✅ Integración y validación (24-03-2026)
6. ✅ Correcciones (25-26-03-2026)
7. ✅ OpenSpec y formalización (27-03-2026)

### Cómo usar

```powershell
cd c:\cursos\desarrollo-ia\copernicoaches\explorer
python -m miller
```

**Navegación:**
- `↑`/`↓` — mover selección  
- `→` — entrar en directorio  
- `←` — volver al padre  
- `Esc` — salir  
- `Ctrl+C` — salida forzada limpia
