# Especificación funcional v3 — Gestor de archivos en consola con Miller Columns

> **Propósito de este documento:** Especificación funcional definitiva con todas las dudas resueltas y decisiones confirmadas. Este documento sustituye a la v2 como referencia de implementación.

---

## 1. Resumen del sistema

Aplicación de consola multiplataforma (Windows, Linux, macOS) que permite navegar el sistema de archivos local mediante el modelo de **Miller Columns** (tres columnas simultáneas), con navegación por teclado mediante flechas de cursor, visualización con colores y actualización dinámica.

- **Columna izquierda** → directorio padre
- **Columna central** → directorio actual (foco)
- **Columna derecha** → contenido del elemento seleccionado

**Tecnologías:** Python 3.12+, Rich para renderizado en consola.

**Compatibilidad:** Windows, Linux y macOS. Se usa `pathlib` para abstracción de rutas.

---

## 2. Historias de usuario

| ID  | Historia |
|-----|----------|
| HU1 | Navegación estructurada: entender en todo momento dónde estoy y qué opciones tengo |
| HU2 | Contexto inmediato: ver simultáneamente padre, actual y destino |
| HU3 | Exploración eficiente: recorrer directorios rápidamente con teclado |
| HU4 | Visibilidad del siguiente paso: ver contenido antes de entrar |
| HU5 | Comprensión del sistema de archivos: entender la jerarquía sin construirla mentalmente |

---

## 3. Comportamiento del sistema

### 3.1 Arranque

- **Directorio inicial:** nivel de unidades de disco disponibles.
  - **Windows:** muestra C:, D:, E:, etc. (todas las unidades presentes)
  - **Linux/macOS:** muestra solo `/` (raíz)
- La columna central muestra las unidades disponibles.
- La columna izquierda está vacía (no hay padre del nivel de unidades).
- La columna derecha muestra el contenido de la unidad seleccionada.
- No se acepta argumento CLI para cambiar el directorio de inicio.

### 3.2 Teclas de navegación

| Tecla | Acción |
|-------|--------|
| `↑` (flecha arriba) | Mover selección al elemento anterior en la columna central |
| `↓` (flecha abajo) | Mover selección al siguiente elemento en la columna central |
| `→` (flecha derecha) | Entrar en el directorio seleccionado |
| `←` (flecha izquierda) | Volver al directorio padre |
| `Esc` | Salir de la aplicación (sin confirmación) |

- No se soportan teclas vim (h/j/k/l).
- No se soporta uso de ratón.

### 3.3 Navegación vertical

- `↑`/`↓` cambian la selección dentro de la columna central.
- La columna derecha se actualiza automáticamente según el elemento seleccionado.
- Si se llega al primer/último elemento, la selección no se mueve más allá.

### 3.4 Entrada en directorio

- `→` sobre un directorio: el elemento seleccionado pasa a ser el directorio actual.
- Las columnas se desplazan:
  - Izquierda ← antiguo directorio actual
  - Centro ← nuevo directorio
  - Derecha ← contenido del nuevo directorio
- `→` sobre un archivo: **no tiene efecto** (no se permite navegar a la derecha).

### 3.5 Retorno al directorio padre

- `←` cambia al directorio padre.
- Las columnas se desplazan:
  - Centro ← antiguo padre
  - Derecha ← antiguo directorio actual
  - Izquierda ← nuevo padre
- La selección se mantiene sobre el directorio desde el que se regresó.
- Al intentar retroceder desde la raíz del sistema: **no ocurre nada** (operación silenciosa).

### 3.6 Salida de la aplicación

- Tecla `Esc`: cierra la aplicación inmediatamente, **sin diálogo de confirmación**.
- `Ctrl+C` se captura desde la capa de input y finaliza la aplicación de forma graceful (salida limpia sin stack trace).

---

## 4. Ordenamiento y filtrado

### 4.1 Orden de elementos

1. **Directorios primero**, luego archivos.
2. Dentro de cada grupo: **orden alfabético** (case-insensitive).

### 4.2 Archivos ocultos

- **No se muestran.**
- En Linux/macOS: archivos que empiezan por `.` (dotfiles).
- En Windows: archivos con atributo `hidden`.
- No existe toggle para mostrar/ocultar. Siempre ocultos.

### 4.3 Enlaces simbólicos

- **No se muestran.** Los enlaces simbólicos se ignoran completamente.
- No aparecen en el listado de ninguna columna.

---

## 5. Visualización

### 5.1 Layout de columnas

