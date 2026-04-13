from pathlib import Path

from app.config.settings import AppSettings


def clear_settings_env(monkeypatch) -> None:
    for env_name in (
        "INBOX_DIR",
        "PROCESSING_DIR",
        "OUTBOX_DIR",
        "ERRORS_DIR",
        "ARCHIVE_DIR",
        "CONFIG_DIR",
        "DATABASE_URL",
        "LOG_LEVEL",
        "ACTIVE_PROCESSOR",
        "FILE_STABILISATION_SECONDS",
    ):
        monkeypatch.delenv(env_name, raising=False)


def test_default_settings(monkeypatch) -> None:
    clear_settings_env(monkeypatch)

    settings = AppSettings(_env_file=None)

    assert settings.inbox_dir == Path("./data/inbox")
    assert settings.log_level == "INFO"
    assert settings.active_processor == "check_account_balance"


def test_custom_inbox_dir_is_accepted(monkeypatch) -> None:
    clear_settings_env(monkeypatch)
    custom_inbox_dir = Path("/tmp/test_inbox")

    settings = AppSettings(_env_file=None, inbox_dir=custom_inbox_dir)

    assert settings.inbox_dir == custom_inbox_dir


def test_log_level_defaults_to_info(monkeypatch) -> None:
    clear_settings_env(monkeypatch)

    settings = AppSettings(_env_file=None)

    assert settings.log_level == "INFO"
