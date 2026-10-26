from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LogEntry:
    timestamp: datetime
    level: str
    message: str


_LEVEL_ALIASES = {
    "WARNING": "WARN",
    "FATAL": "CRITICAL",
}


def parse_timestamp(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    return datetime.fromisoformat(normalized)


def normalize_level(value: str) -> str:
    upper_value = value.upper()
    return _LEVEL_ALIASES.get(upper_value, upper_value)


def is_error_level(level: str) -> bool:
    return normalize_level(level) in {"ERROR", "CRITICAL"}


def parse_line(line: str) -> LogEntry | None:
    stripped = line.strip()
    if not stripped:
        return None

    parts = stripped.split()
    if "T" in parts[0]:
        if len(parts) < 3:
            return None
        timestamp_text = parts[0]
        level = parts[1]
        message = " ".join(parts[2:])
    else:
        if len(parts) < 4:
            return None
        timestamp_text = f"{parts[0]} {parts[1]}"
        level = parts[2]
        message = " ".join(parts[3:])

    try:
        timestamp = parse_timestamp(timestamp_text)
    except (TypeError, ValueError):
        return None

    return LogEntry(timestamp=timestamp, level=normalize_level(level), message=message)