- **Tres columnas** con proporción **1:2:2** (izquierda / centro / derecha) usando `ratio` en la tabla Rich.
- Las columnas se **redimensionan dinámicamente** al cambiar el tamaño del terminal.

### 5.2 Truncamiento de nombres

- Los nombres de archivo/directorio que excedan el ancho de la columna se **truncan con `…`** al final.

### 5.3 Scroll en columnas

- **Scroll automático** siguiendo la selección: el elemento seleccionado siempre es visible.
- Se muestran **indicadores visuales** cuando hay más contenido arriba o abajo (ej. `▲` / `▼`).

### 5.4 Adaptación dinámica

- La aplicación se **adapta dinámicamente** al redimensionar el terminal.
- Las columnas se recalculan automáticamente al nuevo tamaño.
- No existe un tamaño mínimo definido; la aplicación se adapta lo mejor posible.

### 5.5 Paleta de colores

| Elemento | Estilo visual |
|----------|--------------|
| Directorio | Azul, negrita |
| Archivo | Blanco/color por defecto |
| Elemento seleccionado | Inversión de color (highlight) |
| Error | Rojo |

- **Terminales sin soporte de color:** la aplicación funciona en modo degradado, usando solo texto plano y marcadores textuales (ej. `>` para selección, `[DIR]` para directorios).

### 5.6 Ruta actual

- Se muestra en una **cabecera superior fija** (región superior del Layout, siempre visible).
- Se muestra la **ruta absoluta** completa.
- Si la ruta excede el ancho del terminal, se **trunca desde la izquierda** con `…` para que el nombre del directorio actual (parte final de la ruta) siempre sea visible.

### 5.7 Columna izquierda (padre/contexto)

- Muestra el contenido del directorio padre (contexto de navegación).
- El directorio actual aparece resaltado dentro de ella.
- **Scroll automático** al elemento resaltado: si el directorio padre contiene muchos elementos, la columna hace scroll para que el directorio actual sea siempre visible.
- A nivel de unidades, sigue el comportamiento de contexto definido para raíz/unidades.

### 5.8 Columna central (actual)

- Muestra el contenido del directorio actual.
- Siempre tiene una selección activa si hay elementos.
- Define el estado de navegación.

### 5.9 Columna derecha (vista previa)

Depende del elemento seleccionado:

| Tipo de elemento | Contenido de la columna derecha |
|------------------|---------------------------------|
| Directorio | Listado de su contenido (hijos) con nombre y tamaño (solo carpetas) |
| Archivo de texto | Nombre del archivo y **contenido completo** |
| Archivo binario | Solo nombre |
| Sin selección | Vacía |

### 5.10 Tamaños visibles y leyenda de teclas

- Solo los **directorios** muestran su tamaño en formato humano (B, KB, MB, GB), en **color gris claro** (`grey70`).
- Los archivos **no muestran tamaño** en las listas de navegación.
- Se muestra una **leyenda fija de teclas** debajo de las columnas: `↑/↓ mover · → entrar · ← volver · Esc salir`.

#### Detección de archivo de texto

