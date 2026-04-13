## Context

La aplicación Miller Columns en consola muestra contenido por columnas y permite navegar por carpetas, pero actualmente no expone de forma destacada la ruta absoluta activa y el tamaño de carpetas puede no representar correctamente su contenido total. Se requiere mejorar ambos comportamientos sin alterar atajos ni flujo de navegación.

## Goals / Non-Goals

**Goals:**
- Mostrar una cabecera estable con la ruta completa activa encima de la tabla.
- Calcular tamaño de carpeta con criterio único y predecible (agregado de contenidos).
- Mantener la UI responsiva y resiliente ante errores de permisos o rutas inaccesibles.

**Non-Goals:**
- Cambiar keybindings o flujo de navegación.
- Añadir nuevas vistas, filtros o configuración avanzada de formato.
- Implementar cache persistente de tamaños fuera del ciclo de render actual.

## Decisions

1. **Ruta completa desde estado de navegación**
   - La cabecera se alimenta del path activo ya mantenido por el estado de navegación, evitando duplicar fuentes de verdad.
   - Alternativa descartada: reconstruir ruta desde columnas visibles en cada render; añade complejidad innecesaria.

2. **Tamaño de carpeta como suma recursiva de archivos descendientes**
   - Se define el tamaño de carpeta como suma de tamaños de ficheros contenidos (directos e indirectos), omitiendo entradas no accesibles.
   - Alternativa descartada: usar tamaño del inode/directorio (no representa contenido real para usuario).

3. **Manejo de errores no bloqueante**
   - Errores de lectura/permisos durante el cálculo se gestionan de forma tolerante y se continúa con el resto.
   - Alternativa descartada: propagar excepción al render, porque rompe experiencia de navegación.

## Risks / Trade-offs

- [Costo de cómputo en árboles grandes] → Mitigar limitando recálculo al contexto necesario y reutilizando resultados temporales por ciclo de render.
- [Resultados parciales por permisos denegados] → Mitigar documentando que el tamaño puede excluir nodos inaccesibles.
- [Anchura de terminal insuficiente para rutas largas] → Mitigar con truncado visual conservando la ruta completa internamente.

## Migration Plan

- No requiere migración de datos ni cambios de configuración.
- Despliegue directo con validación manual de navegación y tests de tamaño.
- Rollback: revertir cambio en render de cabecera y función de tamaño de carpeta.

## Open Questions

- ¿El formato de tamaño esperado es bytes crudos o human-readable en todas las vistas?
- ¿Debe aplicarse límite de profundidad configurable para cálculo en carpetas extremadamente grandes?