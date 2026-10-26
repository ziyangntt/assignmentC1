from pathlib import Path

from logscope.commands.summary import summarize_file


FIXTURE = Path(__file__).parent / "fixtures" / "sample.log"


def test_summary_counts_entries_and_levels() -> None:
    summary = summarize_file(FIXTURE)

    assert summary["total_lines"] == 6
    assert summary["well_formed"] == 5
    assert summary["malformed"] == 1
    assert summary["levels"] == {
        "INFO": 1,
        "ERROR": 1,
        "WARN": 1,
        "CRITICAL": 1,
        "DEBUG": 1,
    }
    assert summary["top_errors"] == [{"message": "Connection refused", "count": 2}]
    assert summary["first_timestamp"] == "2026-10-01T09:00:00"
    assert summary["last_timestamp"] == "2026-10-01T09:04:00"


def test_summary_limits_errors_to_top_five(tmp_path: Path) -> None:
    log_file = tmp_path / "errors.log"
    log_file.write_text(
        "".join(
            f"2026-10-01 09:00:0{index} ERROR Error {index}\n"
            for index in range(6)
        ),
        encoding="utf-8",
    )

    summary = summarize_file(log_file)

    assert len(summary["top_errors"]) == 5


def test_summary_streams_file_without_reading_all_content(tmp_path: Path) -> None:
    log_file = tmp_path / "streaming.log"
    log_file.write_text("2026-10-01 09:00:00 INFO Started\n", encoding="utf-8")

    summary = summarize_file(log_file)

    assert summary["well_formed"] == 1
