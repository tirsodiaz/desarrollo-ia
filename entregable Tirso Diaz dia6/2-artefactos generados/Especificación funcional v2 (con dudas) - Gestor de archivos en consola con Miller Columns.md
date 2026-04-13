# Especificación funcional v2 — Gestor de archivos en consola con Miller Columns

> **Propósito de este documento:** Consolidar la especificación funcional original, identificar dudas abiertas y definir hipótesis que deben validarse antes o durante la implementación.

---

## 1. Resumen del sistema

Aplicación de consola que permite navegar el sistema de archivos local mediante el modelo de **Miller Columns** (tres columnas simultáneas), con navegación por teclado, visualización con colores y actualización dinámica.

- **Columna izquierda** → directorio padre
- **Columna central** → directorio actual (foco)
- **Columna derecha** → contenido del elemento seleccionado

**Tecnologías:** Python 3.12+, Rich para renderizado en consola.

---

## 2. Historias de usuario (heredadas)

| ID  | Historia |
|-----|----------|
| HU1 | Navegación estructurada: entender en todo momento dónde estoy y qué opciones tengo |
| HU2 | Contexto inmediato: ver simultáneamente padre, actual y destino |
| HU3 | Exploración eficiente: recorrer directorios rápidamente con teclado |
| HU4 | Visibilidad del siguiente paso: ver contenido antes de entrar |
| HU5 | Comprensión del sistema de archivos: entender la jerarquía sin construirla mentalmente |

---

## 3. Comportamiento definido (validado)

### 3.1 Inicio
- Directorio inicial: directorio actual del sistema (por defecto).
- Columna central muestra contenido del directorio inicial.
- Columna izquierda muestra contenido del directorio padre.
- Columna derecha muestra contenido del primer elemento seleccionado.
- Si el directorio está vacío: no hay selección, columna derecha vacía.

### 3.2 Navegación vertical
- Movimiento arriba/abajo dentro de la columna central.
- Columna derecha se actualiza automáticamente según el elemento seleccionado.

### 3.3 Entrada en directorio
- El directorio seleccionado pasa a ser el directorio actual.
- Las columnas se desplazan hacia la izquierda.

### 3.4 Retorno al padre
- El padre pasa a ser el directorio actual.
- Las columnas se desplazan hacia la derecha.
- La selección se mantiene sobre el directorio desde el que se regresó.

### 3.5 Columna derecha
- Directorio → muestra hijos.
- Archivo → muestra nombre, tipo, tamaño (y opcionalmente primeras líneas si es texto).
- Sin selección → vacía.

### 3.6 Casos límite definidos
- Directorio vacío: columna central muestra estado vacío, sin selección.
- Archivo seleccionado: no se permite navegar a la derecha.
- Directorio raíz: no existe columna izquierda operativa.
- Errores de acceso: se muestra indicador de error, el sistema continúa operativo.

### 3.7 Fuera de alcance (MVP)
- Operaciones de modificación (copiar, borrar, mover).
- Integración con sistemas externos.
- Interfaces gráficas (GUI).
- Renderizado avanzado (imágenes, PDFs).
- Navegación dentro de archivos.
- Layouts dinámicos o configurables.
- Uso de ratón.
- Múltiples paneles simultáneos.
- Plugins.

---

## 4. Dudas abiertas

Las siguientes cuestiones no están resueltas en la documentación actual y requieren decisión:

### D01 — Teclas de navegación
La especificación indica "navegación por teclado" pero **no define las teclas concretas**.
- ¿Flechas de cursor (↑↓←→)?
- ¿Teclas vim (h/j/k/l)?
- ¿Ambas simultáneamente?
- ¿Tecla para salir de la aplicación? (q, Esc, Ctrl+C?)

### D02 — Directorio inicial configurable
Se indica "por defecto: directorio actual del sistema".
- ¿Se acepta un argumento de línea de comandos para especificar otro directorio de inicio?
- Si el argumento es inválido, ¿qué ocurre?

### D03 — Ordenamiento de elementos
No se especifica el criterio de ordenamiento dentro de cada columna.
- ¿Alfabético?
- ¿Directorios primero, luego archivos?
- ¿Case-sensitive o case-insensitive?
- ¿Se respeta alguna convención del sistema operativo?

### D04 — Archivos ocultos
No se menciona el tratamiento de archivos ocultos (dotfiles en Linux/macOS, atributo hidden en Windows).
- ¿Se muestran por defecto?
- ¿Existe un toggle para mostrar/ocultar?

### D05 — Enlaces simbólicos (symlinks)
No se menciona cómo tratar enlaces simbólicos.
- ¿Se siguen (se navega al destino)?
- ¿Se muestran con un indicador visual diferente?
- ¿Qué ocurre si el enlace está roto?

