from __future__ import annotations

import re
from datetime import datetime, timedelta


_BUCKET_PATTERN = re.compile(r"^(?P<amount>[1-9]\d*)(?P<unit>[smh])$")


def parse_bucket_size(value: str) -> int:
    match = _BUCKET_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError("bucket size must use a positive integer followed by s, m, or h")

    unit_seconds = {"s": 1, "m": 60, "h": 3600}
    return int(match["amount"]) * unit_seconds[match["unit"]]


def align_bucket(timestamp: datetime, bucket_seconds: int) -> datetime:
    if bucket_seconds <= 0:
        raise ValueError("bucket size must be positive")

    day_start = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
    elapsed_seconds = int((timestamp - day_start).total_seconds())
    return day_start + timedelta(seconds=elapsed_seconds - elapsed_seconds % bucket_seconds)
