# LogScope — Specification

## 1. Purpose

A CLI tool for the operations team to summarise, visualise, and filter application
logs after an incident, directly from the terminal — no dashboard required.

## 2. Distribution

- Language: Python 3.10+ (stdlib only, no mandatory third-party deps).
- Invoked as `logscope <command> <file> [options]`.
- Must work as a single installable CLI (`pip install .` → `logscope` on PATH) or
  as a plain script (`python -m logscope ...`).

## 3. Input Log Format

- Plain text, one entry per line (entries do **not** span multiple lines in v1).
- Expected line shape: `TIMESTAMP LEVEL MESSAGE`, e.g.
  `2026-10-01 09:03:12 ERROR Connection refused to db-primary`
- Accepted timestamp formats: `YYYY-MM-DD HH:MM:SS[.ffffff]`, optionally with a
  `T` separator and/or trailing `Z`/`+HH:MM` offset (ISO-8601-ish). At least one
  parser must succeed for the line to be considered well-formed.
- Accepted levels (case-insensitive): `INFO`, `WARN`/`WARNING`, `ERROR`
  (also tolerate `DEBUG`, `CRITICAL`/`FATAL` — bucket `CRITICAL`/`FATAL` into
  `ERROR` for the error-focused commands, but keep original label in `summary`'s
  level breakdown if easily derived).

## 4. Commands

### 4.1 `logscope summary <file>`

Single pass over the file. Reports:
- Total line count, well-formed count, malformed count.
- Counts by level (INFO / WARN / ERROR / others encountered).
- Top 5 most frequent error messages (message text, normalised by stripping
  variable-looking tokens is a nice-to-have, not required for v1) with counts.
- First and last timestamp seen among well-formed lines.

### 4.2 `logscope timeline <file> --bucket 15m`

- Buckets well-formed lines by timestamp into fixed-size windows aligned to the
  start of the first bucket (e.g. floor to the bucket size).
- `--bucket` accepts `<N><unit>` where unit ∈ `{s, m, h}` (e.g. `30s`, `15m`, `1h`).
  Default: `15m`.
- Counts **errors only** per bucket (ERROR + CRITICAL/FATAL) by default.
- Text output: one line per bucket → `<bucket-start>  <bar>  <count>`, bar made
  of a repeated character (e.g. `#`) scaled to terminal-friendly width (cap bar
  length, e.g. 50 chars, and scale proportionally to the max bucket count).
- Buckets with zero errors are still listed (no gaps), unless the whole file has
  zero errors, in which case print a "no errors found" message.

### 4.3 `logscope grep <file> --level ERROR --since "2026-10-01 09:00"`

- Streams matching lines to stdout (or to the report file in md/json mode).
- `--level` filters by one or more levels (repeatable or comma-separated:
  `--level ERROR,WARN`). Omit to match all levels.
- `--since "<timestamp>"` / `--until "<timestamp>"` (optional, symmetric) filter
  by timestamp range, inclusive of `--since`, exclusive or inclusive of
  `--until` (be consistent, document as inclusive).
- `--limit N` optional cap on number of results (no cap by default).
- Malformed lines are never returned by grep (they have no timestamp/level to
  match against).

## 5. Global/shared options

- `--format json|md` on every command (default: human-readable text to stdout).
  - `json`: machine-readable structured output to stdout.
  - `md`: writes a Markdown report file (default name
    `logscope-<command>-<timestamp>.md` in CWD, overridable with `--output`)
    AND prints the file path to stdout.
- `--output <path>` optional explicit output path for `md`/`json` (when set,
  `json` is also allowed to write to a file instead of stdout).
- `-h/--help` on the top-level command and every subcommand.
- Exit codes: `0` success, `1` usage/argument error, `2` file not found /
  unreadable, `3` unexpected internal error (never a raw traceback for expected
  failure modes).

## 6. Performance & robustness constraints

- **Streaming only.** Must process a 100 MB+ log file without loading it fully
  into memory: read line-by-line (e.g. iterate the file object directly or in
  fixed-size chunks), using O(1)–O(bucket/top-N) memory relative to file size,
  not O(file size).
- Single pass per command (no re-reading the file for the same invocation)
  wherever feasible; `summary` needs only one pass (reservoir/counter style
  aggregation, e.g. `collections.Counter` + heap/`Counter.most_common` for
  top 5).
- **Malformed line handling:** a line that doesn't match the expected
  `TIMESTAMP LEVEL MESSAGE` shape (unparsable timestamp, missing level, empty
  line, binary garbage, truncated last line, etc.) is counted in a
  `malformed` counter and **skipped** — it must never raise an unhandled
  exception or abort the run. Encoding errors on individual lines are handled
  the same way (replace/skip with a decode-error-tolerant read mode).
- The tool must complete on a 100 MB file in a reasonable time on a laptop
  (target: well under a minute for `summary`/`timeline`; `grep` is streaming
  and bounded by `--limit` when set).

## 7. Output contracts

### `summary` JSON shape
```json
{
  "file": "app.log",
  "total_lines": 123456,
  "well_formed": 123000,
  "malformed": 456,
  "levels": {"INFO": 100000, "WARN": 20000, "ERROR": 3000},
  "top_errors": [{"message": "Connection refused to db-primary", "count": 42}],
  "first_timestamp": "2026-10-01T08:00:00",
  "last_timestamp": "2026-10-01T23:59:59"
}
```

### `timeline` JSON shape
```json
{
  "file": "app.log",
  "bucket_size": "15m",
  "buckets": [{"start": "2026-10-01T09:00:00", "error_count": 7}]
}
```

### `grep` JSON shape
```json
{
  "file": "app.log",
  "filters": {"level": ["ERROR"], "since": "2026-10-01T09:00:00", "until": null},
  "match_count": 12,
  "matches": [{"timestamp": "2026-10-01T09:03:12", "level": "ERROR", "message": "..."}]
}
```

`md` output mirrors the same data as a readable report (headings, tables,
fenced code block for the timeline bar chart).

## 8. Out of scope (v1)

- Multi-line stack traces / log entries spanning multiple lines.
- Live/follow mode (`tail -f`-style).
- Log formats other than the one described in §3 (e.g. JSON-lines logs) —
  may be added later behind a `--log-format` flag.
- Remote/compressed files (`.gz`, URLs).

## 9. Testing requirements

- Unit tests for: line parser (valid/invalid cases), bucket alignment math,
  top-5 aggregation, level normalisation, since/until filtering boundaries.
- At least one test that synthesises a large file (or mocks the read loop) to
  assert memory-safe streaming behaviour (no `.read()`/`.readlines()` of the
  whole file).
- A fixture log file with a deliberate mix of well-formed and malformed lines
  used across `summary`, `timeline`, and `grep` tests.
