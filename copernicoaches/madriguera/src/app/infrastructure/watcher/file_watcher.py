import logging
import time
from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileCreatedEvent, FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

logger = logging.getLogger(__name__)


class InboxEventHandler(FileSystemEventHandler):
    def __init__(
        self,
        on_file_ready: Callable[[Path], None],
        stabilisation_seconds: float = 0.5,
    ):
        self._on_file_ready = on_file_ready
        self._stabilisation_seconds = stabilisation_seconds

    def on_created(self, event: FileCreatedEvent) -> None:
        if event.is_directory:
            return

        path = Path(event.src_path)
        if path.suffix.lower() != ".json":
            logger.debug("Ignoring non-JSON file: %s", path.name)
            return

        self._wait_for_stability(path)
        self._on_file_ready(path)

    def _wait_for_stability(self, path: Path) -> None:
        time.sleep(self._stabilisation_seconds)


class FileWatcher:
    def __init__(
        self,
        inbox_dir: Path,
        on_file_ready: Callable[[Path], None],
        stabilisation_seconds: float = 0.5,
    ):
        self._inbox_dir = inbox_dir
        self._handler = InboxEventHandler(on_file_ready, stabilisation_seconds)
        self._observer = PollingObserver()

    def start(self) -> None:
        self._observer.schedule(self._handler, str(self._inbox_dir), recursive=False)
        self._observer.start()
        logger.info("Watcher started on: %s", self._inbox_dir)

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()
        logger.info("Watcher stopped.")
