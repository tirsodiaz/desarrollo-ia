from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    inbox_dir: Path = Path("./data/inbox")
    processing_dir: Path = Path("./data/processing")
    outbox_dir: Path = Path("./data/outbox")
    errors_dir: Path = Path("./data/errors")
    archive_dir: Path = Path("./data/archive")
    config_dir: Path = Path("./data/config")
    database_url: str = "sqlite:///./madriguera.db"
    log_level: str = "INFO"
    active_processor: str = "check_account_balance"
    file_stabilisation_seconds: float = 0.5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    def runtime_directories(self) -> tuple[Path, Path, Path, Path, Path, Path]:
        return (
            self.inbox_dir,
            self.processing_dir,
            self.outbox_dir,
            self.errors_dir,
            self.archive_dir,
            self.config_dir,
        )
