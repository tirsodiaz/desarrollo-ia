# Paso 6 — Servicio de aplicación (orquestación de archivos)

## Objetivo

Implementar el servicio que orquesta el flujo completo: detectar archivos en `/inbox/`, moverlos a `/processing/`, invocar el procesador, y escribir el resultado en `/outbox/` o `/errors/`. Este servicio conecta todos los componentes anteriores.

---

## 1. Rol en la arquitectura

El servicio de aplicación es el **orquestador** que gestiona el ciclo de vida de cada caso:

```
inbox/ ──→ processing/ ──→ processor ──→ outbox/ o errors/
```

No contiene lógica de negocio — solo coordina la secuencia de operaciones.

---

## 2. Implementación

```python
# src/cab/application/service.py

import json
import shutil
import logging
from pathlib import Path

from cab.domain.models import CaseInput
from cab.application.processor import CheckAccountBalanceProcessor
from cab.application.ports import ProcessingError
from cab.infrastructure.filesystem.writers import OutputWriter, ErrorWriter

logger = logging.getLogger(__name__)


class FileProcessingService:
    """
    Servicio que procesa casos desde el sistema de archivos.

    Ciclo de vida de un caso:
    1. Detectar archivos en inbox/
    2. Mover archivo a processing/
    3. Parsear JSON → CaseInput
    4. Ejecutar procesador
    5. Escribir resultado en outbox/ o error en errors/
    6. Mover archivo de processing/ a processed/ con timestamp en el nombre
    """

    def __init__(
        self,
        inbox_dir: Path,
        processing_dir: Path,
        processor: CheckAccountBalanceProcessor,
        output_writer: OutputWriter,
        error_writer: ErrorWriter,
    ) -> None:
        self._inbox_dir = inbox_dir
        self._processing_dir = processing_dir
        self._processor = processor
        self._output_writer = output_writer
        self._error_writer = error_writer

    def process_all(self) -> int:
        """
        Procesa todos los archivos pendientes en inbox/.

        Returns:
            Número de archivos procesados.
        """
        files = sorted(self._inbox_dir.glob("*.json"))
        processed = 0

        for file_path in files:
            self._process_file(file_path)
            processed += 1

        return processed

    def _process_file(self, file_path: Path) -> None:
        """Procesa un único archivo de caso."""
        case_id = file_path.stem
        logger.info("Procesando caso: %s", case_id)

        # 1. Mover a processing/
        processing_path = self._move_to_processing(file_path)

        try:
            # 2. Leer y parsear
            case_input = self._parse_case(processing_path)
            case_id = case_input.caseId

            # 3. Procesar
            result = self._processor.process(case_input)
            logger.info("Caso %s → acción: %s", case_id, result.action.value)

            # 4. Escribir resultado exitoso
            self._output_writer.write(result)

        except ProcessingError as e:
            logger.warning("Error de procesamiento en caso %s: %s", case_id, e)
            self._error_writer.write(
                case_id=case_id,
                errors=[{"code": e.code, "message": e.message}],
            )

        except Exception as e:
            logger.error("Error inesperado en caso %s: %s", case_id, e)
            self._error_writer.write(
                case_id=case_id,
                errors=[{"code": "ERR999", "message": str(e)}],
            )

        finally:
            # 5. Mover archivo a processed/ con timestamp
            if processing_path.exists():
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                stem = processing_path.stem
                dest = processed_dir / f"{stem}_{timestamp}.json"
                shutil.move(str(processing_path), str(dest))

    def _move_to_processing(self, file_path: Path) -> Path:
        """Mueve el archivo de inbox/ a processing/."""
        dest = self._processing_dir / file_path.name
        shutil.move(str(file_path), str(dest))
        return dest

    def _parse_case(self, file_path: Path) -> CaseInput:
        """Lee y parsea un archivo JSON como CaseInput."""
        raw = file_path.read_text(encoding="utf-8")
        data = json.loads(raw)
        return CaseInput.model_validate(data)
```

---

## 3. Flujo paso a paso

```
  inbox/CASE_001.json
         │
    ┌────▼────┐
    │  MOVER  │ → processing/CASE_001.json
    └────┬────┘
         │
    ┌────▼─────────┐
    │  PARSEAR     │ → CaseInput(caseId="CASE_001", ...)
    └────┬─────────┘
         │
    ┌────▼─────────┐
    │  PROCESAR    │ → DomainResult(action=POSITIVE_BALANCE)
    └────┬────┬────┘
         │    │
    ┌────▼──┐ └──┐
    │ÉXITO  │    │ERROR
    │       │    │
    ▼       │    ▼
  outbox/   │  errors/
  CASE_001  │  CASE_001
  .json     │  _error.json
            │
    ┌───────▼──────┐
    │  ARCHIVAR    │ → processed/CASE_001_YYYYMMDD_HHMMSS.json
    └──────────────┘
```

---

## 4. Manejo de errores por capa

| Tipo de error | Origen | Tratamiento |
|---|---|---|
| `ProcessingError` | Procesador (lógica de negocio) | Se escribe en `/errors/` con código y mensaje |
| `ValidationError` (Pydantic) | Parseo del JSON | Se captura como `Exception`, código ERR999 |
| `FileNotFoundError` | Sistema de archivos | Se captura como `Exception`, código ERR999 |
| Cualquier otro | Inesperado | Se captura como `Exception`, código ERR999 |

---

## 5. Decisiones de diseño

| Decisión | Justificación |
|---|---|
| `process_all()` retorna el conteo | Permite al CLI informar cuántos casos se procesaron |
| Archivos se procesan en orden alfabético | `sorted()` garantiza orden determinista |
| El archivo se mueve a `processed/` con timestamp siempre | `finally` asegura el archivado incluso con errores |
| `case_id` se extrae del nombre de archivo como fallback | Si el JSON es inválido, al menos tenemos un identificador |
| `shutil.move` en vez de `rename` | Funciona entre diferentes sistemas de archivos |

---

## 6. Log de trazabilidad

El servicio usa `logging` para registrar:

- Inicio de procesamiento de cada caso
- Acción resultante en caso de éxito
- Advertencia en caso de `ProcessingError`
- Error en caso de excepción inesperada

Esto permite observar *qué entra, qué ocurre, qué sale* — requisito de la especificación.

---

## Criterio de completitud

Este paso está completo cuando:

- [ ] `service.py` define `FileProcessingService`
- [ ] El servicio detecta, mueve, parsea, procesa y escribe resultados
- [ ] Los errores de negocio generan archivos en `/errors/` con el formato correcto
- [ ] Los errores inesperados no rompen el procesamiento de otros casos
- [ ] Cada caso se procesa de forma independiente
- [ ] El archivo de `processing/` se mueve a `processed/` con timestamp siempre (éxito o error)
