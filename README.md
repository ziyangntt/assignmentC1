# LogScope

LogScope is a Python 3.10+ command-line tool for summarising, visualising, and filtering application logs after an incident.

## Implementation plan

The implementation is delivered in the following order. Each step must be completed and verified with `pytest -q` before creating its commit.

### 1. Parser

- Implement streaming, line-by-line log parsing.
- Accept the timestamp formats and log levels defined in `SPEC.md`.
- Normalize levels where required while retaining the original summary breakdown.
- Treat invalid timestamps, missing fields, empty lines, encoding issues, and other malformed input as non-fatal.
- Add parser tests for valid and invalid input cases.

**Verification:** `pytest -q`  
**Commit:** parser implementation and its tests.

### 2. Summary

- Implement `logscope summary <file>` as a single-pass operation.
- Report total, well-formed, and malformed line counts.
- Aggregate counts by level, top five error messages, and first/last valid timestamps.
- Keep memory proportional to the aggregation data rather than file size.
- Add tests using the shared mixed-validity fixture and top-five aggregation cases.

**Verification:** `pytest -q`  
**Commit:** summary implementation and its tests.

### 3. Timeline

- Implement bucket-size parsing for seconds, minutes, and hours.
- Implement fixed-window timestamp alignment and `logscope timeline <file> --bucket <N><unit>`.
- Count `ERROR`, `CRITICAL`, and `FATAL` entries as errors.
- Emit consecutive zero-count buckets between the first and last error bucket; report no errors clearly when appropriate.
- Add tests for bucket parsing, alignment, zero gaps, and error aggregation.

**Verification:** `pytest -q`  
**Commit:** timeline implementation and its tests.

### 4. Grep

- Implement streaming `logscope grep <file>` filtering.
- Support repeatable or comma-separated `--level`, inclusive `--since` and `--until`, and `--limit`.
- Never return malformed lines.
- Stop streaming early once a limit is reached.
- Add tests for level selection, date boundaries, limit behavior, and malformed input exclusion.

**Verification:** `pytest -q`  
**Commit:** grep implementation and its tests.

### 5. Output formats and CLI wiring

- Wire all commands through `argparse` with help text and the required exit codes.
- Implement human-readable output, JSON output matching `SPEC.md` section 7, and Markdown reports.
- Support `--output` for Markdown and JSON output.
- Ensure Markdown output writes the report and prints its path.
- Run the complete suite after all integrations.

**Verification:** `pytest -q`  
**Commit:** CLI and output-format integration.

## Constraints

- Use Python 3.10+ and the standard library only.
- Process logs by streaming; never load an entire log file with `.read()` or `.readlines()`.
- Keep malformed log lines non-fatal.
- Preserve a single pass per command wherever the specification permits.
- Follow the exact JSON contracts and exit-code behavior in `SPEC.md`.

