from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

from check_account_balance.application.case_processor import CheckAccountBalanceProcessor
from check_account_balance.infrastructure.file_case_reader import FileCaseReader
from check_account_balance.infrastructure.file_config_reader import (
    FileBalanceProvider,
    FileCalendarProvider,
    FileConfigProvider,
)
from check_account_balance.infrastructure.file_result_writer import FileResultWriter
from check_account_balance.ports.config_provider import ProcessingError


logger = logging.getLogger(__name__)


def run(data_dir: Path, verbose: bool = False) -> int:
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")

    inbox_dir = data_dir / "inbox"
    processing_dir = data_dir / "processing"
    processed_dir = data_dir / "processed"
    outbox_dir = data_dir / "outbox"
    errors_dir = data_dir / "errors"
    config_dir = data_dir / "config"

    for directory in [inbox_dir, processing_dir, processed_dir, outbox_dir, errors_dir, config_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    reader = FileCaseReader(inbox_dir=inbox_dir, processing_dir=processing_dir, processed_dir=processed_dir)
    writer = FileResultWriter(outbox_dir=outbox_dir, errors_dir=errors_dir)

    processor = CheckAccountBalanceProcessor(
        balance_provider=FileBalanceProvider(config_dir),
        calendar_provider=FileCalendarProvider(config_dir),
        config_provider=FileConfigProvider(config_dir),
    )

    processed = 0
    for case_file in reader.read_cases():
        try:
            result = processor.process(case_file.case_input)
            writer.write_result(result)
            logger.info("Caso %s procesado con acción %s", case_file.case_id, result.action.value)
        except ProcessingError as exc:
            writer.write_error(case_file.case_id, exc.code, exc.message)
            logger.warning("Error de negocio en %s: %s", case_file.case_id, exc)
        except Exception as exc:
            writer.write_error(case_file.case_id, "ERR999", str(exc))
            logger.exception("Error inesperado en %s", case_file.case_id)
        finally:
            reader.cleanup(case_file)

        processed += 1

    return processed


def main() -> None:
    parser = argparse.ArgumentParser(description="Check Account Balance")
    parser.add_argument("--data-dir", default="data", type=Path)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Modo demonio: monitoriza inbox continuamente",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        metavar="SEGUNDOS",
        help="Segundos entre comprobaciones en modo demonio (default: 10)",
    )
    args = parser.parse_args()

    if args.daemon:
        log_level = logging.DEBUG if args.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        )
        logger.info(
            "Demonio iniciado — revisando inbox cada %d s. Ctrl+C para detener.",
            args.interval,
        )
        try:
            while True:
                total = run(data_dir=args.data_dir, verbose=args.verbose)
                if total > 0:
                    logger.info("Ciclo completado: %d caso(s) procesado(s).", total)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("Demonio detenido.")
    else:
        total = run(data_dir=args.data_dir, verbose=args.verbose)
        if total == 0:
            print("No hay casos pendientes en inbox/")
        else:
            print(f"Procesados {total} caso(s)")


if __name__ == "__main__":
    main()
