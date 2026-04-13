## Context

La aplicación de consola renderiza entradas de sistema de archivos en columnas, pero actualmente no comunica el tipo de entrada mediante un marcador visual dedicado. El cambio es local al render de items y no afecta al flujo de navegación ni al modelo de datos.

## Goals / Non-Goals

**Goals:**
- Añadir marcador visual consistente para directorios y para archivos.
- Mantener compatibilidad con el layout y controles actuales.
- Evitar regresiones en navegación y selección.

**Non-Goals:**
- Soporte de iconos por extensión de archivo.
- Tematización avanzada o configuración de iconos por usuario.
- Cambios de arquitectura o nuevas dependencias de icon packs.

## Decisions

- Usar iconos Unicode simples para carpeta y fichero en el prefijo de cada item renderizado.
  - Rationale: implementación mínima, portable y sin dependencias nuevas.
  - Alternative considered: iconos coloreados/temáticos por Rich markup; se pospone para reducir alcance.
- Resolver tipo de entrada desde metadatos ya disponibles en el item (is_dir/path), sin consultas extra de filesystem en render.
  - Rationale: evita coste adicional por frame.
  - Alternative considered: recalcular tipo en tiempo de render; descartado por ineficiencia y acoplamiento.
- Mantener un único punto de formateo de etiqueta por item.
  - Rationale: facilita pruebas y evita divergencias entre columnas.

## Risks / Trade-offs

- [Riesgo] Fuentes/terminales que muestren Unicode con ancho irregular → Mitigación: mantener prefijo corto y validar alineación en Windows Terminal/PowerShell.
- [Riesgo] Tests de texto exacto pueden fallar por nuevo prefijo → Mitigación: actualizar expectativas de render y cubrir ambos tipos de entrada.
- [Trade-off] Iconos fijos sin configuración inicial → Mitigación: dejar extensión futura documentada, fuera de este cambio.

## Migration Plan

- No requiere migración de datos ni despliegue especial.
- Aplicar cambio de render y ajustar pruebas asociadas.
- Rollback: revertir formateo de etiqueta de item al estado previo.

## Open Questions

- ¿Iconos definitivos: 📁/📄 o alternativa ASCII (`[D]`/`[F]`) para terminales limitadas?
- ¿Debe mostrarse icono también en breadcrumbs o solo en listas de columnas?
