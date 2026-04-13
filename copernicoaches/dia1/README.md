# Día 1 — Ejercicio práctico

El objetivo de este ejercicio es comprobar que todo el entorno técnico funciona y empezar a trabajar con Copilot de forma estructurada.

No se trata de programar rápido.  
Se trata de entender un proyecto existente, documentarlo y ampliarlo siguiendo una pequeña especificación.

---

## Punto de partida

En esta carpeta (`dia1/`) hay una aplicación **Flask** sencilla.

El proyecto ya incluye:

- código base
- `pyproject.toml`
- dependencias declaradas

Vuestro trabajo es conseguir que la aplicación funcione en vuestro entorno.

---

## Paso 1 — Ejecutar el proyecto

Debéis conseguir que la aplicación funcione localmente.

Para ello tendréis que:

- revisar `pyproject.toml`
- instalar dependencias
- ejecutar la aplicación

Podéis usar **GitHub Copilot** para ayudaros.

Cuando funcione, la aplicación debería abrirse en:

```

[http://localhost:5001](http://localhost:5001)

```

---

## Paso 2 — Analizar el proyecto

Antes de modificar nada, revisad el código y tratad de entender:

- qué hace la aplicación
- qué ficheros existen
- cómo está organizada
- cómo se ejecuta

Podéis pedir a Copilot que explique el código.

---

## Paso 3 — Documentar el proyecto

Crearemos un pequeño documento `README-dia1.md` donde expliquéis:

- qué hace la aplicación
- estructura básica del proyecto
- cómo instalar dependencias
- cómo ejecutar la aplicación

---

## Paso 4 — Definir una ampliación

La aplicación debe ampliarse con una **mini To-Do app**.

Debe permitir como mínimo:

- ver tareas
- añadir tareas
- marcar tareas como completadas

Pero **no empecéis programando directamente**.

Primero debéis escribir una pequeña **spec**.

---

## Paso 5 — Escribir una spec

Crear un documento:

```

todo-spec.md

```

La spec debe describir brevemente:

- objetivo
- alcance
- comportamiento esperado
- cambios necesarios en backend
- cambios en la interfaz
- criterios de aceptación

Esto evita hacer "vibe coding".

---

## Paso 6 — Usar Copilot para implementar

Cuando tengáis la spec:

1. redactad un **prompt claro para Copilot**
2. pedid ayuda para implementar la funcionalidad
3. revisad el código generado

---

## Paso 7 — Commit

Subid los cambios al repositorio de cada proyecto. NO al repositorio comun.

Si todavia no teneis vuestro repo enlazado como remoto, anadidlo primero:

```bash
# Comprobar remotos actuales
git remote -v

# Anadir vuestro repositorio (sustituye la URL)
git remote add personal <URL_DE_VUESTRO_REPO>

# Opcional: si existe origin apuntando al repo comun, podeis renombrarlo
git remote rename origin comun
```

Luego haced commit y subid al remoto `personal`:

```bash
git add .
git commit -m "dia1 ejercicio"
git push -u personal HEAD
```

---

## Resultado esperado

Al final del día cada equipo debe tener:

- aplicación funcionando
- documentación del proyecto
- spec para la funcionalidad To-Do
- primera implementación de la To-Do app
```

---

# `todo-spec-template.md`

```markdown
# To-Do Feature Spec

## Objetivo

Añadir una funcionalidad simple de gestión de tareas a la aplicación existente.

## Alcance

La aplicación permitirá:

- visualizar una lista de tareas
- añadir una nueva tarea
- marcar una tarea como completada

No se utilizará base de datos.  
Las tareas pueden almacenarse en memoria o en un archivo simple.

## Cambios funcionales

Nueva página o sección que muestre:

- lista de tareas
- formulario para añadir tarea
- opción para marcar tarea como completada

## Cambios técnicos

Posibles cambios en:

- rutas Flask
- templates HTML
- estructura de datos para almacenar tareas

## Criterios de aceptación

La funcionalidad se considera correcta si:

- se puede añadir una tarea
- se puede ver la lista de tareas
- se puede marcar una tarea como completada
