# Changelog

## [1.1.1] - 2026-10-16

RRULE parsing rejects unknown keys, duplicate keys (case-insensitively), empty or malformed key=value fragments and invalid BYDAY tokens before generating dates or writing output. BYDAY accepts only the unnumbered weekday tokens MO,TU,WE,TH,FR,SA,SU; ordinal weekdays are unsupported. The existing DAILY/WEEKLY/MONTHLY/YEARLY subset, interval/count bounds and ISO/RFC UNTIL fixtures remain supported. This is not full RFC 5545 validation and does not model DST rules.


## 1.1.0 - 2026-07-27

- Corrected month-end, leap-day, and interval-weekday recurrence previews.
- Added `UNTIL` support, preview bounds, timezone-awareness validation, and truncation evidence.

## 1.0.0 - 2026-07-26

- Released the first complete Recurring Date Pattern Explainer command-line workflow.
- Added deterministic reporting, representative examples, cross-platform tests, and explicit limitations.
