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
