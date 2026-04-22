# Especificación Funcional (v2)

## Índice

1. Introducción y contexto
2. Objetivo del documento
3. Alcance funcional
   3.1 In-Scope
   3.2 Out-of-Scope
4. Requerimientos funcionales
5. Historias de usuario
6. Reglas de negocio
7. Arquitectura y modos de ejecución
8. Flujos de usuario
9. Supuestos e hipótesis
10. Riesgos y bloqueos

---

## 1. Introducción y contexto

Este documento describe la solución de conversión de documentos bidireccional para el proyecto denominado **docconv**. Se origina en el ejercicio de entrega asistida por IA del taller `dia4-docconv-jano` y en la guía de arquitectura asociada.

El objetivo del ejercicio es entregar una solución clara de transformación entre formatos Word (.docx) y Markdown (.md), soportada tanto por un modo CLI como por un modo MCP para integración con agentes de IA.

### Fuentes utilizadas

- `dia4-docconv-jano/Architecture-Guide.md`
- `dia4-docconv-jano/Ejercicio de Entrega Asistida por IA.md`
- `docconv/README.md`

---

## 2. Objetivo del documento

El objetivo es definir la especificación funcional v2 de la aplicación de conversión de documentos. El documento debe:

- describir el comportamiento esperado del sistema
- establecer el alcance funcional principal
- definir criterios de aceptación y reglas de negocio
- documentar los modos de ejecución y los flujos esperados
- registrar supuestos y riesgos

Este documento está dirigido a los equipos de desarrollo y a quienes validen la solución con el negocio.

---

## 3. Alcance funcional

### 3.1 In-Scope

La solución debe permitir:

- conversión de documentos de **Word (.docx) a Markdown (.md)**
- conversión de documentos de **Markdown (.md) a Word (.docx)**
- preservación de la estructura lógica del documento:
  - encabezados
  - párrafos
  - listas ordenadas y desordenadas
  - tablas
  - citas
  - bloques de código
- preservación de formato básico:
  - negrita
  - cursiva
  - enlaces
- ejecución desde línea de comandos (CLI)
- ejecución como servicio MCP accesible por un agente
- reporte de elementos no soportados o degradados mediante advertencias

### 3.2 Out-of-Scope

No se incluye en esta versión:

- conversión de formatos distintos a `.docx` y `.md`
- edición en línea de documentos
- interfaz gráfica de usuario
- integración con sistemas externos fuera de MCP
- sincronización de carpetas ni almacenamiento en la nube
- soporte completo de elementos avanzados de Word como macros o ecuaciones complejas

---

## 4. Requerimientos funcionales

### RF-1 — Conversión bidireccional

El sistema debe convertir `Word → Markdown` y `Markdown → Word`.

### RF-2 — Modo CLI predeterminado

El sistema debe ejecutarse por defecto mediante un comando de línea.

### RF-3 — Modo MCP

El sistema debe poder iniciarse en modo MCP con la misma lógica de conversión.

### RF-4 — Preservación de estructura lógica

El sistema debe conservar la jerarquía de encabezados, la separación de párrafos, las listas, tablas, citas y bloques de código.

### RF-5 — Preservación de formato básico

El sistema debe conservar negrita, cursiva y enlaces dentro de los documentos convertidos.

### RF-6 — Reporte de pérdidas o degradaciones

El sistema debe informar explícitamente cuando un elemento no puede ser convertido fielmente.

### RF-7 — Salida utilizable

El documento resultante debe ser utilizable en su formato de destino sin exigir que el usuario rehaga el documento manualmente.

### RF-8 — Consistencia entre CLI y MCP

La conversión debe usar la misma lógica central en ambos modos, sin duplicar la regla de negocio en adaptadores.

---

## 5. Historias de usuario

### US-1 — Conversión bidireccional de documentos

Como usuario, quiero convertir documentos de Word a Markdown y Markdown a Word, para trabajar en el mismo contenido en ambos formatos.

**Criterios de aceptación**

- Se permite conversión en ambas direcciones.
- El resultado es utilizable en el formato de destino.
- No se requiere rehacer el documento completo luego de la conversión.

### US-2 — Uso sencillo e integrado con el agente

Como usuario, quiero iniciar la conversión sin salir de Visual Studio Code, para mantener mi flujo de trabajo.

**Criterios de aceptación**

- Un agente puede invocar la conversión desde VS Code.
- El flujo es claro y directo.
- El resultado se genera de forma predecible.

### US-3 — Conservación de estructura lógica

Como usuario, quiero que los encabezados, párrafos, listas y tablas se mantengan, para que el documento conserve su organización.

**Criterios de aceptación**

- La jerarquía de encabezados se mantiene.
- Los párrafos permanecen diferenciados.
- Las listas y tablas se conservan.

### US-4 — Conservación de formato básico

Como usuario, quiero preservar negrita, cursiva y enlaces, para no perder estilo ni significado.

**Criterios de aceptación**

- La negrita y la cursiva se conservan.
- Los enlaces permanecen como enlaces.
- El sistema advierte si no puede preservar algo.

### US-5 — Preservación de características Markdown

Como usuario, quiero que el documento Markdown resultante sea natural y legible.

**Criterios de aceptación**

