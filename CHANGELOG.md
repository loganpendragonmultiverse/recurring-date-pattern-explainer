# Changelog

## 1.1.2 — 2026-10-19

- Correct daily explanation spelling and plural frequency wording.
- Reject malformed JSON root, start and preview-count shapes before output.
- Skip inactive weekly interval blocks while preserving start-anchored dates.
- Create reports exclusively, refuse symlinks and handle closed stdout cleanly.
- Clarify date/filter boundaries and include reusable documentation and examples in distributions.


## [1.1.1] - 2026-10-16

Preview generation stops before advancing once COUNT, preview_count or the inclusive UNTIL boundary has been satisfied. Remaining advances outside Python datetime's supported range fail with an actionable error and produce no CLI output file, including very large intervals. A one-result preview at 9999-12-31 remains valid.

DAILY rules now check weekday reachability using gcd(INTERVAL, 7) before iteration. An unreachable BYDAY without UNTIL fails with an actionable error rather than iterating until datetime overflow; with UNTIL it returns an empty, explicitly truncated preview. Reachable daily rules retain their existing dates. This correction does not extend the supported RFC or DST subset.

RRULE parsing rejects unknown keys, duplicate keys (case-insensitively), empty or malformed key=value fragments and invalid BYDAY tokens before generating dates or writing output. BYDAY accepts only the unnumbered weekday tokens MO,TU,WE,TH,FR,SA,SU; ordinal weekdays are unsupported. The existing DAILY/WEEKLY/MONTHLY/YEARLY subset, interval/count bounds and ISO/RFC UNTIL fixtures remain supported. This is not full RFC 5545 validation and does not model DST rules.


## 1.1.0 - 2026-07-27

- Corrected month-end, leap-day, and interval-weekday recurrence previews.
- Added `UNTIL` support, preview bounds, timezone-awareness validation, and truncation evidence.

## 1.0.0 - 2026-07-26

- Released the first complete Recurring Date Pattern Explainer command-line workflow.
- Added deterministic reporting, representative examples, cross-platform tests, and explicit limitations.
