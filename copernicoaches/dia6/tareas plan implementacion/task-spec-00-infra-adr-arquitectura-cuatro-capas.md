# SPEC-00 | INFRA | ADR | ADR-001: Arquitectura de cuatro capas desacopladas

## Metadatos

| Campo | Valor |
|-------|-------|
| **ID** | task-SPEC-00-infra-adr-arquitectura-cuatro-capas |
| **CÃ³digo de plan** | SPEC-00 |
| **Ã‰pica** | INFRA â€” ConfiguraciÃ³n del proyecto y estructura |
| **Feature** | ADR â€” Architecture Decision Records |
| **Tipo** | Tarea de arquitectura |
| **Prioridad** | Alta |
| **EstimaciÃ³n** | 1 h |

---

## DescripciÃ³n tÃ©cnica

Redactar y publicar el **ADR-001** que documenta la decisiÃ³n de adoptar arquitectura de cuatro capas desacopladas. Formato: Markdown siguiendo plantilla MADR.

### Decisiones a documentar

| DecisiÃ³n | JustificaciÃ³n |
|----------|--------------|
| SeparaciÃ³n en 4 capas (`state`, `navigation`, `filesystem`, `ui`) | CohesiÃ³n alta, acoplamiento bajo, testabilidad por capa |
| `pathlib.Path` exclusivamente para rutas | Portabilidad Windows/Linux/macOS sin concatenaciÃ³n de strings |
| `rich` sin Textual para el MVP | Menor complejidad para primera entrega funcional |
| `pytest` como framework de test | EstÃ¡ndar de facto en Python, compatible con `pytest-cov` |
| `dataclass(frozen=True)` para `FileEntry` | Value object inmutable: semÃ¡ntica correcta para entradas del FS |
| Python 3.12 mÃ­nimo | Soporte nativo `match/case`, mejoras en typing |

---

## Objetivo arquitectÃ³nico

Generar trazabilidad de las decisiones de diseÃ±o del arranque del proyecto. Permite que futuros mantenedores entiendan el *por quÃ©* de la estructura, reduciendo probabilidad de regresiones arquitectÃ³nicas.

---

## Criterios de aceptaciÃ³n

| # | Criterio |
|---|---------|
| CA-1 | ADR existe en `docs/adr/ADR-001-arquitectura-cuatro-capas.md` |
| CA-2 | Secciones: Contexto, Opciones consideradas, DecisiÃ³n, Consecuencias |
| CA-3 | Se documentan las 6 decisiones de diseÃ±o de la tabla anterior |
| CA-4 | Estado del ADR: `Aceptado` con fecha de decisiÃ³n |
| CA-5 | Revisado y aprobado por al menos un miembro del equipo |

---

## Artefactos y entregables

- `docs/adr/ADR-001-arquitectura-cuatro-capas.md`

---

## Dependencias

| Tipo | DescripciÃ³n |
|------|-------------|
| **Interna** | SPEC-00-INFRA-SETUP (estructura de proyecto debe existir) |
| **Bloquea** | Cualquier tarea que requiera justificaciÃ³n arquitectÃ³nica en revisiÃ³n de PR |


