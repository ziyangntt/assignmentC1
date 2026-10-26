import json
from pathlib import Path

from logscope.cli import main


def test_summary_json_output(capsys, tmp_path: Path) -> None:
    log_file = tmp_path / "app.log"
    log_file.write_text("2026-10-01 09:00:00 INFO Started\n", encoding="utf-8")

    assert main(["summary", str(log_file), "--format", "json"]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output["well_formed"] == 1


def test_timeline_markdown_writes_requested_file(capsys, tmp_path: Path) -> None:
    log_file = tmp_path / "app.log"
    report_file = tmp_path / "report.md"
    log_file.write_text("2026-10-01 09:00:00 ERROR Failed\n", encoding="utf-8")

    assert main(["timeline", str(log_file), "--format", "md", "--output", str(report_file)]) == 0

    assert capsys.readouterr().out.strip() == str(report_file)
    assert "# LogScope Timeline" in report_file.read_text(encoding="utf-8")


def test_grep_text_output(capsys, tmp_path: Path) -> None:
    log_file = tmp_path / "app.log"
    log_file.write_text("2026-10-01 09:00:00 ERROR Failed\n", encoding="utf-8")

    assert main(["grep", str(log_file), "--level", "ERROR"]) == 0

    assert "2026-10-01T09:00:00 ERROR Failed" in capsys.readouterr().out


def test_missing_file_returns_file_error(capsys, tmp_path: Path) -> None:
    assert main(["summary", str(tmp_path / "missing.log")]) == 2

    assert "No such file" in capsys.readouterr().err
