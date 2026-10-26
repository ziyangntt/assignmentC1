from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path

from logscope.parser import is_error_level, parse_line


def summarize_file(file_path: str | Path) -> dict[str, object]:
    path = Path(file_path)
    total_lines = 0
    well_formed = 0
    malformed = 0
    levels: Counter[str] = Counter()
    errors: Counter[str] = Counter()
    first_timestamp: datetime | None = None
    last_timestamp: datetime | None = None

    with path.open("r", encoding="utf-8", errors="replace") as log_file:
        for line in log_file:
            total_lines += 1
            entry = parse_line(line)
            if entry is None:
                malformed += 1
                continue

            well_formed += 1
            levels[entry.level] += 1
            if is_error_level(entry.level):
                errors[entry.message] += 1
            if first_timestamp is None or entry.timestamp < first_timestamp:
                first_timestamp = entry.timestamp
            if last_timestamp is None or entry.timestamp > last_timestamp:
                last_timestamp = entry.timestamp

    return {
        "file": str(path),
        "total_lines": total_lines,
        "well_formed": well_formed,
        "malformed": malformed,
        "levels": dict(levels),
        "top_errors": [
            {"message": message, "count": count}
            for message, count in errors.most_common(5)
        ],
        "first_timestamp": first_timestamp.isoformat() if first_timestamp else None,
        "last_timestamp": last_timestamp.isoformat() if last_timestamp else None,
    }
