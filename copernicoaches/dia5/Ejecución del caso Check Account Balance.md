## Documento de misión — Ejecución del caso “Check Account Balance”

### 1. Por qué existe este ejercicio

El objetivo no es desarrollar una aplicación completa ni practicar una tecnología concreta. El objetivo es trabajar sobre un problema que ya está definido a nivel de proceso, datos y comportamiento, y llevarlo a una implementación que sea comprensible, verificable y controlada.

En entornos reales, la información no llega limpia ni preparada. Aparece fragmentada en diagramas, estructuras de datos y contratos técnicos. La dificultad principal no está en escribir código, sino en interpretar correctamente ese conjunto y convertirlo en un sistema que se comporte como se espera.

Este ejercicio reproduce esa situación de forma controlada.

El caso contiene:

* lógica de negocio clara pero no trivial
* dependencias externas simuladas
* ambigüedades reales que requieren decisión

El trabajo consiste en transformar ese contexto en un sistema operativo sencillo, pero correcto.

---

### 2. Qué se espera construir

Se espera una implementación funcional del proceso descrito en la especificación, con las siguientes características:

* ejecución automática basada en archivos
* lectura de casos desde una carpeta de entrada
* aplicación de reglas de decisión
* generación de resultados estructurados
* manejo explícito de errores

El sistema debe permitir observar claramente:

* qué entra
* qué ocurre
* qué sale

No se espera una solución compleja. Se espera una solución clara.

---

### 3. Qué se está evaluando realmente

El foco no está en la cantidad de código ni en el uso de librerías avanzadas.

Se evalúa:

* comprensión del problema
* fidelidad al comportamiento esperado
* claridad de la solución
* capacidad de traducir reglas a lógica ejecutable
* manejo de casos límite
* trazabilidad entre entrada, decisión y salida

Una implementación simple pero correcta tiene más valor que una solución sofisticada pero opaca.

---

### 4. Alcance del trabajo

Cada equipo debe:

1. Implementar el proceso completo definido en la especificación
2. Utilizar el modelo basado en archivos (entrada, procesamiento, salida, errores)
3. Simular las dependencias externas mediante configuración
4. Ejecutar el sistema con distintos casos de prueba
5. Validar que los resultados son coherentes con las reglas

No es necesario:

* construir una interfaz gráfica
* exponer servicios HTTP
* optimizar rendimiento
* añadir funcionalidades fuera del alcance

---

### 5. Resultados esperados

Cada equipo debe entregar un conjunto mínimo de artefactos:

#### 5.1 Sistema ejecutable

Un programa que pueda ejecutarse localmente y procese casos desde archivos.

#### 5.2 Estructura de carpetas

Organización clara de:

* entrada
* procesamiento
* salida
* errores
* configuración

#### 5.3 Casos de prueba

Un conjunto de ejemplos que cubran al menos:

* saldo positivo
* saldo cero
* saldo negativo con origen cliente
* saldo negativo con origen banco
* caso con espera
* caso con cancelación

#### 5.4 Resultados generados

Archivos de salida que reflejen correctamente las decisiones del sistema.

#### 5.5 Explicación breve

Un documento corto que explique:

* cómo se ha interpretado el problema
* qué decisiones se han tomado
* qué ambigüedades se han resuelto y cómo

---

### 6. Cómo se va a revisar

La revisión se basa en tres ejes.

#### 6.1 Comportamiento

Se ejecutan casos de prueba y se verifica:

* que el sistema produce la acción correcta
* que las fechas se calculan correctamente
* que los estados `wait` y `cancel` funcionan como se espera

#### 6.2 Claridad

Se analiza si:

* el flujo del sistema es comprensible
* la estructura de archivos es coherente
* los nombres y decisiones son explícitos

#### 6.3 Robustez

Se comprueba:

* qué ocurre cuando falta información
* cómo se gestionan errores
* si el sistema falla de forma controlada

---

### 7. Criterios de calidad

Una solución se considera sólida cuando:

* cualquier persona puede seguir el flujo sin explicaciones adicionales
* los resultados son reproducibles
* las reglas están claramente reflejadas en el comportamiento
* los errores no rompen el sistema, sino que se registran

---

### 8. Qué no se espera

No se espera:

* código extenso o complejo
* uso intensivo de frameworks
* soluciones optimizadas prematuramente
* creatividad fuera del problema planteado

El valor está en la precisión, no en la sofisticación.

---

### 9. Resultado final esperado

Al finalizar, cada equipo debe haber demostrado que es capaz de:

* leer un problema estructurado pero no directamente implementable
* convertirlo en un sistema operativo simple
* validar su propio resultado
* explicar cómo funciona y por qué

Ese resultado es la base para trabajar posteriormente con especificaciones más complejas y entornos más cercanos a producción.
