# Ingeniería de contexto en generación de código

## Del prototipo frágil al sistema estable

En el desarrollo asistido por IA, la diferencia entre obtener un prototipo funcional y construir un sistema robusto no depende solo del modelo, sino de cómo se gestiona el contexto. Este principio se observa con claridad en el caso **Atrium**, un gestor de archivos en consola basado en Miller Columns. El nombre puede variar, pero el patrón es general.

Existen dos enfoques habituales.

El primero consiste en proporcionar a la IA una especificación funcional y una guía de arquitectura, y pedir directamente: “implementa el gestor de archivos”. A partir de ahí, se itera con pequeñas correcciones. Este enfoque es rápido. También es inherentemente inestable.

El segundo enfoque introduce un paso intermedio. La IA genera primero varios documentos de especificación detallados, cada uno autocontenido y con información relevante copiada desde las fuentes originales. Después, se implementa cada uno de esos documentos de forma secuencial.

La diferencia entre ambos enfoques es estructural.

### El problema del enfoque directo

En el caso Atrium, la especificación funcional define con precisión el comportamiento: navegación por columnas, centralidad de la columna activa, reglas de selección, comportamiento al volver atrás, diferencias entre directorios y archivos. La guía de arquitectura establece límites claros: separación entre estado, navegación, acceso al sistema de archivos y renderizado; el estado como única fuente de verdad; la visualización como proyección, no como motor.

Este material es sólido. El problema no es la calidad de la entrada, sino cómo se degrada en el proceso iterativo.

En un flujo directo, la IA comienza con todo el contexto disponible. Sin embargo, tras varias iteraciones, ese contexto se ve desplazado por código generado, correcciones puntuales y nuevas instrucciones. El sistema deja de estar gobernado por la especificación original y pasa a estar gobernado por el historial reciente. Esto es fragmentación de contexto.

A partir de ahí, se observan tres efectos sistemáticos.

El primero es la compresión prematura del problema. La IA reduce una especificación rica a una idea simplificada: “explorador de archivos en tres columnas con navegación por teclado”. Esa simplificación permite avanzar rápido, pero elimina matices críticos: mantener la selección al volver al directorio padre, actualizar correctamente la columna derecha según el tipo de elemento, tratar correctamente el directorio raíz o evitar efectos secundarios en el estado.

El segundo es la mezcla de capas. Aunque la arquitectura exige separación estricta, la implementación tiende a fusionar entrada, lógica de navegación y renderizado en un mismo bucle. Esto no es un error puntual; es una consecuencia de optimizar la coherencia local bajo presión de contexto.

El tercero es un bucle de corrección miope. Cada ajuste se realiza sobre el estado actual del código, no sobre la especificación original. El sistema evoluciona mediante parches. Las desviaciones se acumulan.

El resultado típico es un prototipo convincente pero frágil, que funciona en escenarios básicos y falla en los detalles que la especificación sí contemplaba.

### El cambio de estrategia: especificaciones intermedias

El enfoque alternativo introduce una capa adicional: la generación de especificaciones intermedias.

En el caso Atrium, esto implica que la IA produzca, por ejemplo, cuatro documentos: modelo de estado y acceso al sistema de archivos, lógica de navegación, renderizado, y composición general con bucle de eventos y validación. Cada documento incluye información relevante copiada de las fuentes originales.

Este paso no añade complejidad innecesaria. Cambia la forma en que el contexto se presenta al modelo.

La redundancia se convierte en una herramienta. Aunque en ingeniería tradicional se evita duplicar información, en generación de código asistida por IA esa duplicación estabiliza el proceso. Cada especificación contiene los invariantes que necesita. La IA no depende de recordar documentos anteriores; los tiene presentes en cada paso.

### Beneficios operativos

Este enfoque produce efectos concretos.

Reduce la entropía del contexto activo. Cada paso trabaja con un problema acotado, con sus restricciones y criterios de aceptación explícitos. La probabilidad de improvisación disminuye.

Preserva la arquitectura. Al separar explícitamente las responsabilidades en las especificaciones, se evita que la implementación colapse capas. El renderizado permanece como proyección; la navegación no invade la lógica de estado.

Facilita la recuperación ante errores. Si una fase se desvía, la siguiente no hereda automáticamente esa desviación. Cada paso se reinicia sobre su propia especificación.

Permite evaluar el progreso. Cada documento intermedio es un artefacto verificable. La validación no se limita al código final; se realiza en cada transición: contexto → especificación → implementación.

### Condición necesaria: una buena partición

El enfoque no es automático. La calidad depende de cómo se divida el sistema.

En Atrium, la partición natural está ya implícita en la arquitectura:

* Un módulo para el estado y el acceso al sistema de archivos  
* Un módulo para la lógica de navegación y selección  
* Un módulo para el renderizado como proyección del estado  
* Un módulo de composición, bucle de eventos y validación

Esta división respeta las dependencias reales del sistema. Si la partición es arbitraria, se introduce una nueva forma de fragmentación, ahora entre documentos.

### Conclusión

El enfoque directo permite construir rápidamente un prototipo. No garantiza la conservación de los invariantes del sistema a lo largo de múltiples iteraciones.

El enfoque basado en especificaciones intermedias alinea el proceso con el comportamiento real de los modelos de generación de código. Sustituye memoria implícita por restatements explícitos. Convierte una conversación larga y difusa en una secuencia de derivaciones controladas.

En términos prácticos: el primer enfoque depende de que el modelo recuerde el problema. El segundo garantiza que el problema se reintroduce, en la forma correcta, en cada paso.

Para sistemas como Atrium y, en general, para cualquier desarrollo no trivial, esta diferencia determina si el resultado es un demo o un sistema.  