- El Markdown usa sintaxis estándar (encabezados `#`, listas, tablas GFM, etc.).
- El contenido no degrada progresivamente con conversiones repetidas.

### US-6 — Transparencia ante pérdidas

Como usuario, quiero saber cuándo se pierde o degrada una parte, para revisar manualmente si es necesario.

**Criterios de aceptación**

- El sistema informa elementos no soportados.
- No hay pérdida silenciosa de contenido soportado.
- El usuario puede identificar las partes afectadas.

---

## 6. Reglas de negocio

### RB-1 — Un solo motor de conversión

La lógica de conversión debe residir en una capa de dominio independiente de la entrada/salida.

### RB-2 — Adaptadores ligeros

Los adaptadores (CLI y MCP) deben limitarse a parsear argumentos, manejar I/O y reportar resultados.

### RB-3 — Informe de advertencias

Los elementos no soportados deben registrarse como advertencias, no como errores silenciosos.

### RB-4 — Gestión de errores

En caso de error técnico o entrada inválida, el sistema debe terminar con código de salida `1` y mostrar el error.

### RB-5 — Compatibilidad mínima

La aplicación debe funcionar con Python 3.11+ y usar `uv` para la gestión de dependencias y ejecución.

---

## 7. Arquitectura y modos de ejecución

### 7.1 Arquitectura recomendada

Según la guía de arquitectura, el sistema debe ser una aplicación en capas con:

- **Entry point**: `__main__.py` o ejecutable único
- **CLI adapter**: parseo de argumentos, salida por stdio
- **MCP adapter**: servidor MCP con herramienta `convert_document`
- **Application layer**: orquestación de la conversión
- **Domain layer**: lógica de conversión pura
- **Infrastructure layer**: lectura/escritura de archivos

### 7.2 Modos de ejecución

#### CLI

Comando esperado:

```bash
docconv input.docx output.md
docconv input.md output.docx
```

#### MCP

Comando esperado:

```bash
docconv --mcp
```

El modo MCP expone una herramienta con entrada `input_path` y `output_path`, retornando:

```json
{ "success": bool, "warnings": [...], "error": string | null }
```

### 7.3 Principios clave

- El modo CLI es el predeterminado.
- El modo MCP debe reutilizar la misma lógica central.
- No debe duplicarse lógica entre adaptadores.
- La arquitectura debe ser el mismo código base para ambos modos.

---

## 8. Flujos de usuario

### Flujo 1 — Conversión CLI

1. El usuario ejecuta `docconv input.docx output.md`.
2. El adaptador CLI valida la existencia de `input.docx`.
3. El sistema determina la dirección de conversión por la extensión de archivos.
4. Se invoca la aplicación de conversión.
5. El sistema escribe `output.md`.
6. Si hay advertencias, se imprimen en stderr.
7. Si la conversión falla, se imprime un error y se retorna código `1`.

### Flujo 2 — Conversión MCP

1. Se inicia `docconv --mcp`.
2. El agente envía una llamada a `convert_document` con `input_path` y `output_path`.
3. El adaptador MCP valida los parámetros.
4. Se invoca la aplicación de conversión.
5. El adaptador devuelve resultado JSON con éxito, advertencias y error.

### Flujo 3 — Conversión bidireccional

1. El usuario decide la dirección de conversión.
2. El sistema lee la extensión del archivo fuente.
3. Se aplica la conversión adecuada:
   - `.docx` → `.md`
   - `.md` → `.docx`
4. Se preserva estructura y formato básico.
5. Se reporta cualquier elemento degradado.

---

## 9. Supuestos e hipótesis

- **Hipótesis**: El nombre oficial del producto es `docconv`.
- **Hipótesis**: La herramienta final debe ser utilizable tanto por CLI como por agente MCP.
- **Hipótesis**: La preservación de formato básico se considera prioritaria frente a elementos avanzados de Word.
- **Información pendiente**: No hay definición explícita de los formatos de advertencia o del esquema JSON final usado por MCP.
- **Información pendiente**: No existe una lista completa de elementos de Word que deben manejarse en una primera versión.

---

## 10. Riesgos y bloqueos

- **Riesgo 1**: La conversión de Word a Markdown puede perder información avanzada de formato si no se define claramente el nivel de soporte.
- **Riesgo 2**: Si el modo MCP no se define con precisión, la integración con agentes puede quedar incompleta o inconsistente.
- **Riesgo 3**: La falta de un esquema de advertencias estándar puede generar resultados difíciles de interpretar.
- **Riesgo 4**: Si no se controla la compatibilidad entre CLI y MCP, podrían surgir duplicaciones en la implementación.
- **Riesgo 5**: El proyecto `docconv` está ubicado en `C:\cursos\desarrollo-ia\copernicoaches\docconv` y debe ser la referencia directa para la implementación.

---

## 11. Observaciones finales

Esta especificación funcional v2 se basa en el ejercicio asistido por IA y en la guía de arquitectura existente. El proyecto debe construirse como una aplicación única cuyo núcleo de conversión sea reutilizado por ambos modos de operación.

La implementación de referencia existente en el repositorio es `docconv`, ubicada en `C:\cursos\desarrollo-ia\copernicoaches\docconv`, que cumple con la mayoría de los requerimientos descritos y puede tomarse como base de validación.
