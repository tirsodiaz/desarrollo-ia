# SPEC-00 | INFRA | VERIFICACION | Verificar instalaciÃ³n y arranque del proyecto

## Metadatos

| Campo | Valor |
|-------|-------|
| **ID** | task-SPEC-00-infra-verificacion-instalacion-y-arranque |
| **CÃ³digo de plan** | SPEC-00 |
| **Ã‰pica** | INFRA â€” ConfiguraciÃ³n del proyecto y estructura |
| **Feature** | VERIFICACION â€” ValidaciÃ³n del entorno de desarrollo |
| **Tipo** | Tarea tÃ©cnica â€” CI/Entorno |
| **Prioridad** | Alta |
| **EstimaciÃ³n** | 1 h |

---

## DescripciÃ³n tÃ©cnica

Verificar que el proyecto se instala y ejecuta correctamente en un entorno limpio. Crear scripts de verificaciÃ³n rÃ¡pida para uso en pipeline futuro.

### Pasos de verificaciÃ³n

1. Crear entorno virtual: `python -m venv .venv`
2. Activar entorno y ejecutar: `pip install -e ".[dev]"`
3. Verificar entry point: `python -m miller` â†’ mensaje de arranque
4. Verificar script alias: `miller` â†’ mismo resultado
5. Ejecutar test suite: `pytest` â†’ 0 errors, 0 failures
6. Documentar comandos en `README.md`

### Artefactos de CI a crear

- `scripts/verify.ps1` â€” script PowerShell (Windows)
- `scripts/verify.sh` â€” script Bash (Linux/macOS)

---

## Objetivo arquitectÃ³nico

Garantizar la *reproducibilidad del entorno* desde el primer commit. Establece la disciplina de integraciÃ³n continua y evita el sÃ­ndrome de "funciona en mi mÃ¡quina".

---

## Criterios de aceptaciÃ³n

| # | Criterio |
|---|---------|
| CA-1 | `pip install -e ".[dev]"` finaliza sin errores en entorno limpio |
| CA-2 | `python -m miller` imprime mensaje de arranque con cÃ³digo de salida 0 |
| CA-3 | `miller` (entry point) produce el mismo resultado que `python -m miller` |
| CA-4 | `pytest` reporta `0 passed, 0 errors` |
| CA-5 | Scripts `verify.sh` / `verify.ps1` existen y pasan en entorno local |
| CA-6 | `README.md` documenta comandos de instalaciÃ³n y ejecuciÃ³n |

---

## Artefactos y entregables

- `scripts/verify.sh` y `scripts/verify.ps1`
- `README.md` con secciÃ³n de instalaciÃ³n y primeros pasos
- Evidencia de ejecuciÃ³n exitosa (output capturado en el PR)

---

## Dependencias

| Tipo | DescripciÃ³n |
|------|-------------|
| **Interna** | SPEC-00-INFRA-SETUP (proyecto y estructura deben existir) |
| **Bloquea** | SPEC-01-DOMINIO-MODELO â€” no iniciar implementaciÃ³n sin entorno verificado |

---

## Riesgos

| Riesgo | MitigaciÃ³n |
|--------|-----------|
| Sin `venv` activo â†’ contaminaciÃ³n de instalaciones globales | Documentar activaciÃ³n de venv como paso previo obligatorio |
| Diferencias entre PowerShell y bash | Mantener ambas versiones del script |


