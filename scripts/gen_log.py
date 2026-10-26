from __future__ import annotations

import argparse
from pathlib import Path


LEVELS = ("INFO", "WARN", "ERROR", "DEBUG", "CRITICAL")
MESSAGES = {
    "INFO": "Request completed successfully",
    "WARN": "Request latency exceeded threshold",
    "ERROR": "Connection refused by db-primary",
    "DEBUG": "Cache lookup completed",
    "CRITICAL": "Database connection pool exhausted",
}


def build_line(index: int) -> str:
    level = LEVELS[index % len(LEVELS)]
    seconds = index % 86_400
    hour, remainder = divmod(seconds, 3_600)
    minute, second = divmod(remainder, 60)
    return f"2026-10-01 {hour:02}:{minute:02}:{second:02} {level} {MESSAGES[level]} request_id={index:09d}\n"


def generate_log(output: Path, target_bytes: int) -> int:
    written = 0
    index = 0
    with output.open("w", encoding="utf-8", newline="\n") as log_file:
        while written < target_bytes:
            line = build_line(index)
            log_file.write(line)
            written += len(line.encode("utf-8"))
            index += 1
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a synthetic LogScope log file.")
    parser.add_argument("output", type=Path, nargs="?", default=Path("synthetic-100mb.log"))
    parser.add_argument("--size-mb", type=int, default=100)
    arguments = parser.parse_args()
    if arguments.size_mb <= 0:
        parser.error("--size-mb must be positive")

    written = generate_log(arguments.output, arguments.size_mb * 1024 * 1024)
    print(f"Generated {arguments.output} ({written} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
