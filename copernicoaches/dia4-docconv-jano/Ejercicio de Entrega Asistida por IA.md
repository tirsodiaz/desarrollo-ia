## **Brief Funcional — Ejercicio de Entrega Asistida por IA**

NOTE: the application name MUST be ¨Jano¨

### **Objetivo**

El objetivo de este ejercicio es que los equipos ejecuten un ciclo completo de trabajo asistido por IA, desde la interpretación de necesidades hasta la generación de resultados utilizables.

El foco NO está en la implementación técnica en sí, sino en:

* La transformación entre distintos tipos de artefactos
* La coherencia entre las diferentes fases
* El uso de la IA como herramienta de trabajo estructurada
* La capacidad de convertir ambigüedad en definición clara

---

## **Escenario General**

Se proporcionará un conjunto de **historias de usuario** (definidas previamente).

A partir de estas, el equipo deberá:

1. Interpretar y estructurar las necesidades
2. Generar una **especificación funcional de referencia**
3. Registrar dicha especificación en ClickUp utilizando MCP
4. Utilizar la especificación junto con una guía de arquitectura (ya definida)
5. Generar un **plan de implementación**
6. Ejecutar una solución funcional básica
7. Crear capacidades reutilizables de IA (comandos, agente, prompts)

---

## **Alcance Funcional**

El sistema a definir debe permitir:

* Convertir documentos de Word a Markdown
* Convertir documentos de Markdown a Word

El resultado debe ser utilizable y comprensible, manteniendo la estructura lógica del contenido.

---

## **Requisito No Funcional (NFR-0) — Modo de Ejecución**

El sistema DEBE permitir dos formas de uso:

* Uso directo mediante un comando (modo CLI)
* Uso como servicio accesible (modo MCP)

Ambos modos deben ofrecer las mismas capacidades desde el punto de vista del usuario.

Este requisito condiciona cómo se define la solución, pero no debe ser tratado como un detalle técnico en esta fase.

## **Historias de Usuario Funcionales**

### **US-1 — Conversión bidireccional de documentos**

Como usuario,
quiero poder convertir documentos de Word a Markdown y documentos de Markdown a Word,
para poder trabajar con el mismo contenido en ambos formatos según el contexto de uso.

**Criterios de aceptación**

* El sistema permite conversión en ambas direcciones.
* El resultado generado es utilizable en el formato de destino.
* La conversión no exige rehacer manualmente el documento completo tras cada transformación.

---

### **US-2 — Uso sencillo e integrado con el agente**

Como usuario,
quiero poder realizar la conversión de la forma menos intrusiva posible mediante el agente en Visual Studio Code,
para no tener que salir de mi entorno habitual de trabajo ni depender de pasos innecesarios.

**Criterios de aceptación**

* El usuario puede iniciar la conversión desde el agente.
* El flujo de uso es claro y directo.
* El sistema devuelve o genera el resultado de forma predecible.

---

### **US-3 — Conservación de la estructura lógica**

Como usuario,
quiero que la estructura lógica del documento se mantenga durante la conversión,
para que el contenido siga siendo comprensible y conserve su organización original.

**Criterios de aceptación**

* Los encabezados se mantienen con su jerarquía correcta.
* Los párrafos se conservan como unidades diferenciadas.
* Las listas se preservan como listas.
* Las tablas se mantienen como estructuras tabulares.
* No se pierden silenciosamente elementos estructurales soportados.

---

### **US-4 — Conservación del formato básico**

Como usuario,
quiero que el formato básico del documento se preserve en la medida de lo posible,
para mantener la legibilidad y el énfasis del contenido.

**Criterios de aceptación**

* La negrita se conserva.
* La cursiva se conserva.
* Los enlaces siguen identificándose como enlaces cuando aplique.
* Si algún elemento soportado no puede mantenerse completamente, el sistema debe indicarlo de forma explícita.

---

### **US-5 — Preservación de las características propias de Markdown**

Como usuario,
quiero que las características propias del estilo Markdown se mantengan al convertir entre formatos,
para que el documento siga siendo natural y correcto también en su representación textual.

**Criterios de aceptación**

* La estructura de encabezados en Markdown se representa correctamente.
* Las listas y tablas en Markdown siguen siendo legibles y coherentes.
* Los elementos de énfasis de Markdown se preservan cuando sea posible.
* La conversión repetida entre ambos formatos no debe degradar progresivamente los elementos cuya preservación está garantizada.

---

### **US-6 — Transparencia ante pérdidas o degradaciones**

Como usuario,
quiero saber cuándo algún elemento no puede convertirse de forma completa,
para poder revisar el resultado y corregirlo si es necesario.

**Criterios de aceptación**

* El sistema informa de elementos no soportados o degradados.
* No se pierde contenido soportado sin advertencia.
* El usuario puede identificar qué partes requieren revisión manual.

---

### **Dónde encajan estas historias**

Estas historias complementan el **NFR-0** y deben utilizarse como base para:

* interpretar el comportamiento esperado del sistema
* redactar la especificación funcional
* derivar criterios de validación
* comprobar que la solución implementada responde realmente a la necesidad definida

---

## **Fases del Ejercicio**

### **Fase 1 — Interpretación**

Entrada:

* Historias de usuario

El equipo deberá:

