from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from logscope.parser import is_error_level, parse_line
from logscope.timeutil import align_bucket, parse_bucket_size


def timeline_file(file_path: str | Path, bucket_size: str = "15m") -> dict[str, object]:
    path = Path(file_path)
    bucket_seconds = parse_bucket_size(bucket_size)
    counts: Counter[datetime] = Counter()
    first_bucket: datetime | None = None
    last_bucket: datetime | None = None

    with path.open("r", encoding="utf-8", errors="replace") as log_file:
        for line in log_file:
            entry = parse_line(line)
            if entry is None or not is_error_level(entry.level):
                continue

            bucket_start = align_bucket(entry.timestamp, bucket_seconds)
            counts[bucket_start] += 1
            if first_bucket is None or bucket_start < first_bucket:
                first_bucket = bucket_start
            if last_bucket is None or bucket_start > last_bucket:
                last_bucket = bucket_start

    buckets: list[dict[str, object]] = []
    if first_bucket is not None and last_bucket is not None:
        bucket_start = first_bucket
        while bucket_start <= last_bucket:
            buckets.append(
                {"start": bucket_start.isoformat(), "error_count": counts[bucket_start]}
            )
            bucket_start += timedelta(seconds=bucket_seconds)

    return {"file": str(path), "bucket_size": bucket_size, "buckets": buckets}