### D06 — Ancho de columnas
Se indica "ancho consistente por columna" pero no se define cómo calcularlo.
- ¿Ancho fijo (ej. 1/3 del terminal)?
- ¿Proporcional o adaptativo?
- ¿Qué ocurre con nombres de archivo muy largos? ¿Truncamiento con ellipsis?

### D07 — Scroll dentro de columnas
Si un directorio tiene más elementos de los que caben en la altura del terminal:
- ¿Scroll automático siguiendo la selección?
- ¿Se muestran indicadores de que hay más contenido arriba/abajo?

### D08 — Tamaño mínimo de terminal
- ¿Existe un tamaño mínimo de terminal soportado?
- ¿Qué ocurre si el terminal es demasiado pequeño para tres columnas?
- ¿Se adapta dinámicamente al redimensionar?

### D09 — Rendimiento con directorios grandes
- ¿Qué ocurre con directorios que contienen miles de archivos?
- ¿Se implementa algún tipo de carga diferida o paginación?
- ¿Existe un límite máximo de elementos mostrados?

### D10 — Paleta de colores
Se indica "uso de colores para selección y tipo de elemento" pero no se definen.
- ¿Qué colores concretos para directorios, archivos, selección?
- ¿Se consideran terminales sin soporte de color?
- ¿Se diferencian visualmente tipos de archivo (ejecutables, texto, etc.)?

### D11 — Ubicación de la ruta actual
Se indica "visualización de la ruta actual (por ejemplo, en cabecera o barra de estado)".
- ¿Cabecera superior, barra inferior, o ambas?
- ¿Se muestra la ruta absoluta o relativa al directorio de inicio?

### D12 — Vista previa de archivos
"Opcional: primeras líneas si es texto".
- ¿Cuántas líneas máximo de vista previa?
- ¿Cómo se determina si un archivo es "texto"? ¿Por extensión, por contenido?
- ¿Qué encoding se asume? ¿Qué ocurre con archivos binarios?
- ¿Qué metadatos exactos se muestran para archivos no texto? (nombre, tipo, tamaño — ¿formato del tamaño? KB, MB?)

### D13 — Columna izquierda en la raíz
"No existe columna izquierda operativa".
- ¿Se muestra vacía?
- ¿Se oculta y se redistribuye el espacio?
- ¿Se muestra un mensaje tipo "raíz del sistema"?

### D14 — Indicador de errores de acceso
"Se muestra un indicador de error".
- ¿Dónde se muestra? ¿En la columna derecha, en una barra de estado, como overlay?
- ¿Qué texto? ¿"Acceso denegado", "Error de lectura"?
- ¿Se autocierra o requiere interacción?