* Analizar el significado real de las historias
* Identificar ambigüedades
* Detectar información faltante
* Formular supuestos razonables

Salida:

* Entendimiento estructurado del problema

---

### **Fase 2 — Especificación Funcional**

El equipo deberá transformar las historias en una **especificación funcional clara y estructurada**.

La especificación debe incluir:

* Descripción funcional del sistema
* Comportamientos esperados
* Reglas principales
* Supuestos y limitaciones
* Casos relevantes o excepciones

Requisito:

* La especificación debe registrarse en ClickUp mediante MCP

---

### **Fase 3 — Planificación**

Entrada:

* Especificación funcional
* Guía de arquitectura (proporcionada)

El equipo deberá:

* Traducir la solución en un **plan de trabajo estructurado**

El plan debe:

* Estar ordenado
* Reflejar dependencias
* Ser ejecutable paso a paso

Salida:

* Plan de implementación

---

### **Fase 4 — Ejecución**

El equipo deberá construir una **solución funcional mínima** que permita:

* Convertir documentos entre Word y Markdown
* Demostrar claramente el resultado de la conversión

El foco está en:

* Que el flujo sea visible
* Que el resultado sea comprensible
* Que exista trazabilidad entre lo definido y lo construido

---

### **Fase 5 — Capacidades de IA**

El equipo deberá crear elementos reutilizables que faciliten el trabajo con IA:

#### **Comandos (Prompt Commands)**

* Para interpretar historias
* Para generar especificaciones
* Para crear planes

Deben ser reutilizables y claros.

---

#### **Agente Personalizado**

Un agente que permita:

* Procesar historias o especificaciones
* Generar artefactos
* Interactuar con sistemas externos (como ClickUp)

Debe tener un rol claro y acotado.

---

#### **Capacidades / Skills**

Funciones reutilizables como:

* Generación estructurada de contenido
* Registro de información en ClickUp
* Apoyo a la conversión de documentos

---

## **Entregables Esperados**

Cada equipo debe producir:

1. **Especificación funcional**

   * Registrada en ClickUp

2. **Plan de implementación**

   * Claro, ordenado y ejecutable

3. **Solución funcional**

   * Conversión Word ↔ Markdown demostrable

4. **Elementos de IA**

   * Comandos
   * Agente
   * Al menos una capacidad reutilizable

5. **Trazabilidad**

   * Relación clara entre:

     * Historias
     * Especificación
     * Plan
     * Resultado

---

## **Criterios de Evaluación**

Se evaluará:

* Claridad y calidad de la especificación
* Coherencia entre fases
* Uso efectivo de la IA
* Capacidad de estructurar el problema
* Calidad de los entregables
* Trazabilidad completa del proceso


---

## Test case

El repositorio incluye un directorio `test-case` que contiene dos documentos con contenido equivalente en ambos formatos:

* `Que es un LLM.docx`
* `Que es un LLM.md`

Ambos archivos representan el mismo documento funcional y han sido preparados para cubrir los elementos principales que la solución debe preservar durante la conversión, incluyendo:

* estructura de encabezados
* párrafos
* listas
* tablas
* negrita y cursiva
* bloques de cita
* bloques de código
* enlaces

La finalidad de este material es servir como caso de prueba base para validar la conversión en ambas direcciones:

* Word → Markdown
* Markdown → Word

### Uso esperado del test case

Los equipos DEBEN utilizar estos dos documentos como referencia de equivalencia funcional entre formatos. No se espera identidad binaria ni equivalencia visual perfecta, pero sí conservación del contenido y de la estructura lógica que la solución garantiza preservar.

El caso de prueba DEBERÍA utilizarse tanto para validación manual como para pruebas automatizadas.

### Recomendación de prueba automatizada

Una buena prueba automatizada consiste en verificar que conversiones repetidas en ambas direcciones no produzcan pérdida de información en aquellos elementos cuya preservación está garantizada por el sistema.

Por ejemplo:

1. tomar `Que es un LLM.docx`
2. convertirlo a Markdown
3. convertir el resultado de nuevo a Word
4. repetir el ciclo varias veces
5. comprobar que se mantienen:

   * el texto
   * la jerarquía de encabezados
   * las listas
   * las tablas
   * el formato básico soportado
   * los enlaces
   * los bloques de cita y de código

De forma equivalente, debe poder hacerse el mismo ejercicio comenzando desde `Que es un LLM.md`.

### Criterio de validación

La validación automática DEBE centrarse en la preservación semántica y estructural, no en diferencias menores de serialización o presentación. En otras palabras, la prueba debe confirmar que el contenido que el sistema promete conservar sigue presente tras múltiples conversiones, y que no aparece degradación acumulativa en los elementos soportados.

### Objetivo

Este test case existe para demostrar que la solución no solo convierte archivos una vez, sino que mantiene estabilidad razonable cuando los documentos pasan varias veces por el proceso de transformación. Ese comportamiento es esencial para considerar que la conversión es fiable dentro del alcance definido del ejercicio.

---

## **Principio Clave**

Este ejercicio no consiste en “usar IA para generar código”.

Consiste en:

* Pensar mejor
* Estructurar mejor
* Transformar mejor

La calidad del resultado dependerá de cómo el equipo utilice la IA para razonar, no solo para producir.
