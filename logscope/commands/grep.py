from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from logscope.parser import normalize_level, parse_line, parse_timestamp


def parse_levels(values: Iterable[str] | None) -> set[str] | None:
    if values is None:
        return None

    levels = {
        normalize_level(level.strip())
        for value in values
        for level in value.split(",")
        if level.strip()
    }
    return levels or None


def grep_file(
    file_path: str | Path,
    levels: Iterable[str] | None = None,
    since: str | datetime | None = None,
    until: str | datetime | None = None,
    limit: int | None = None,
) -> dict[str, object]:
    if limit is not None and limit < 0:
        raise ValueError("limit must not be negative")

    path = Path(file_path)
    selected_levels = parse_levels(levels)
    since_timestamp = parse_timestamp(since) if isinstance(since, str) else since
    until_timestamp = parse_timestamp(until) if isinstance(until, str) else until
    matches: list[dict[str, str]] = []

    with path.open("r", encoding="utf-8", errors="replace") as log_file:
        for line in log_file:
            entry = parse_line(line)
            if entry is None:
                continue
            if selected_levels is not None and entry.level not in selected_levels:
                continue
            if since_timestamp is not None and entry.timestamp < since_timestamp:
                continue
            if until_timestamp is not None and entry.timestamp > until_timestamp:
                continue

            matches.append(
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "level": entry.level,
                    "message": entry.message,
                }
            )
            if limit is not None and len(matches) >= limit:
                break

    return {
        "file": str(path),
        "filters": {
            "level": sorted(selected_levels) if selected_levels is not None else None,
            "since": since_timestamp.isoformat() if since_timestamp else None,
            "until": until_timestamp.isoformat() if until_timestamp else None,
        },
        "match_count": len(matches),
        "matches": matches,
    }
