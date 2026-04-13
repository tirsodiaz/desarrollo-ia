# Guía de arquitectura — Aplicación de consola

## Objetivo

Definir una estructura clara que permita implementar el sistema de forma mantenible, extensible y sin acoplamientos innecesarios.


## Principios clave

1. Separación estricta entre:

   * estado
   * lógica de navegación
   * visualización

2. Arquitectura orientada a componentes simples

3. Evitar lógica en la capa de visualización

4. Preparar el sistema para evolución sin reescritura

---

## Tecnologías recomendadas

* Python 3.12+
* **Rich** para renderizado en consola
* opcional futuro: **Textual**

---

## Capas de la aplicación

### 1. Estado (modelo)

Define:

* directorio actual
* directorio padre
* contenido del directorio actual
* elemento seleccionado
* contenido del elemento seleccionado

Este estado es la única fuente de verdad.

---

### 2. Lógica de navegación

Responsable de:

* gestionar eventos de teclado
* actualizar el estado
* controlar transiciones (entrar, salir, mover selección)

No contiene código de visualización.

---

### 3. Capa de sistema de archivos

Responsable de:

* leer directorios
* obtener metadatos de archivos
* manejar errores de acceso

No conoce la interfaz ni la navegación.

---

### 4. Visualización

Responsable de:

* representar el estado en consola
* dibujar columnas
* aplicar estilos

Recibe estado, no lo modifica.

## Interfaz de visualización

Contrato mínimo:

```text
render(state)
```

Posible evolución:

```text
render_left(state)
render_center(state)
render_right(state)
```

## Principio de desacoplamiento

La visualización:

* no accede directamente al sistema de archivos
* no contiene lógica de navegación
* no modifica estado

La lógica:

* no conoce detalles de renderizado

## Extensibilidad prevista

La arquitectura permite:

* sustituir Rich por otra librería
* introducir nuevos tipos de visualización
* especializar la columna derecha
* evolucionar hacia interfaces más complejas

Sin modificar:

* lógica de navegación
* modelo de estado

## Restricciones del MVP

* una única vista (tres columnas)
* sin plugins
* sin múltiples modos de interfaz
* sin persistencia compleja

## Regla arquitectónica final

> El sistema debe funcionar correctamente sin la capa de visualización;
> la visualización es una proyección del estado, no su motor.
