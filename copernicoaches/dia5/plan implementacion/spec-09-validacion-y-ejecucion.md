# Paso 9 — Validación y ejecución

## Objetivo

Verificar que el sistema completo funciona correctamente: preparar casos de prueba reales, ejecutarlos y validar que los resultados son coherentes con las reglas de la especificación.

---

## 1. Casos de prueba preparados

Crear los siguientes archivos JSON en `data/inbox/`:

### 1.1 Saldo positivo

```json
// data/inbox/CASE_001.json
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

**Resultado esperado:** `outbox/CASE_001.json` → `action: "positiveBalance"`

### 1.2 Saldo cero

```json
// data/inbox/CASE_002.json
{
  "caseId": "CASE_002",
  "source": "CLI",
  "contracts": [
    { "contractId": "ACC_002" }
  ],
  "accountClosure": {
    "dateToCheckBalance": null,
    "entity": "0014"
  }
}
```

**Resultado esperado:** `outbox/CASE_002.json` → `action: "zeroBalance"`

### 1.3 Saldo negativo — origen cliente, sin fecha

```json
// data/inbox/CASE_003.json
{
  "caseId": "CASE_003",
  "source": "CLI",
  "contracts": [
    { "contractId": "ACC_003" }
  ],
  "accountClosure": {
    "dateToCheckBalance": null,
    "entity": "0014"
  }
}
```

**Resultado esperado:** `outbox/CASE_003.json` → `action: "wait"`, `dateTime` calculado

### 1.4 Saldo negativo — origen banco, sin fecha

```json
// data/inbox/CASE_004.json
{
  "caseId": "CASE_004",
  "source": "BATCH",
  "contracts": [
    { "contractId": "ACC_003" }
  ],
  "accountClosure": {
    "dateToCheckBalance": null,
    "entity": "0014"
  }
}
```

**Resultado esperado:** `outbox/CASE_004.json` → `action: "bankNegativeBalance"`

### 1.5 Saldo negativo — fecha = hoy (cancelación)

```json
// data/inbox/CASE_005.json
{
  "caseId": "CASE_005",
  "source": "CLI",
  "contracts": [
    { "contractId": "ACC_003" }
  ],
  "accountClosure": {
    "dateToCheckBalance": "2026-03-23",
    "entity": "0014"
  }
}
```

> Nota: Ajustar `dateToCheckBalance` al día de ejecución.

**Resultado esperado:** `outbox/CASE_005.json` → `action: "cancel"`

### 1.6 Saldo negativo — fecha futura (espera)

```json
// data/inbox/CASE_006.json
{
  "caseId": "CASE_006",
  "source": "CLI",
  "contracts": [
    { "contractId": "ACC_003" }
  ],
  "accountClosure": {
    "dateToCheckBalance": "2026-03-25",
    "entity": "0014"
  }
}
```

**Resultado esperado:** `outbox/CASE_006.json` → `action: "wait"`, `dateTime: "2026-03-25T00:01:00"`

### 1.7 Cuenta inexistente (error)

```json
// data/inbox/CASE_007.json
{
  "caseId": "CASE_007",
  "source": "CLI",
  "contracts": [
    { "contractId": "ACC_999" }
  ],
  "accountClosure": {}
}
```

**Resultado esperado:** `errors/CASE_007_error.json` → `code: "ERR001"`

---

## 2. Secuencia de validación

### 2.1 Instalar el proyecto

```bash
cd <raíz del proyecto>
pip install -e ".[dev]"
```

### 2.2 Ejecutar tests automatizados

```bash
pytest tests/ -v
```

Todos los tests deben pasar.

### 2.3 Ejecutar con datos reales

```bash
cab run --data-dir data --verbose
```

### 2.4 Verificar resultados

```bash
# Ver resultados exitosos
ls data/outbox/

# Ver errores
ls data/errors/

# Verificar que inbox está vacío (todo procesado)
ls data/inbox/

# Verificar que processing está vacío (todo limpio)
ls data/processing/
```

### 2.5 Inspeccionar un resultado

```bash
cat data/outbox/CASE_001.json
```

Salida esperada:

```json
{
  "caseId": "CASE_001",
  "action": "positiveBalance",
  "dateTime": null
}
```

---

## 3. Matriz de validación

| Caso | Entrada | Acción esperada | dateTime | Destino | ✓ |
|------|---------|-----------------|----------|---------|---|
| CASE_001 | ACC_001, saldo=120.50 | positiveBalance | null | outbox | ☐ |
| CASE_002 | ACC_002, saldo=0 | zeroBalance | null | outbox | ☐ |
| CASE_003 | ACC_003, saldo=-45.20, CLI | wait | fecha calculada | outbox | ☐ |
| CASE_004 | ACC_003, saldo=-45.20, BATCH | bankNegativeBalance | null | outbox | ☐ |
| CASE_005 | ACC_003, fecha=hoy | cancel | null | outbox | ☐ |
| CASE_006 | ACC_003, fecha=futuro | wait | 2026-03-25T00:01 | outbox | ☐ |
| CASE_007 | ACC_999 (no existe) | - | - | errors | ☐ |

---

## 4. Lista de verificación final

### Comportamiento

- [ ] Cada caso de prueba produce la acción correcta
- [ ] Las fechas se calculan correctamente (días laborables)
- [ ] Los estados `wait` y `cancel` funcionan según la especificación
- [ ] Los archivos se mueven correctamente entre carpetas
- [ ] Mismo input → mismo output (determinismo)

### Claridad

- [ ] El flujo es comprensible leyendo el código
- [ ] La estructura de archivos es coherente con la especificación
- [ ] Los nombres de clases, métodos y variables son explícitos
- [ ] El log muestra qué entra, qué ocurre y qué sale

### Robustez

- [ ] Un caso con cuenta inexistente genera error controlado
- [ ] Un caso sin contratos genera error controlado
- [ ] Un JSON malformado no rompe el procesamiento de otros casos
- [ ] La carpeta `processing/` queda vacía después de ejecutar

### Arquitectura

- [ ] El dominio no depende de infraestructura
- [ ] Los puertos están definidos como `Protocol`
- [ ] Los adaptadores se pueden sustituir sin tocar el dominio
- [ ] El CLI es solo un punto de ensamblaje (Composition Root)
- [ ] Los tests de dominio no necesitan mocks de infraestructura

---

## 5. Resumen de artefactos entregables

| Artefacto | Ubicación |
|---|---|
| Sistema ejecutable | `src/cab/` con comando `cab run` |
| Estructura de carpetas | `data/` (inbox, processing, processed, outbox, errors, config) |
| Casos de prueba | `data/inbox/*.json` + tests automatizados |
| Resultados generados | `data/outbox/*.json` + `data/errors/*.json` |
| Tests automatizados | `tests/` con pytest |

---

## 6. Orden de ejecución completo

```
Paso 0: Configurar proyecto y carpetas        → pyproject.toml, data/, src/cab/
Paso 1: Modelos de dominio                     → domain/models.py
Paso 2: Reglas de dominio                      → domain/rules.py
Paso 3: Puertos de aplicación                  → application/ports.py
Paso 4: Caso de uso (procesador)               → application/processor.py
Paso 5: Adaptadores de infraestructura         → infrastructure/filesystem/
Paso 6: Servicio de aplicación                 → application/service.py
Paso 7: Adaptador CLI                          → cli/commands.py
Paso 8: Tests                                  → tests/
Paso 9: Validación y ejecución                 → esta guía
```

Cada paso depende de los anteriores. Cada paso es verificable de forma independiente.
