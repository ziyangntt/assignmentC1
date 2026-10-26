from datetime import datetime

import pytest

from logscope.timeutil import align_bucket, parse_bucket_size


@pytest.mark.parametrize(
    ("value", "expected"),
    [("30s", 30), ("15m", 900), ("1h", 3600), ("12h", 43200)],
)
def test_parse_bucket_size(value: str, expected: int) -> None:
    assert parse_bucket_size(value) == expected


@pytest.mark.parametrize("value", ["0m", "15", "m", "-1h", "1d"])
def test_parse_bucket_size_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        parse_bucket_size(value)


def test_align_bucket_floors_to_bucket_start() -> None:
    timestamp = datetime(2026, 10, 1, 9, 17, 42)

    assert align_bucket(timestamp, 900) == datetime(2026, 10, 1, 9, 15)
