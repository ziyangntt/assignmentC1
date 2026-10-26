from pathlib import Path

from logscope.commands.timeline import timeline_file


def test_timeline_counts_errors_and_includes_zero_gap(tmp_path: Path) -> None:
    log_file = tmp_path / "timeline.log"
    log_file.write_text(
        "\n".join(
            [
                "2026-10-01 09:01:00 ERROR First error",
                "2026-10-01 09:14:00 FATAL Second error",
                "2026-10-01 09:31:00 ERROR Third error",
                "2026-10-01 09:32:00 INFO Ignored",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    timeline = timeline_file(log_file, "15m")

    assert timeline["buckets"] == [
        {"start": "2026-10-01T09:00:00", "error_count": 2},
        {"start": "2026-10-01T09:15:00", "error_count": 0},
        {"start": "2026-10-01T09:30:00", "error_count": 1},
    ]


def test_timeline_returns_no_buckets_when_no_errors(tmp_path: Path) -> None:
    log_file = tmp_path / "no-errors.log"
    log_file.write_text("2026-10-01 09:00:00 INFO Started\n", encoding="utf-8")

    assert timeline_file(log_file)["buckets"] == []