### D15 — Compatibilidad multiplataforma
- ¿El sistema debe funcionar en Windows, Linux y macOS?
- ¿O solo en un sistema operativo específico?
- Rutas (separadores `/` vs `\`), raíz (`/` vs `C:\`), permisos: ¿se abstrae?

### D16 — Salida de la aplicación
No se define cómo el usuario cierra la aplicación.
- ¿Tecla específica (q, Esc)?
- ¿Ctrl+C con manejo graceful?
- ¿Confirmación antes de salir?

### D17 — Actualización ante cambios externos
Si el sistema de archivos cambia mientras la aplicación está abierta:
- ¿Se detectan cambios automáticamente?
- ¿Se requiere acción manual para refrescar (tecla F5 o similar)?
- ¿O se asume que el sistema de archivos es estático durante la sesión?

### D18 — Caracteres especiales en nombres
- ¿Cómo se manejan nombres con caracteres Unicode, espacios, o caracteres especiales?
- ¿Se truncan, escapan o muestran tal cual?

---

## 5. Hipótesis a validar

Las siguientes hipótesis son asunciones razonables derivadas de la documentación existente. **Deben confirmarse o descartarse antes de implementar.**

### Navegación

| ID | Hipótesis | Riesgo si es incorrecta |
|----|-----------|------------------------|
| H01 | Las teclas de navegación son las flechas de cursor (↑↓←→) como mapping principal | Confusión del usuario, retrabajo en la capa de input |
| H02 | La tecla `q` cierra la aplicación sin confirmación | Cierre accidental, o falta de mecanismo de salida |
| H03 | El directorio inicial se puede pasar como argumento CLI; si no se pasa, se usa `cwd` | Rigidez en el arranque si solo sirve `cwd` |
| H04 | Al intentar retroceder desde la raíz del sistema, no ocurre nada (operación silenciosa) | Comportamiento inesperado si no hay feedback |

### Ordenamiento y filtrado

| ID | Hipótesis | Riesgo si es incorrecta |
|----|-----------|------------------------|
| H05 | Los elementos se ordenan: directorios primero, luego archivos, ambos en orden alfabético case-insensitive | Orden confuso o inconsistente |
| H06 | Los archivos ocultos (dotfiles / atributo hidden) **no se muestran** por defecto en el MVP | Se muestran archivos que el usuario no espera ver, o se ocultan archivos necesarios |
| H07 | Los enlaces simbólicos se muestran como su tipo destino (directorio o archivo) sin indicador especial en el MVP | Navegación confusa si un symlink apunta a un destino inválido |

### Visualización

| ID | Hipótesis | Riesgo si es incorrecta |
|----|-----------|------------------------|
| H08 | Cada columna ocupa 1/3 del ancho disponible del terminal | Layout roto en terminales estrechos |
| H09 | Los nombres largos se truncan con `…` al límite de la columna | Nombres ilegibles o desbordamiento visual |
| H10 | La ruta actual se muestra en una cabecera superior (encima de las columnas) | Falta de contexto si se ubica en otro sitio |
| H11 | Scroll vertical dentro de columnas: se mantiene el ítem seleccionado visible, desplazando la lista | El usuario pierde visibilidad del elemento seleccionado |
| H12 | Se usan los colores por defecto de Rich para diferenciar directorios (azul/negrita) de archivos (blanco/normal), con selección resaltada (inversión de color) | Colores ilegibles en ciertos temas de terminal |
| H13 | El terminal mínimo soportado es 80×24 caracteres | La app se rompe en terminales más pequeños |

### Vista previa de archivos

| ID | Hipótesis | Riesgo si es incorrecta |
|----|-----------|------------------------|
| H14 | Para archivos de texto, se muestran las primeras 10 líneas como vista previa | Demasiado o muy poco contenido mostrado |
| H15 | Se determina si un archivo es texto por su extensión (.txt, .md, .py, .json, .csv, etc.) — no por análisis de contenido | Archivos de texto no reconocidos, o binarios tratados como texto |
| H16 | Los archivos binarios/no-texto muestran: nombre, extensión y tamaño en formato humano (KB, MB) | Metadatos insuficientes o formato confuso |

### Errores y robustez

| ID | Hipótesis | Riesgo si es incorrecta |
|----|-----------|------------------------|
| H17 | Los errores de acceso (permisos) se muestran en la columna derecha con un mensaje tipo "[Acceso denegado]" | El error no es visible o bloquea la navegación |
| H18 | La aplicación no se detiene ante un error de lectura individual; simplemente marca el elemento como inaccesible | Crash de la aplicación por un directorio protegido |
| H19 | No se implementa detección automática de cambios en el filesystem; el contenido se lee al navegar | Datos desactualizados si el filesystem cambia |

### Plataforma

| ID | Hipótesis | Riesgo si es incorrecta |
|----|-----------|------------------------|
| H20 | El MVP se desarrolla y prueba en el sistema operativo del desarrollador (Windows) y se usa `pathlib` para compatibilidad multiplataforma | Dependencias de plataforma, paths hardcodeados |
| H21 | La columna izquierda en la raíz del sistema se muestra vacía (sin redistribuir espacio) | Layout inconsistente o confuso en la raíz |

---

## 6. Criterios de aceptación propuestos

Para considerar el MVP funcional, se proponen los siguientes criterios mínimos:

1. **Arranque correcto:** La aplicación arranca mostrando tres columnas con el directorio actual.
2. **Navegación vertical:** ↑/↓ cambian la selección en la columna central y actualizan la columna derecha.
3. **Entrada en directorio:** → o Enter entra en el directorio seleccionado, desplazando las columnas.
4. **Retorno al padre:** ← vuelve al directorio padre, manteniendo la selección previa.
5. **Diferenciación visual:** Directorios y archivos se distinguen visualmente (color/estilo).
6. **Selección visible:** El elemento seleccionado es claramente identificable.
7. **Ruta visible:** La ruta actual se muestra en pantalla.
8. **Directorio vacío:** Se maneja correctamente sin errores.
9. **Error de acceso:** Se muestra mensaje de error sin detener la aplicación.
10. **Salida limpia:** El usuario puede salir de la aplicación de forma controlada.

---

## 7. Próximos pasos

1. **Validar hipótesis** (H01–H21) con el propietario del producto o el equipo.
2. **Priorizar dudas** (D01–D18): separar las que bloquean implementación de las que se pueden decidir durante desarrollo.
3. **Definir plan de implementación** basado en las capas de la guía de arquitectura (estado → lógica → filesystem → visualización).
4. **Implementar MVP** resolviendo las hipótesis validadas.
5. **Verificar** contra los criterios de aceptación.

---

## Anexo: Trazabilidad

| Documento fuente | Contenido utilizado |
|------------------|-------------------|
| Especificación funcional original | Historias de usuario, reglas de navegación, casos límite, alcance |
| Guía de arquitectura | Capas, tecnologías, principios de desacoplamiento |
| Capacidades - objetivos y entrega | Contexto del ejercicio, capacidades esperadas |
| Informe individual de uso de IA | Estructura de entrega y evaluación |
