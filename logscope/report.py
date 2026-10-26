from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, cast


def write_json(data: dict[str, object], output: str | None = None) -> str | None:
    rendered = json.dumps(data, indent=2) + "\n"
    if output is None:
        print(rendered, end="")
        return None
    Path(output).write_text(rendered, encoding="utf-8")
    return output


def render_text(command: str, data: dict[str, object]) -> str:
    if command == "summary":
        errors = cast(list[dict[str, object]], data["top_errors"])
        lines = [
            f"File: {data['file']}",
            f"Lines: {data['total_lines']} total, {data['well_formed']} well-formed, {data['malformed']} malformed",
            f"Levels: {data['levels']}",
            f"First timestamp: {data['first_timestamp']}",
            f"Last timestamp: {data['last_timestamp']}",
            "Top errors:",
        ]
        lines.extend(f"  {error['count']}  {error['message']}" for error in errors)
        return "\n".join(lines)
    if command == "timeline":
        buckets = cast(list[dict[str, object]], data["buckets"])
        if not buckets:
            return "No errors found"
        maximum = max(cast(int, bucket["error_count"]) for bucket in buckets)
        lines = []
        for bucket in buckets:
            count = cast(int, bucket["error_count"])
            bar_length = max(1, round(count / maximum * 50)) if count else 0
            lines.append(f"{bucket['start']}  {'#' * bar_length}  {count}")
        return "\n".join(lines)
    matches = cast(list[dict[str, str]], data["matches"])
    return "\n".join(
        f"{match['timestamp']} {match['level']} {match['message']}" for match in matches
    )


def render_markdown(command: str, data: dict[str, object]) -> str:
    if command == "summary":
        levels = cast(dict[str, int], data["levels"])
        errors = cast(list[dict[str, object]], data["top_errors"])
        error_rows = "\n".join(
            f"| {error['message']} | {error['count']} |" for error in errors
        ) or "| None | 0 |"
        return "\n".join(
            [
                "# LogScope Summary",
                "",
                f"- File: `{data['file']}`",
                f"- Total lines: {data['total_lines']}",
                f"- Well-formed lines: {data['well_formed']}",
                f"- Malformed lines: {data['malformed']}",
                f"- First timestamp: {data['first_timestamp']}",
                f"- Last timestamp: {data['last_timestamp']}",
                "",
                "## Levels",
                "",
                "| Level | Count |",
                "| --- | ---: |",
                *[f"| {level} | {count} |" for level, count in levels.items()],
                "",
                "## Top errors",
                "",
                "| Message | Count |",
                "| --- | ---: |",
                error_rows,
                "",
            ]
        )
    if command == "timeline":
        return "\n".join(
            ["# LogScope Timeline", "", "```text", render_text(command, data), "```", ""]
        )
    matches = cast(list[dict[str, str]], data["matches"])
    return "\n".join(
        [
            "# LogScope Grep",
            "",
            f"- File: `{data['file']}`",
            f"- Matches: {data['match_count']}",
            "",
            "| Timestamp | Level | Message |",
            "| --- | --- | --- |",
            *[
                f"| {match['timestamp']} | {match['level']} | {match['message']} |"
                for match in matches
            ],
            "",
        ]
    )


def write_markdown(command: str, data: dict[str, object], output: str | None = None) -> str:
    target = Path(output) if output else Path(f"logscope-{command}-{datetime.now():%Y%m%d-%H%M%S}.md")
    target.write_text(render_markdown(command, data), encoding="utf-8")
    print(target)
    return str(target)


def emit(command: str, data: dict[str, object], output_format: str, output: str | None) -> None:
    if output_format == "json":
        write_json(data, output)
    elif output_format == "md":
        write_markdown(command, data, output)
    else:
        print(render_text(command, data))
