## Ejercicio extendido — De comandos a agentes y skills con reviews de películas

### Objetivo

Trabajar un mismo caso de negocio en tres niveles de sofisticación:

1. **Prompt commands** para ejecutar tareas concretas
2. **Custom agents** para especializar el comportamiento
3. **Skills** para automatizar un flujo completo con MCP

El caso será un mini sistema editorial de reviews de películas:

* **ClickUp** actúa como bandeja de entrada y salida editorial
* **SQLite (`movies.db`)** actúa como sistema estructurado de datos
* **Copilot / agente** actúa como capa de transformación

La idea central es simple:

* una tarea informal aparece en ClickUp
* la IA la interpreta
* la convierte en una entrada formal en la base de datos
* después recupera esa entrada
* genera un artículo más elaborado
* y lo vuelve a guardar en ClickUp como resultado editorial

---

## Escenario de trabajo

En ClickUp habrá tareas con texto libre, por ejemplo:

> “Nueva review. Película: The Thing. Me gustó mucho. Muy buena atmósfera, paranoia, efectos brutales. Creo que es de 1982. Hacer review más seria.”

Ese contenido no está bien estructurado.
El sistema debe convertirlo en algo útil.

En la base de datos SQLite debe existir una estructura razonable para almacenar, por ejemplo:

* título
* año
* texto base de review
* valoración
* estado
* versión formal o artículo

No hace falta que todo exista ya. Parte del ejercicio puede ser inspeccionar el esquema y adaptarse a él.

---

## Parte 1 — Prompt commands

Aquí el objetivo no es “tener inteligencia general”, sino crear **comandos reutilizables** en lenguaje natural para tareas concretas, como se explica en la documentación de prompt files .

### Comando 1 — `/ingest-movie-review`

Función:

* leer una tarea de ClickUp
* extraer de ella la información esencial
* transformarla en una estructura clara
* insertar esa estructura en `movies.db`

Debe hacer, como mínimo:

* identificar título
* detectar año si existe
* separar opinión libre de metadatos
* evitar inventar datos

Si el año no está claro, debe dejarlo vacío o marcarlo como dudoso.

### Comando 2 — `/update-movie-review`

Función:

* tomar una nueva tarea o comentario de ClickUp
* localizar la película correspondiente en SQLite
* actualizar la review o algunos campos

Ejemplo:

> “Corrección: no era de 1981, era de 1982. Añadir que la música también destaca.”

### Comando 3 — `/draft-article`

Función:

* recuperar una entrada formal desde SQLite
* redactar una review en estilo más editorial
* devolver el texto sin modificar todavía la base de datos

Aquí todavía no hay flujo completo.
Solo comandos puntuales.

### Qué debe aprender el equipo en esta fase

Que un prompt command sirve para **pedir una tarea concreta**.
No define un rol profundo ni una automatización compleja.
Es útil como primer paso porque obliga a pensar muy bien la intención de cada comando.

---

## Parte 2 — Custom agent

Después pasamos a un agente personalizado. Según el material, un custom agent define un **rol persistente**, con reglas y límites más estables que un prompt puntual .

### Agente propuesto — `movie-editor.agent.md`

Rol:

**Editor técnico de reviews de cine**

Responsabilidad:

* convertir entradas informales en registros consistentes
* mantener calidad y trazabilidad de la información
* redactar artículos sin alterar los hechos almacenados

Reglas sugeridas:

* no inventar datos factuales
* diferenciar entre dato confirmado y opinión
* usar ClickUp como entrada y publicación
* usar SQLite como fuente de verdad estructurada
* si hay ambigüedad, señalarla explícitamente
* no sobrescribir datos existentes sin justificación

### Qué cambia respecto a los comandos

Con los comandos decías: “haz esto”.

Con el agente dices: “trabaja de esta manera”.

Eso permite que varios comandos se comporten de forma coherente.
Por ejemplo, `/ingest-movie-review` y `/draft-article` ya no serían solo instrucciones aisladas. Ahora estarían ejecutados por un agente que entiende el dominio editorial.

### Ejercicio en esta fase

Pedir al equipo que compare resultados:

* ejecutar `/draft-article` sin agente especializado
* ejecutar `/draft-article` con `movie-editor`

Luego revisar diferencias:

* coherencia
* respeto por datos
* claridad del texto
* tratamiento de incertidumbre

Ese contraste es pedagógicamente útil.

---

## Parte 3 — Skill

Aquí llegamos al nivel más interesante. En el material, la skill se entiende como una **capacidad reutilizable compuesta**, que combina prompts, lógica y herramientas, incluyendo MCP .

### Skill propuesta — `publish-movie-review`

Esta skill debe orquestar el ciclo completo.

#### Flujo esperado

1. Leer una tarea nueva en ClickUp
2. Interpretar el contenido informal
3. Comprobar si la película ya existe en SQLite
4. Insertar o actualizar el registro formal
5. Recuperar la versión estructurada
6. Generar un artículo breve y coherente
7. Crear una nueva nota o tarea en ClickUp con el artículo final
8. Marcar el ítem original como procesado, si procede

