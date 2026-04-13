## Especificación funcional — Simulación de proceso automático de verificación de saldo

### 1. Propósito

Definir un sistema autónomo que simula la ejecución de un proceso bancario de verificación de saldo dentro de un flujo de cierre de cuentas. El sistema procesa casos a partir de archivos de entrada, aplica reglas de decisión y genera resultados estructurados sin intervención humana.

El sistema no implementa servicios reales ni interfaces de usuario. Opera exclusivamente mediante archivos en un sistema de carpetas.

---

### 2. Modelo operativo

El sistema se comporta como un proceso en ejecución continua que:

1. Detecta nuevos casos en una carpeta de entrada
2. Procesa cada caso de forma independiente
3. Determina una acción en función de reglas definidas
4. Genera un resultado estructurado
5. Maneja errores de forma explícita

El flujo es determinista y basado en reglas.

---

### 3. Estructura de carpetas

```plaintext
/inbox/         → casos pendientes de procesar  
/processing/    → casos en curso  
/outbox/        → resultados correctos  
/errors/        → resultados con error  
/config/        → datos de configuración y simulación  
```

---

### 4. Formato de entrada

Cada caso se representa como un archivo JSON en `/inbox/`.

Ejemplo simplificado:

```json
{
  "caseId": "CASE_001",
  "source": "CLI",
  "contracts": [
    { "contractId": "ACC_001" }
  ],
  "accountClosure": {
    "dateToCheckBalance": null,
    "entity": "0014"
  }
}
```

Campos relevantes:

* `caseId`: identificador del caso
* `source`: origen del proceso (ej. `CLI`, interno)
* `contracts[]`: lista de cuentas asociadas
* `accountClosure.dateToCheckBalance`: fecha de revalidación
* `accountClosure.entity`: entidad para cálculo de calendario

---

### 5. Configuración del sistema

El sistema utiliza archivos en `/config/` para simular dependencias externas.

#### 5.1 Saldos

```json
{
  "ACC_001": 120.50,
  "ACC_002": 0,
  "ACC_003": -45.20
}
```

#### 5.2 Calendario

Lista de días laborables y no laborables.

#### 5.3 Reglas

Parámetros configurables:

```json
{
  "daysToCheckBalance": 3
}
```

---

### 6. Flujo de procesamiento

Para cada archivo en `/inbox/`:

1. Mover el archivo a `/processing/`
2. Leer el contenido del caso
3. Determinar el `accountId` a partir de `contracts`
4. Obtener el saldo desde la configuración
5. Evaluar reglas de decisión
6. Generar resultado
7. Guardar resultado en `/outbox/` o `/errors/`

---

### 7. Lógica de decisión

El sistema evalúa el saldo y determina una acción.

#### 7.1 Casos directos

| Condición | Acción            |
| --------- | ----------------- |
| saldo > 0 | `positiveBalance` |
| saldo = 0 | `zeroBalance`     |

#### 7.2 Saldo negativo

Si saldo < 0:

1. Evaluar el origen (`source`)

| Condición      | Acción                    |
| -------------- | ------------------------- |
| source = `CLI` | `customerNegativeBalance` |
| otro valor     | `bankNegativeBalance`     |

2. Evaluar fecha de revalidación (`dateToCheckBalance`)

| Condición       | Acción                |
| --------------- | --------------------- |
| no existe       | calcular fecha futura |
| igual a hoy     | `cancel`              |
| distinta de hoy | `wait`                |

---

### 8. Cálculo de fecha futura

Cuando no existe `dateToCheckBalance`:

1. Leer `daysToCheckBalance` desde configuración
2. Consultar calendario
3. Calcular el siguiente día laborable según el parámetro
4. Guardar la fecha en el resultado

---

### 9. Formato de salida

Resultado en `/outbox/`:

```json
{
  "caseId": "CASE_001",
  "action": "positiveBalance",
  "dateTime": null
}
```

Posibles valores de `action`:

* `positiveBalance`
* `zeroBalance`
* `customerNegativeBalance`
* `bankNegativeBalance`
* `wait`
* `cancel`

Si la acción es `wait`, se incluye:

```json
"dateTime": "2026-03-20T00:01:00"
```

---

### 10. Manejo de errores

Si ocurre un error:

1. El procesamiento se detiene
2. Se genera un archivo en `/errors/`

Formato:

```json
{
  "caseId": "CASE_001",
  "taskName": "Check Account Balance",
  "dateTime": "2026-03-19T10:00:00",
  "errors": [
    {
      "code": "ERR001",
      "message": "Balance no encontrado"
    }
  ]
}
```

---

### 11. Comportamiento del sistema

* Cada caso se procesa de forma independiente
* No hay interacción entre casos
* El sistema es idempotente por archivo
* No hay estado persistente fuera de los archivos
* Las reglas son completamente deterministas

---

### 12. Alcance

Incluido:

* lectura y escritura de archivos
* evaluación de reglas
* simulación de dependencias externas
* generación de resultados

Excluido:

* interfaces gráficas
* llamadas a APIs reales
* persistencia en bases de datos
* concurrencia avanzada

---

### 13. Consideraciones abiertas

* selección del contrato cuando existen múltiples entradas
* definición exacta del saldo a utilizar
* normalización de valores de `source`
* precisión del calendario laboral

Estas decisiones deben resolverse en la configuración o en la lógica del sistema.
