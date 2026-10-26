from datetime import datetime

from logscope.parser import is_error_level, normalize_level, parse_line, parse_timestamp


def test_parse_line_accepts_space_separated_timestamp() -> None:
    entry = parse_line("2026-10-01 09:03:12 ERROR Connection refused")

    assert entry is not None
    assert entry.timestamp == datetime(2026, 10, 1, 9, 3, 12)
    assert entry.level == "ERROR"
    assert entry.message == "Connection refused"


def test_parse_line_accepts_iso_timestamp_and_offset() -> None:
    entry = parse_line("2026-10-01T09:03:12Z warning Cache miss")

    assert entry is not None
    assert entry.timestamp == datetime(2026, 10, 1, 9, 3, 12)
    assert entry.level == "WARN"
    assert entry.message == "Cache miss"


def test_parse_line_accepts_fractional_seconds() -> None:
    entry = parse_line("2026-10-01 09:03:12.123456 INFO Started")

    assert entry is not None
    assert entry.timestamp.microsecond == 123456


def test_parse_line_returns_none_for_malformed_input() -> None:
    assert parse_line("") is None
    assert parse_line("not a log line") is None
    assert parse_line("2026-99-01 09:03:12 ERROR Invalid timestamp") is None


def test_level_normalization_and_error_detection() -> None:
    assert normalize_level("fatal") == "CRITICAL"
    assert normalize_level("warning") == "WARN"
    assert is_error_level("ERROR")
    assert is_error_level("FATAL")
    assert not is_error_level("INFO")


def test_parse_timestamp_accepts_z_suffix() -> None:
    assert parse_timestamp("2026-10-01T09:03:12Z") == datetime(2026, 10, 1, 9, 3, 12)
