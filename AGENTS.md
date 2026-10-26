# Project Instructions — LogScope

These are standing instructions for aXet.code when working in this repository.
Read `SPEC.md` first — it is the source of truth for behaviour. This file is
about *how* to build/run/test, not *what* to build.

## What this project is

A Python CLI (`logscope`) that summarises application logs after an incident:
`summary`, `timeline`, `grep` subcommands, `--format json|md`, streaming-only
processing of large (100 MB+) log files, malformed lines never crash the tool.

## Layout

```
logscope/
  __init__.py
  __main__.py        # `python -m logscope`
  cli.py              # argparse wiring, dispatch to commands
  parser.py           # line parsing: timestamp/level/message, malformed detection
  timeutil.py         # bucket size parsing ("15m" -> seconds), bucket alignment
  commands/
    summary.py
    timeline.py
    grep.py
  report.py            # shared json/md rendering + --output handling
tests/
  fixtures/
    sample.log         # mixed well-formed + malformed lines
  test_parser.py
  test_timeutil.py
  test_summary.py
  test_timeline.py
  test_grep.py
pyproject.toml
SPEC.md
AGENTS.md
README.md
```

## Build / run / test commands

- Run locally without installing: `python -m logscope summary app.log`
- Install editable: `pip install -e .` then `logscope summary app.log`
- Run tests: `pytest -q`
- Run a single test file: `pytest -q tests/test_parser.py`
- Lint/format: none configured yet — do not add new tooling unless asked.

## Hard constraints (do not regress these)

1. **Streaming only.** Never call `.read()` / `.readlines()` on the whole log
   file. Iterate the file object line-by-line (or fixed-size chunks). Any
   command must be able to process a 100 MB+ file without loading it fully
   into memory.
2. **Malformed lines never crash the tool.** Wrap per-line parsing in
   try/except (or validate before use); on failure, increment a `malformed`
   counter and continue. No unhandled exception should ever propagate out of
   normal log-content issues (bad timestamp, missing level, empty line, stray
   encoding error, truncated final line).
3. **Single pass per command** where the spec allows it (`summary`,
   `timeline` especially) — don't re-read the file multiple times for one
   invocation.
4. **`--format json|md` must exist on every command** and follow the JSON
   shapes documented in `SPEC.md` §7 exactly (keys and nesting). `md` writes a
   report file and also prints the resulting path to stdout.
5. **Exit codes** per `SPEC.md` §5 (`0` ok, `1` usage error, `2` file error,
   `3` internal error) — keep this consistent across subcommands.

## Coding conventions

- Python 3.10+, stdlib only unless the user explicitly approves a dependency.
- Use `argparse` with subparsers for the CLI; keep each subcommand's argument
  definitions next to its command module, wired up in `cli.py`.
- Keep parsing (`parser.py`) and time-bucket math (`timeutil.py`) pure and
  unit-testable, independent of argparse/CLI concerns.
- No code comments unless explicitly requested.
- Match existing naming/style once code exists — don't rename things
  gratuitously.

## Testing expectations

- Implement in this order: parser, summary, timeline, grep, then shared output
  formats and CLI wiring.
- After each implementation stage, run `pytest -q` and resolve failures before
  continuing.
- When commits are requested, create one focused commit after each verified
  stage; do not commit unverified work.
- After any change to `parser.py`, `timeutil.py`, or a command module, run
  `pytest -q` before considering the task done.
- When adding a new parsing edge case, add a corresponding line to
  `tests/fixtures/sample.log` and a targeted unit test rather than only
  testing through the CLI.
- Add a regression test whenever a bug is fixed.

## Things to avoid

- Don't add a dashboard/web UI, `tail -f` live mode, `.gz`/remote file support,
  or multi-line log entry handling — all explicitly out of scope per
  `SPEC.md` §8.
- Don't introduce third-party dependencies (e.g. pandas, click, rich) without
  asking first — this tool is meant to run anywhere with just stdlib.
- Don't weaken the streaming/memory constraints for convenience (e.g. sorting
  all lines in memory, building a full list of every match before printing).
