# Día 1 — Documentación del proyecto

## ¿Qué hace la aplicación?

Esta es una aplicación mínima en **Flask** que muestra una pequeña lista de tareas (To-Do) en una página web.

- Lee un archivo YAML (`todo-items.yaml`) donde hay una lista de tareas.
- Carga esas tareas en memoria en el arranque de cada petición.
- Renderiza una plantilla HTML (`templates/index.html`) que muestra la lista de tareas.
- Si el archivo no existe o el contenido no es válido, muestra una lista vacía.

La idea del ejercicio es usar esta base para extenderla con una mini To-Do app más completa.

---

## Estructura básica del proyecto

En la carpeta `dia1/` encontrarás:

- `app.py` → código principal de la aplicación Flask.
- `pyproject.toml` → configuración del proyecto y dependencias (usado por **uv**).
- `requirements.txt` → listado de dependencias en formato clásico de pip (no es necesario si usas uv, pero sirve de referencia).
- `todo-items.yaml` → archivo de datos con una lista inicial de tareas.
- `templates/` → carpeta con las plantillas HTML.
  - `templates/index.html` → plantilla que muestra la lista de tareas.
- `README.md` → enunciado general del ejercicio del Día 1.
- `README-dia1.md` → este documento, con la documentación específica del proyecto.
- `.venv/` (generado por uv) → entorno virtual con las dependencias instaladas.
- `uv.lock` → archivo de bloqueo generado por uv con versiones concretas de las dependencias.

---

## Requisitos previos

- **Python** 3.13 o superior (según `pyproject.toml`).
- **uv** instalado (gestor de dependencias y entornos).
- Sistema operativo: probado en Windows (PowerShell / terminal de VS Code).

---

## Cómo instalar dependencias

1. Abre una terminal en la carpeta del proyecto `dia1/`:

   ```powershell
   cd C:\ZZZZZ\workspace\copernicoaches\dia1
   ```

2. Ejecuta la sincronización de dependencias con **uv**:

   ```powershell
   uv sync
   ```

   Esto hará lo siguiente:

   - Creará un entorno virtual en `.venv/`.
   - Instalará las dependencias definidas en `pyproject.toml` (principalmente `flask` y `pyyaml`).

> Nota: no es necesario usar `pip install -r requirements.txt` si trabajas con **uv**, ya que `uv sync` se encarga de todo.

---

## Cómo ejecutar la aplicación

Con las dependencias ya instaladas, hay dos formas recomendadas de arrancar la app.

### Opción 1: usando uv directamente (recomendado)

Desde la carpeta `dia1/`:

```powershell
uv run python app.py
```

- `uv run` usa automáticamente el entorno virtual gestionado por uv.
- El servidor Flask se levantará escuchando en el puerto **5001**.

### Opción 2: activando el entorno virtual manualmente

1. Activar el entorno virtual (Windows, PowerShell):

   ```powershell
   .\.venv\Scripts\activate
   ```

2. Ejecutar la aplicación con `python`:

   ```powershell
   python app.py
   ```

---

## Cómo acceder a la aplicación

Una vez arrancada, abre el navegador y entra en:

- http://localhost:5001

Deberías ver una página titulada **"Lista To-Do"** que muestra las tareas leídas desde `todo-items.yaml` o un mensaje indicando que no hay tareas definidas.

---

## Paso 4 — Definición de la ampliación (To-Do app)

La ampliación definida consiste en convertir la aplicación en una mini **To-Do app**, que permita:

- ver la lista de tareas existentes
- añadir nuevas tareas desde la propia página
- marcar tareas como completadas

La fuente de datos sigue siendo el archivo YAML `todo-items.yaml`, sin base de datos.

La especificación detallada de esta ampliación está recogida en el documento:

- `todo-spec.md`

---

## Paso 5 — Spec de la funcionalidad To-Do

En `todo-spec.md` se describe:

- el objetivo de la funcionalidad To-Do
- el alcance (qué hace y qué no hace)
- el comportamiento esperado desde el punto de vista del usuario
- los cambios necesarios en backend (rutas, carga/guardado de datos)
- los cambios necesarios en la interfaz (formulario, botones de completar)
- los criterios de aceptación para validar que la funcionalidad está completa

Puedes abrir ese archivo para ver la spec completa o modificarla si el equipo decide cambiar el comportamiento.

---

## Paso 6 — Ampliación implementada (mini To-Do app)

La aplicación se ha ampliado siguiendo la spec anterior:

- `app.py` ahora:
   - carga las tareas desde `todo-items.yaml` como objetos con texto y estado (`done`)
   - guarda los cambios de vuelta en el YAML cuando se añaden o completan tareas
   - expone la ruta `/` aceptando `GET` y `POST` para listar y crear tareas
   - expone la ruta `/complete/<int:item_id>` para marcar una tarea como completada
- `templates/index.html` ahora:
   - muestra un formulario para añadir una nueva tarea
   - lista las tareas diferenciando visualmente las completadas (tachadas y con etiqueta)
   - ofrece un botón "Completar" para cada tarea pendiente

### Flujo de uso de la To-Do app

1. Abre la aplicación en http://localhost:5001.
2. En el bloque "Añadir nueva tarea", escribe el texto de la tarea y pulsa **Añadir**.
3. La página se recarga y la nueva tarea aparece en la lista.
4. Para marcar una tarea como completada, pulsa el botón **Completar** junto a esa tarea.
5. La tarea aparecerá tachada y con la marca de "Completada".

Los cambios se guardan en `todo-items.yaml`, de modo que, al reiniciar la aplicación, las tareas y su estado se mantienen.

---

## Notas adicionales

- Si cambias manualmente el contenido de `todo-items.yaml`, basta con refrescar la página del navegador para ver la nueva lista.
- El servidor se ejecuta en modo `debug=True` (definido en `app.py`), por lo que se recarga automáticamente cuando modificas el código.
- Puedes usar este proyecto como base para seguir ampliando la To-Do app (por ejemplo, permitiendo eliminar tareas o filtrar por estado).
