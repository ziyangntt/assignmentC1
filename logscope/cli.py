from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from logscope.commands.grep import grep_file
from logscope.commands.summary import summarize_file
from logscope.commands.timeline import timeline_file
from logscope.report import emit


def add_output_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=("text", "json", "md"), default="text")
    parser.add_argument("--output")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="logscope")
    subparsers = parser.add_subparsers(dest="command", required=True)

    summary_parser = subparsers.add_parser("summary")
    summary_parser.add_argument("file")
    add_output_arguments(summary_parser)

    timeline_parser = subparsers.add_parser("timeline")
    timeline_parser.add_argument("file")
    timeline_parser.add_argument("--bucket", default="15m")
    add_output_arguments(timeline_parser)

    grep_parser = subparsers.add_parser("grep")
    grep_parser.add_argument("file")
    grep_parser.add_argument("--level", action="append")
    grep_parser.add_argument("--since")
    grep_parser.add_argument("--until")
    grep_parser.add_argument("--limit", type=int)
    add_output_arguments(grep_parser)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        arguments = parser.parse_args(argv)
    except SystemExit as error:
        return 0 if error.code == 0 else 1

    try:
        if arguments.command == "summary":
            data = summarize_file(arguments.file)
        elif arguments.command == "timeline":
            data = timeline_file(arguments.file, arguments.bucket)
        else:
            data = grep_file(
                arguments.file,
                levels=arguments.level,
                since=arguments.since,
                until=arguments.until,
                limit=arguments.limit,
            )
        emit(arguments.command, data, arguments.format, arguments.output)
    except OSError as error:
        print(f"logscope: {error}", file=sys.stderr)
        return 2
    except ValueError as error:
        print(f"logscope: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"logscope: internal error: {error}", file=sys.stderr)
        return 3
    return 0
