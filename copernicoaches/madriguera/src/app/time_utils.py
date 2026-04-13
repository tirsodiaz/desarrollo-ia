from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


def to_naive_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        raise ValueError("Expected timezone-aware datetime")
    return value.astimezone(UTC).replace(tzinfo=None)


def to_aware_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
