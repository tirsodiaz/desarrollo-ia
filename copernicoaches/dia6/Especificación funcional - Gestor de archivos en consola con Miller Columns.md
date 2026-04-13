## Especificación funcional - Gestor de archivos en consola con Miller Columns

## Historias de usuario

**HU1 — Navegación estructurada** Como usuario, quiero navegar por el sistema de archivos de forma clara y continua para entender en todo momento dónde estoy y qué opciones tengo.

**HU2 — Contexto inmediato** Como usuario, quiero ver simultáneamente el directorio actual, su padre y sus posibles destinos para no perder contexto al moverme.

**HU3 — Exploración eficiente** Como usuario, quiero recorrer directorios rápidamente usando solo el teclado para minimizar fricción en entornos de consola.

**HU4 — Visibilidad del siguiente paso** Como usuario, quiero ver el contenido del elemento seleccionado antes de entrar en él para anticipar mis acciones.

**HU5 — Comprensión del sistema de archivos** Como usuario, quiero entender la estructura jerárquica del sistema de archivos sin tener que construirla mentalmente.

Ver referencia “Miller Columns” (column view): [https://en.wikipedia.org/wiki/Miller\_columns](https://en.wikipedia.org/wiki/Miller_columns)

## Propósito

El sistema proporciona una navegación estructurada del sistema de archivos basada en el modelo de **Miller Columns**, adaptado a un entorno de consola.

Este modelo permite:

* mantener contexto continuo durante la navegación  
* reducir la carga cognitiva  
* anticipar acciones sin cambiar de estado  
* evitar navegación ciega (entrar/salir sin visibilidad previa)

En un entorno restringido como la consola, este enfoque sustituye múltiples comandos por una **visualización estructurada y persistente del estado**.

## Modelo de interfaz

La interfaz se compone de tres columnas visibles simultáneamente:

* **Columna izquierda** → directorio padre  
* **Columna central** → directorio actual (foco)  
* **Columna derecha** → contenido del elemento seleccionado

El modelo soporta un número conceptual ilimitado de columnas, pero la interfaz muestra una ventana fija (por defecto, tres columnas) que se desplaza con la navegación.

La columna central define el estado actual del sistema.

## Comportamiento al inicio

Al arrancar la aplicación:

* se establece un directorio inicial (por defecto: directorio actual del sistema)  
* la columna central muestra el contenido de ese directorio  
* la columna izquierda muestra el contenido del directorio padre  
* la columna derecha muestra el contenido del elemento seleccionado en la columna central

Selección inicial:

* el primer elemento disponible en la columna central queda seleccionado  
* si el directorio está vacío, no hay selección y la columna derecha permanece vacía

## Reglas de navegación

### Movimiento vertical

El usuario navega dentro del directorio actual:

* mueve la selección en la columna central  
* la columna derecha se actualiza automáticamente

Comportamiento:

* si el elemento seleccionado es un directorio → se muestran sus hijos  
* si es un archivo → se muestra vista previa o metadatos

### Entrada en directorio

Cuando el usuario accede a un directorio:

* el elemento seleccionado pasa a ser el nuevo directorio actual  
    
* las columnas se desplazan:  
    
  * izquierda ← antiguo directorio actual  
  * centro ← nuevo directorio  
  * derecha ← contenido del nuevo directorio

### Retorno al directorio padre

Cuando el usuario vuelve atrás:

* el directorio padre pasa a ser el nuevo directorio actual  
    
* las columnas se desplazan:  
    
  * centro ← antiguo padre  
  * derecha ← antiguo directorio actual  
  * izquierda ← nuevo padre

* la selección se mantiene sobre el directorio desde el que se ha regresado

## Reglas de contenido de columnas

### Columna izquierda (padre)

* muestra el contenido del directorio padre  
* destaca el directorio actual dentro de ella  
* en la raíz del sistema, puede permanecer vacía o fija

### Columna central (actual)

* muestra el contenido del directorio actual  
* siempre mantiene una selección activa si hay elementos  
* define el estado de navegación

### Columna derecha (vista previa)

Depende del elemento seleccionado:

* si es directorio → muestra su contenido  
* si es archivo → muestra vista previa o metadatos  
* si no hay selección → permanece vacía

## Reglas visuales

El sistema garantiza:

* diferenciación visual entre archivos y directorios  
* resaltado claro del elemento seleccionado  
* énfasis visual en la columna central  
* visualización de la ruta actual (por ejemplo, en cabecera o barra de estado)

## Casos límite

### Directorio vacío

* la columna central muestra estado vacío  
* no hay selección  
* la columna derecha permanece vacía

### Selección de archivo

* no se permite navegación hacia la derecha  
* la columna derecha muestra información del archivo

### Directorio raíz

* no existe columna izquierda operativa  
* el sistema mantiene estabilidad visual

### Errores de acceso

* se muestra un indicador de error  
* el sistema continúa operativo  
* la columna derecha puede reflejar el error si aplica

## Modelo de estado

El sistema mantiene en todo momento:

* directorio actual  
* elemento seleccionado  
* directorio padre  
* objetivo de vista previa

Las columnas representan vistas derivadas de este estado.

## Extensión de la especificación funcional — Visualización

### Propósito

Definir cómo se presenta la información en consola, manteniendo el modelo de Miller Columns y asegurando claridad, consistencia y previsibilidad en el comportamiento.

### Alcance (en scope)

La visualización del sistema cumple:

* representación en **tres columnas** (izquierda, centro, derecha)
* uso de **texto estructurado en consola**
* uso de **colores y resaltado básico**
* actualización dinámica al navegar
* diferenciación visual entre:

  * directorios
  * archivos
  * elemento seleccionado

### Reglas de visualización

#### Columna izquierda (padre)

* listado textual del contenido del directorio padre
* el directorio actual aparece resaltado

#### Columna central (actual)

* listado textual del contenido del directorio actual
* un elemento está siempre seleccionado (si hay contenido)
* el elemento seleccionado se resalta claramente

#### Columna derecha (vista del seleccionado)

Comportamiento:

* si el elemento es un directorio → listado de su contenido

* si el elemento es un archivo → mostrar:

  * nombre
  * tipo
  * tamaño
  * opcional: primeras líneas si es texto

* si no hay selección → columna vacía


### Reglas de presentación

* alineación clara en columnas
* ancho consistente por columna
* uso de colores para:

  * selección
  * tipo de elemento
* visibilidad de la ruta actual (cabecera o estado)


### Comportamiento esperado

La visualización permite:

* entender el estado sin ambigüedad
* anticipar la navegación
* identificar rápidamente el elemento seleccionado
* ver el siguiente nivel sin cambiar de contexto

## Alcance

Incluye:

* navegación por teclado  
* visualización estructurada en tres columnas  
* actualización dinámica del contenido  
* representación del sistema de archivos local


### Fuera de alcance (out of scope)

En el MVP no se incluye:

* operaciones de modificación (copiar, borrar, mover)  
* integración con sistemas externos  
* navegación múltiple simultánea  
* uso de ratón* operaciones de modificación (copiar, borrar, mover)  
* integración con sistemas externos  
* interfaces gráficas (GUI)
* renderizado avanzado (imágenes, PDFs, etc.)
* visualización específica por tipo de archivo
* navegación dentro de archivos
* layouts dinámicos o configurables
* uso de ratón
* múltiples paneles simultáneos

### Principio funcional

> La visualización es simple, textual y suficiente para entender el estado completo del sistema en cada momento.

## Principio fundamental

El sistema garantiza en todo momento:

la columna central define dónde está el usuario, la columna izquierda muestra de dónde viene, y la columna derecha muestra a dónde puede ir.  