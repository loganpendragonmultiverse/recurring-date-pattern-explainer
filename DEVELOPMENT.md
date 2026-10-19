# Development contract

Translate common RRULE recurrence patterns into plain language and preview dates.

Version 1.1 corrects month/leap/interval behavior and adds bounded `UNTIL` previews. Preserve the documented RFC 5545 and timezone limitations.

Preserve deterministic, source-safe behavior and the interpretation boundary documented in the README. Every feature release must update tests, version metadata, changelog, README claims, repository metadata, release assets, and the Forge catalog together.

## 1.1.1 — 2026-10-16

RRULE parsing rejects unknown keys, duplicate keys (case-insensitively), empty or malformed key=value fragments and invalid BYDAY tokens before generating dates or writing output. BYDAY accepts only the unnumbered weekday tokens MO,TU,WE,TH,FR,SA,SU; ordinal weekdays are unsupported. The existing DAILY/WEEKLY/MONTHLY/YEARLY subset, interval/count bounds and ISO/RFC UNTIL fixtures remain supported. This is not full RFC 5545 validation and does not model DST rules.

DAILY rules now check weekday reachability using gcd(INTERVAL, 7) before iteration. An unreachable BYDAY without UNTIL fails with an actionable error rather than iterating until datetime overflow; with UNTIL it returns an empty, explicitly truncated preview. Reachable daily rules retain their existing dates. This correction does not extend the supported RFC or DST subset.

Preview generation stops before advancing once COUNT, preview_count or the inclusive UNTIL boundary has been satisfied. Remaining advances outside Python datetime's supported range fail with an actionable error and produce no CLI output file, including very large intervals. A one-result preview at 9999-12-31 remains valid.

## 1.1.2 validation

The bounded regression suite covers strict input shapes, frequency wording,
start-anchored weekly dates, very large intervals, literal report rendering,
exclusive output creation and closed stdout. Run the documented Ruff, mypy,
pytest and build commands before review. Validate both wheel and source archive
in a clean environment outside the checkout; use their packaged sample and
confirm all four project documents are included. Python 3.10 is the minimum;
Windows and macOS behavior also depends on the repository CI matrix.
