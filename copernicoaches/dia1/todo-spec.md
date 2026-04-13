# To-Do Feature Spec

## Objetivo

Ampliar la aplicación existente para convertirla en una mini **To-Do app** que permita gestionar una lista simple de tareas desde la interfaz web.

## Alcance

La aplicación permitirá:

- visualizar una lista de tareas
- añadir una nueva tarea
- marcar una tarea como completada

No se utilizará base de datos.  
Las tareas se almacenarán en un archivo YAML (`todo-items.yaml`).

## Comportamiento esperado

- Al abrir la página principal, se muestra la lista de tareas:
  - cada tarea indica si está completada o no
  - las tareas completadas se muestran diferenciadas (por ejemplo, tachadas o con estilo distinto)
- El usuario puede añadir una nueva tarea mediante un formulario sencillo (campo de texto + botón).
- El usuario puede marcar una tarea como completada mediante una acción en la interfaz (enlace o botón junto a cada tarea pendiente).
- Tras añadir o completar una tarea, la aplicación redirige de nuevo a la página principal mostrando el estado actualizado.

## Cambios necesarios en backend

- Extender la función de carga de tareas para trabajar con objetos que incluyan:
  - texto de la tarea
  - estado de completada (booleano)
- Añadir una función de guardado de tareas en `todo-items.yaml`.
- Ampliar la ruta principal (`/`):
  - aceptar peticiones `POST` para crear nuevas tareas
  - seguir devolviendo la vista con la lista actualizada en `GET`
- Añadir una nueva ruta (por ejemplo `/complete/<int:item_id>`) para marcar una tarea como completada a partir de su índice en la lista.

## Cambios en la interfaz (frontend)

- Actualizar `templates/index.html` para:
  - mostrar la lista de tareas con una distinción visual entre completadas y pendientes
  - incluir un formulario para añadir una nueva tarea (campo de texto + botón "Añadir")
  - incluir, para cada tarea pendiente, un enlace o botón "Completar" que apunte a la ruta correspondiente.

## Criterios de aceptación

La funcionalidad se considera correcta si:

- al abrir la página, se ve la lista de tareas leídas desde `todo-items.yaml`
- se puede añadir una nueva tarea desde la propia página y aparece en la lista sin errores
- se puede marcar una tarea como completada desde la interfaz y su estado se refleja visualmente
- los datos quedan persistidos en `todo-items.yaml` de forma que, al recargar la página o reiniciar la aplicación, se mantiene el estado de las tareas.
