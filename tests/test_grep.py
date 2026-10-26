from pathlib import Path

import pytest

from logscope.commands.grep import grep_file, parse_levels


def make_log(tmp_path: Path) -> Path:
    log_file = tmp_path / "grep.log"
    log_file.write_text(
        "\n".join(
            [
                "2026-10-01 09:00:00 INFO Started",
                "2026-10-01 09:01:00 ERROR Failed request",
                "malformed line",
                "2026-10-01 09:02:00 WARNING Slow request",
                "2026-10-01 09:03:00 ERROR Failed request again",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return log_file


def test_parse_levels_accepts_comma_separated_and_repeatable_values() -> None:
    assert parse_levels(["error,warn", "INFO"]) == {"ERROR", "WARN", "INFO"}


def test_grep_filters_by_levels(tmp_path: Path) -> None:
    result = grep_file(make_log(tmp_path), levels=["ERROR,WARN"])

    assert result["match_count"] == 3
    assert [entry["level"] for entry in result["matches"]] == ["ERROR", "WARN", "ERROR"]


def test_grep_applies_inclusive_timestamp_boundaries(tmp_path: Path) -> None:
    result = grep_file(
        make_log(tmp_path),
        since="2026-10-01 09:01:00",
        until="2026-10-01 09:02:00",
    )

    assert result["match_count"] == 2
    assert [entry["timestamp"] for entry in result["matches"]] == [
        "2026-10-01T09:01:00",
        "2026-10-01T09:02:00",
    ]


def test_grep_stops_at_limit_and_skips_malformed_lines(tmp_path: Path) -> None:
    result = grep_file(make_log(tmp_path), limit=2)

    assert result["match_count"] == 2
    assert [entry["message"] for entry in result["matches"]] == ["Started", "Failed request"]


def test_grep_rejects_negative_limit(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        grep_file(make_log(tmp_path), limit=-1)
