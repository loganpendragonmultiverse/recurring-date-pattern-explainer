# Recurring Date Pattern Explainer

[![CI](https://github.com/loganpendragonmultiverse/recurring-date-pattern-explainer/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/recurring-date-pattern-explainer/actions/workflows/ci.yml)

Translate common RRULE recurrence patterns into plain language and preview dates. The command uses explicit UTF-8 JSON input and produces reviewable JSON or Markdown output.

## Three-minute start

```bash
python -m pip install .
rrule-explain examples/sample.json
rrule-explain examples/sample.json --format json --output report.json
```

The example documents the input shape. Version 1.1 correctly preserves month-end intent, clips leap days only when needed, honors interval weeks with `BYDAY`, and supports ISO or RFC 5545 `UNTIL` values with explicit truncation evidence. Preview counts are bounded from 1 to 1,000. Existing report files are never overwritten. Source inputs are read-only except where the documented purpose explicitly creates a new output artifact.

## Input and date semantics

Input must be a JSON object with text `start` (an ISO date or datetime) and text
`rrule`. Optional `preview_count` is an integer from 1 to 1,000, default 10;
strings, booleans and fractional numbers are rejected. `COUNT` further limits
that preview. Unknown RRULE keys and duplicate keys are errors.

Weeks with `BYDAY` use seven-day blocks anchored to `start`, rather than RFC
Monday week boundaries. For example, Wednesday 2026-10-21 with
`FREQ=WEEKLY;INTERVAL=2;BYDAY=MO;COUNT=3` previews October 26, November 9 and
November 23. Monthly and yearly rules advance the original day of month,
clipping only when necessary (January 31 → February 28 → March 31).
`BYDAY` filters those monthly/yearly dates; it does not expand all matching
weekdays in each month or year. An unsatisfiable filter without `UNTIL` fails
at the supported datetime boundary rather than returning a partial report.

`UNTIL` is inclusive. A date-only value means midnight, so a later time on
that date is excluded. Start and UNTIL must both be timezone-aware or both
naive; fixed offsets are preserved, without named-zone or DST calculations.
This is a deterministic preview subset, not an RFC-complete calendar engine.

## Installing a release

Download the wheel from the GitHub release, then install the actual downloaded
filename with `python -m pip install /path/to/the-downloaded.whl`. The command
`rrule-explain --help` verifies installation. A minimal input file is:

```json
{"start": "2026-10-21", "rrule": "FREQ=DAILY;COUNT=3"}
```

Save it as `input.json` and run `rrule-explain input.json --format json`.
Wheel installs include the four project documents, license, contribution guide
and sample under `share/doc/recurring-date-pattern-explainer` in the Python
environment. Source archives include those documents and `examples/sample.json`.

Reports require a new output path. Existing files, directories and symlinks are
refused, including a path pointing to the input. Errors return status 2;
invalid input produces no report. A failed write can leave a partial new file,
which should be inspected before sharing. Closed output pipes fail cleanly.

## Privacy and platforms

The tool runs locally and does not upload input or include telemetry. Python 3.10 or newer is supported on Windows, macOS, and Linux.

## Interpretation boundary

The supported subset covers DAILY, WEEKLY, MONTHLY, and YEARLY with INTERVAL, BYDAY, COUNT, and UNTIL. It preserves supplied timezone-aware datetimes but does not calculate timezone rules, DST shifts, or the complete RFC 5545 grammar.

## Development

```bash
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
mypy src
pytest
python -m build
```

The project is feature-complete for its documented v1 scope. Maintenance focuses on correctness, security, compatibility, and well-supported input improvements.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).

## 1.1.1 — 2026-10-16

RRULE parsing rejects unknown keys, duplicate keys (case-insensitively), empty or malformed key=value fragments and invalid BYDAY tokens before generating dates or writing output. BYDAY accepts only the unnumbered weekday tokens MO,TU,WE,TH,FR,SA,SU; ordinal weekdays are unsupported. The existing DAILY/WEEKLY/MONTHLY/YEARLY subset, interval/count bounds and ISO/RFC UNTIL fixtures remain supported. This is not full RFC 5545 validation and does not model DST rules.

DAILY rules now check weekday reachability using gcd(INTERVAL, 7) before iteration. An unreachable BYDAY without UNTIL fails with an actionable error rather than iterating until datetime overflow; with UNTIL it returns an empty, explicitly truncated preview. Reachable daily rules retain their existing dates. This correction does not extend the supported RFC or DST subset.

Preview generation stops before advancing once COUNT, preview_count or the inclusive UNTIL boundary has been satisfied. Remaining advances outside Python datetime's supported range fail with an actionable error and produce no CLI output file, including very large intervals. A one-result preview at 9999-12-31 remains valid.