- Se determina **por extensión del archivo**. Extensiones reconocidas como texto:
  `.txt`, `.md`, `.py`, `.json`, `.csv`, `.xml`, `.html`, `.css`, `.js`, `.ts`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.conf`, `.log`, `.sh`, `.bat`, `.ps1`, `.sql`, `.java`, `.c`, `.cpp`, `.h`, `.rs`, `.go`, `.rb`, `.php`
- Cualquier otra extensión se trata como binario.

#### Encoding

- Se asume **UTF-8** para la lectura de archivos de texto.
- Si la lectura falla por encoding, se trata como archivo binario (solo nombre).

---

## 6. Errores y robustez

### 6.1 Errores de acceso

- Si un directorio o archivo no es accesible (permisos, etc.), se muestra un mensaje en la **barra de estado** (parte inferior de la pantalla).
- Texto del mensaje: **"Error"** (seguido de contexto breve si es posible, ej. "Error: acceso denegado").
- El mensaje **no se autocierra**: permanece visible hasta que el usuario navega a otro elemento o realiza otra acción.
- La aplicación **no se detiene**; continúa operativa.

### 6.2 Directorios grandes

- Se cargan **todos los elementos** del directorio, sin límite ni paginación.
- No se implementa carga diferida.

### 6.3 Cambios externos en el filesystem

- La aplicación implementa **detección automática** de cambios en el sistema de archivos.
- Cuando se detectan cambios, las columnas se actualizan automáticamente.

### 6.4 Caracteres especiales en nombres

- Los nombres con caracteres Unicode, espacios u otros caracteres especiales se **muestran tal cual**, sin escapado ni transformación (salvo el truncamiento por ancho de columna).

### 6.5 Estabilidad visual en terminal

- El bucle principal usa **pantalla alternativa del terminal** para evitar acumulación visual y mantener una experiencia tipo TUI.
- Cada frame se renderiza con limpieza completa de pantalla y reposicionamiento al inicio (`clear(home=True)`).
- Al salir (Esc o Ctrl+C), el terminal vuelve al buffer principal sin ensuciar el historial de salida de comandos.

---

## 7. Fuera de alcance (MVP)

- Operaciones de modificación (copiar, borrar, mover, renombrar).
- Integración con sistemas externos.
- Interfaces gráficas (GUI).
- Renderizado avanzado (imágenes, PDFs).
- Navegación dentro de archivos.
- Layouts dinámicos o configurables.
- Uso de ratón.
- Múltiples paneles simultáneos.
- Plugins.
- Toggle de archivos ocultos.
- Visualización de enlaces simbólicos.
- Argumento CLI para directorio de inicio.

---

## 8. Criterios de aceptación

| # | Criterio | Validación |
|---|----------|------------|
| CA01 | La aplicación arranca mostrando tres columnas con el contenido de `C:\` (o `/` en Linux/macOS) | Verificar visualmente al arrancar |
| CA02 | `↑`/`↓` cambian la selección en la columna central y actualizan la columna derecha | Navegar por un directorio con varios elementos |
| CA03 | `→` sobre un directorio entra en él, desplazando las columnas | Entrar en al menos 3 niveles de profundidad |
| CA04 | `→` sobre un archivo no tiene efecto | Seleccionar archivo y pulsar `→` |
| CA05 | `←` vuelve al padre manteniendo la selección previa | Entrar y salir de un directorio |
| CA06 | `←` en la raíz no hace nada | Pulsar `←` estando en `C:\` |
| CA07 | Directorios y archivos se distinguen visualmente (color/estilo) | Verificar directorio en directorio con ambos tipos |
| CA08 | El elemento seleccionado es claramente identificable (highlight) | Verificar inversión de color |
| CA09 | La ruta absoluta se muestra en cabecera superior | Verificar al navegar |
| CA10 | Directorios primero, orden alfabético case-insensitive | Verificar en directorio con mezcla |
| CA11 | Archivos ocultos no se muestran | Verificar en directorio con dotfiles/hidden |
| CA12 | Enlaces simbólicos no se muestran | Verificar en directorio con symlinks |
| CA13 | Nombres largos se truncan con `…` | Crear/buscar archivo con nombre largo |
| CA14 | Scroll automático con indicadores `▲`/`▼` en directorios grandes | Navegar en directorio con muchos elementos |
| CA15 | Archivo de texto seleccionado muestra contenido completo en columna derecha | Seleccionar archivo `.txt` o `.py` |
| CA16 | Archivo binario seleccionado muestra solo su nombre | Seleccionar archivo `.exe` o `.zip` |
| CA17 | Error de acceso muestra "Error" en barra de estado sin cerrar la app | Navegar a directorio sin permisos |
| CA18 | `Esc` o `Ctrl+C` cierran la aplicación inmediatamente | Pulsar `Esc` y `Ctrl+C` |
| CA19 | Directorio vacío: columna central vacía, sin selección, columna derecha vacía | Navegar a directorio vacío |
| CA20 | Cambios en filesystem se reflejan automáticamente | Crear/borrar archivo mientras la app está abierta |
| CA21 | La app se adapta al redimensionar el terminal | Cambiar tamaño de ventana del terminal |
| CA22 | Funciona en terminal sin colores (modo degradado) | Ejecutar en terminal sin soporte de color |
| CA23 | La interfaz muestra separadores verticales entre columnas | Verificar líneas verticales en render normal |
| CA24 | Solo los directorios muestran tamaño en gris claro | Verificar sufijos de tamaño en carpetas, ausencia en archivos |
| CA26 | Al seleccionar archivo de texto, la columna derecha muestra contenido completo y la izquierda mantiene contexto de padre | Seleccionar archivo de texto y verificar ambas columnas |
| CA25 | Se muestra leyenda de teclas en pantalla principal | Verificar línea de ayuda bajo las columnas |

---

## 9. Modelo de estado

El sistema mantiene en todo momento:

| Campo | Descripción |
|-------|-------------|
| `current_dir` | Directorio actual (ruta absoluta) |
| `parent_dir` | Directorio padre (o `None` si es raíz) |
| `selected_index` | Índice del elemento seleccionado en la columna central |
| `current_contents` | Lista ordenada de elementos del directorio actual |
| `preview_target` | Elemento seleccionado (para columna derecha) |

Las columnas son **vistas derivadas** de este estado.

---

## 10. Arquitectura (resumen)

Cuatro capas desacopladas:

| Capa | Responsabilidad |
|------|-----------------|
| **Estado (modelo)** | Única fuente de verdad: directorio actual, selección, contenido |
| **Lógica de navegación** | Gestiona eventos de teclado, actualiza estado, controla transiciones |
| **Sistema de archivos** | Lee directorios, obtiene metadatos, detecta cambios, maneja errores |
| **Visualización** | Renderiza estado en consola con Rich. No modifica estado |

> **Regla:** El sistema debe funcionar correctamente sin la capa de visualización; la visualización es una proyección del estado, no su motor.

---

## 11. Registro de decisiones (resolución de dudas v2)

| Duda | Decisión | Justificación |
|------|----------|---------------|
| D01 — Teclas | Flechas de cursor únicamente | Estándar universal, sin curva de aprendizaje |
| D02 — Directorio inicial | Raíz de C:\ (o / en *nix) | Punto de partida fijo y predecible |
| D03 — Ordenamiento | Directorios primero, alfabético case-insensitive | Convención habitual en gestores de archivos |
| D04 — Archivos ocultos | No se muestran, sin toggle | Simplifica MVP, evita ruido visual |
| D05 — Symlinks | No se muestran | Evita complejidad de links rotos y ciclos |
| D06 — Ancho columnas | Proporción 1:2:2 dinámica (ratio), truncamiento con `…` | Redimensionado dinámico al cambiar tamaño del terminal |
| D07 — Scroll | Automático + indicadores ▲/▼ | Visibilidad completa sin perder contexto |
| D08 — Terminal | Adaptación dinámica al redimensionar | Experiencia fluida sin restricciones |
| D09 — Dirs grandes | Se cargan todos | Sin paginación; simplicidad para MVP |
| D10 — Colores | Azul/negrita dirs, highlight selección, modo degradado sin color | Accesibilidad en cualquier terminal |
| D11 — Ruta | Cabecera superior, ruta absoluta | Máxima claridad de ubicación |
| D12 — Vista previa | Contenido completo en columna derecha para archivos de texto, UTF-8, binarios solo nombre+tamaño | Mayor utilidad en lectura de archivos |
| D13 — Comportamiento izquierda | Columna izquierda mantiene contexto de padre | Conserva orientación de navegación Miller |
| D14 — Errores | Barra de estado, texto "Error", no se autocierra | Error visible sin bloquear navegación |
| D15 — Plataforma | Windows + Linux + macOS | Compatibilidad total con pathlib |
| D16 — Salida | Esc sin confirmación | Salida rápida y directa |
| D17 — Cambios externos | Detección automática | Contenido siempre actualizado |
| D18 — Caracteres especiales | Se muestran tal cual | Sin transformación, máxima fidelidad |

---

## 12. Estado de implementación

### ✅ Implementación completada (23 de marzo de 2026)

| Componente | Estado | Pruebas |
|------------|--------|---------|
| **Modelo de estado** (FileEntry, AppState) | ✅ Completado | 6 tests pasados |
| **Lector del sistema de archivos** (list_directory, preview, hidden detection) | ✅ Completado | 18 tests pasados |
| **Navegador** (move_up/down, enter, parent, refresh) | ✅ Completado | 27 tests pasados |
| **Renderizador Rich** (3 columnas, header, separadores, scroll, style) | ✅ Completado | 10 tests pasados |
| **Manejador de entrada** (input_handler, lectura de teclado) | ✅ Completado | Integrado en tests |
| **Loop principal** (composición, despacho de eventos, Ctrl+C) | ✅ Completado | 5 tests integración |
| **Pantalla limpia + pantalla alternativa** (clear(home) + screen buffer alternativo) | ✅ Completado | Validado en tests |
| **Visualización de tamaño por entrada** (archivo/directorio) | ✅ Completado | Validado en tests de render/integración |
| **Leyenda de teclas en UI** | ✅ Completado | Validado visualmente |

### Resultados de pruebas (24 de marzo de 2026)
- **Total de tests:** 67
- **Pasados:** 65 ✅
- **Omitidos:** 2 (limitaciones de Windows: symlinks y permisos)
- **Fallos:** 0
- **Cobertura:** Todas las capas (modelo, filesystem, navegación, UI, integración)
- **5 iteraciones** de corrección y mejora completadas

### Correcciones aplicadas
- **Fix renderer:** `box.VERTICAL` (inexistente en Rich) → `box.SQUARE` (separadores verticales `│` visibles entre columnas)
- **Fix renderizado con Layout:** Refactorización del renderer usando `rich.layout.Layout` para garantizar regiones fijas:
  - **Cabecera siempre visible:** La ruta absoluta se muestra en una región fija de 1 línea en la parte superior, garantizada por Layout (no se desplaza nunca). Rutas largas se truncan desde la izquierda con `…` para mantener visible el nombre del directorio actual.
  - **Scroll en columna izquierda:** La columna izquierda ahora hace scroll automático al elemento resaltado (directorio actual dentro de su padre), igual que la columna central.
  - **Mayor espacio para contenido:** El cálculo de `list_height` pasa de `height - 8` a `height - footer - 3`, aprovechando mejor el espacio disponible del terminal para mostrar más contenido de archivos en la columna derecha.
  - **Footer fijo:** La leyenda de teclas y mensajes de error se muestran en una región fija inferior, siempre visible.

### Validación de Criterios de Aceptación
- **18/26 criterios** validados por tests automatizados ✅
- **8/26 criterios** listos para validación manual:
  - CA12 (enlaces simbólicos) — código implementado
  - CA17 (errores de permiso) — código implementado
  - CA21 (redimensionamiento de terminal) — código implementado
  - CA22 (modo sin color) — código implementado
  - CA23 (separadores verticales) — código implementado
  - CA24 (tamaño visible por entrada) — código implementado
  - CA25 (leyenda de teclas) — código implementado
  - CA26 (contenido completo en derecha + contexto en izquierda) — código implementado

### Bugs resueltos post-implementación (Iteración 2)
1. ✅ **Pantalla acumulada** — Agregado `console.clear()` en cada render
2. ✅ **Escape en Unix** — Corregida `_read_key_unix()` para retornar "escape"
3. ✅ **Sistema de unidades** — Implementada navegación desde nivel de unidades
4. ✅ **Unidad no resaltada** — Corregida comparación usando `.drive`
5. ✅ **Columna derecha sin estilos** — Aplicados estilos de color a directorios en preview

### Mejoras funcionales adicionales (Iteración 3)
1. ✅ **Historial visible al hacer scroll** — Bucle en pantalla alternativa para evitar acumulación visual
2. ✅ **Separación visual de columnas** — Agregadas líneas verticales entre paneles
3. ✅ **Tamaño por entrada** — Render de tamaño humano para archivos y directorios
4. ✅ **Leyenda de teclado** — Línea de ayuda visible en la interfaz principal

### Correcciones de visualización (Iteración 4)
1. ✅ **Cabecera no visible** — Refactorización a `rich.layout.Layout` con regiones fijas (header, body, footer) que garantizan visibilidad permanente
2. ✅ **Scroll en columna izquierda** — La columna padre ahora hace scroll automático al directorio resaltado
3. ✅ **Contenido de archivo íntegro** — Mayor espacio para contenido (cálculo optimizado de `list_height`) con indicadores de scroll

### Correcciones de visualización (Iteración 5)
1. ✅ **Redimensionado dinámico** — Columnas de la tabla cambiadas de `width` fijo a `ratio` (1:2:2), se adaptan automáticamente al crecer/reducir la ventana del terminal
2. ✅ **Tamaño solo en carpetas** — El tamaño en formato humano ahora solo se muestra junto a directorios, en color gris claro (`grey70`). Los archivos no muestran tamaño en las listas de navegación ni en la cabecera de vista previa

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

### Archivos generados
- `explorer/src/miller/` — módulo principal (4 capas)
- `explorer/tests/` — suite de pruebas (67 tests)
- `explorer/pyproject.toml` — configuración del proyecto
- `explorer/README.md` — documentación de usuario

---

## Anexo: Trazabilidad

| Documento fuente | Contenido utilizado |
|------------------|-------------------|
| Especificación funcional original (v1) | Historias de usuario, reglas de navegación, casos límite, alcance |
| Especificación funcional v2 | Dudas abiertas e hipótesis identificadas |
| Guía de arquitectura | Capas, tecnologías, principios de desacoplamiento |
| Capacidades - objetivos y entrega | Contexto del ejercicio, capacidades esperadas |
| Respuestas del usuario (D01–D18) | Resolución de todas las dudas abiertas |
| Plan de implementación (5 pasos) | Ejecución de architecture en 4 fases iterativas |