### Qué une esta skill

* **Prompt**: invocación de alto nivel
* **Agent**: comportamiento editorial consistente
* **MCP ClickUp**: lectura y escritura de tareas/notas
* **MCP SQLite**: persistencia y consulta de datos

Aquí ya no hablamos de una acción puntual.
Hablamos de una capacidad reutilizable de negocio.

---

## Propuesta de progresión didáctica

### Fase A — Comandos

Cada equipo crea tres prompt files:

* `/ingest-movie-review`
* `/update-movie-review`
* `/draft-article`

Tienen que probarlos manualmente con varios ejemplos de ClickUp.

### Fase B — Agente

Cada equipo define `movie-editor.agent.md` con:

* rol
* reglas
* límites
* criterios de calidad

Luego repiten los comandos usando ese agente.

### Fase C — Skill

Cada equipo diseña una skill tipo:

* `/publish-movie-review`
* o equivalente como capacidad compuesta

La skill debe cubrir el flujo completo, no solo una parte.

---

## Ejemplos de entradas para ClickUp

Conviene que las tareas sean deliberadamente imperfectas. Por ejemplo:

**Ejemplo 1**

> “Nueva peli: Alien. Muy tensa, muy buena, Sigourney Weaver brutal. Creo que del 79. Hacer review.”

**Ejemplo 2**

> “Corregir Blade Runner. Añadir que el final es ambiguo y que visualmente sigue siendo top.”

**Ejemplo 3**

> “The Thing. Atmosphere increíble. Quizá poner nota 5/5. Revisar año.”

Así el equipo ve que el problema real no es técnico, sino de transformación de contexto.

---

## Qué entregable puede pedirse

Cada equipo debería cerrar el ejercicio con cuatro piezas.

Primero, un pequeño paquete de comandos:

* los prompt files
* una explicación breve de qué hace cada uno

Segundo, el agente personalizado:

* archivo `.agent.md`
* reglas definidas
* justificación breve del rol

Tercero, la skill:

* descripción del flujo completo
* herramientas MCP usadas
* entradas y salidas esperadas

Cuarto, una demostración mínima:

* tarea informal en ClickUp
* registro formal en SQLite
* artículo final generado
* publicación del artículo en ClickUp

---

## Qué se está enseñando realmente

Este ejercicio no trata solo de cine.
Lo que enseña es algo más importante:

* **prompt command**: resolver una tarea concreta
* **custom agent**: especializar comportamiento y criterio
* **skill**: empaquetar una capacidad multi-paso reutilizable

Eso permite mostrar de forma muy clara cómo se pasa de una interacción aislada a un flujo estructurado con herramientas externas, exactamente en la línea del artículo que compartiste .

## Texto listo para usar en el programa

### Ejercicio extendido — De comandos a agentes y skills con MCP

En este ejercicio vamos a trabajar una misma tarea en tres niveles: comandos, agente personalizado y skill. El objetivo es entender cómo se pasa de una instrucción puntual a una capacidad más completa y reutilizable.

Partimos de un caso simple: la gestión de reviews de películas. En ClickUp habrá tareas con descripciones informales, por ejemplo una nota breve con el título de la película, una opinión libre y algunos datos incompletos. Esa información debe ser leída por la IA, interpretada y transformada en una entrada formal dentro de la base de datos SQLite `movies.db`.

En una primera fase, cada equipo definirá varios prompt commands. Uno para ingerir una review informal y guardarla en la base de datos, otro para actualizar una review existente y otro para generar un borrador de artículo a partir de una entrada ya estructurada. Aquí el foco está en aprender a definir comandos claros, reutilizables y bien delimitados.

En una segunda fase, el equipo creará un custom agent con un rol editorial estable. Ese agente debe comportarse como un editor de reviews: separar datos de opiniones, no inventar información, tratar la ambigüedad con cuidado y usar SQLite como fuente estructurada de verdad. La idea es comprobar cómo cambia el resultado cuando ya no trabajamos solo con comandos, sino con un rol persistente y explícito.

En la tercera fase, el equipo diseñará una skill que una todo el flujo. La skill debe leer una tarea de ClickUp, convertirla en un registro formal en SQLite, recuperar ese registro, redactar un artículo breve y volver a guardarlo en ClickUp como salida editorial. Aquí ya no se evalúa una acción aislada, sino una capacidad compuesta que usa dos MCP y coordina varias etapas del trabajo.

El resultado esperado es que cada equipo demuestre una cadena completa: entrada informal en ClickUp, transformación estructurada en SQLite y publicación final de un artículo generado por la IA. El objetivo no es hacer una demo vistosa, sino entender cómo comandos, agentes y skills representan niveles distintos de madurez en el trabajo con IA conectada a sistemas reales.


