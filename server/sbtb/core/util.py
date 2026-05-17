from datetime import datetime, UTC
from uuid import UUID


def utc_now() -> datetime:
    return datetime.now(UTC)


def is_valid_uuid4(uuid_: str) -> bool:
    try:
        return UUID(uuid_).version == 4
    except ValueError:
        return False
