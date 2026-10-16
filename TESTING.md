# Testing

Run the repository CI commands: ruff format --check ., ruff check ., mypy src, pytest and python -m build.

## 1.1.1 — 2026-10-16

RRULE parsing rejects unknown keys, duplicate keys (case-insensitively), empty or malformed key=value fragments and invalid BYDAY tokens before generating dates or writing output. BYDAY accepts only the unnumbered weekday tokens MO,TU,WE,TH,FR,SA,SU; ordinal weekdays are unsupported. The existing DAILY/WEEKLY/MONTHLY/YEARLY subset, interval/count bounds and ISO/RFC UNTIL fixtures remain supported. This is not full RFC 5545 validation and does not model DST rules.

Regression tests use synthetic inputs and disposable trees. Run the complete suite and inspect built wheel/source documentation before preparing a draft PR.

DAILY rules now check weekday reachability using gcd(INTERVAL, 7) before iteration. An unreachable BYDAY without UNTIL fails with an actionable error rather than iterating until datetime overflow; with UNTIL it returns an empty, explicitly truncated preview. Reachable daily rules retain their existing dates. This correction does not extend the supported RFC or DST subset.

Preview generation stops before advancing once COUNT, preview_count or the inclusive UNTIL boundary has been satisfied. Remaining advances outside Python datetime's supported range fail with an actionable error and produce no CLI output file, including very large intervals. A one-result preview at 9999-12-31 remains valid.
