Conceptos clave
Simulación de un proceso automático que decide cómo avanzar en el cierre de una
cuenta en función del saldo.
Entrada → decisión → resultado
Todo basado en reglas y sin intervención humana.
Funcionamiento
Sistema batch basado en archivos:
■ /inbox/ → entrada
■ /outbox/ → resultado
■ /errors/ → errores
■ /config/ → datos simulados
Procesa casos, aplica reglas y genera una acción.
Lógica
Decisiones deterministas:
■ saldo (positivo / cero / negativo)
■ origen (CLI vs banco)
■ fechas (wait / cancel)
Mismo input → mismo output.
Enfoque
No es un ejercicio de tecnología.
Se trabaja:
■ interpretación del problema
■ traducción a lógica ejecutable
■ claridad y trazabilidad
Referencias
■ Ejecución del caso Check Account Balance.md
Propósito, expectativas y revisión
■ Especificación funcional - Simulación de proceso automático de
verificación de saldo.md
Reglas, comportamiento y formatos
Ambos definen el marco completo del ejercicio.