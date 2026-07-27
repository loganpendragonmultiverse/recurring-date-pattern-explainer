from __future__ import annotations

import calendar
import json
from datetime import datetime, timedelta
from typing import Any

PROJECT = "recurring-date-pattern-explainer"


def _require(data: dict[str, Any], key: str) -> Any:
    value = data.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"{key} is required")
    return value


def _recurrence(data: dict[str, Any]) -> dict[str, Any]:
    rule = {
        part.split("=", 1)[0].upper(): part.split("=", 1)[1]
        for part in str(_require(data, "rrule")).split(";")
        if "=" in part
    }
    frequency = rule.get("FREQ")
    if frequency not in {"DAILY", "WEEKLY", "MONTHLY", "YEARLY"}:
        raise ValueError("supported FREQ values are DAILY, WEEKLY, MONTHLY, and YEARLY")
    interval = int(rule.get("INTERVAL", "1"))
    if interval < 1:
        raise ValueError("INTERVAL must be positive")
    start = datetime.fromisoformat(str(_require(data, "start")))
    preview_count = int(data.get("preview_count", 10))
    if not 1 <= preview_count <= 1000:
        raise ValueError("preview_count must be between 1 and 1000")
    count = min(int(rule.get("COUNT", preview_count)), preview_count)
    if count < 1:
        raise ValueError("COUNT must be positive")
    until = None
    if "UNTIL" in rule:
        raw_until = rule["UNTIL"]
        try:
            until = datetime.fromisoformat(raw_until.replace("Z", "+00:00"))
        except ValueError:
            compact = raw_until.removesuffix("Z")
            expanded = (
                f"{compact[:4]}-{compact[4:6]}-{compact[6:8]}"
                if len(compact) == 8
                else f"{compact[:4]}-{compact[4:6]}-{compact[6:8]}T"
                f"{compact[9:11]}:{compact[11:13]}:{compact[13:15]}"
                if len(compact) == 15 and compact[8] == "T"
                else ""
            )
            if expanded:
                try:
                    until = datetime.fromisoformat(
                        expanded + ("+00:00" if raw_until.endswith("Z") else "")
                    )
                except ValueError:
                    pass
        if until is None:
            raise ValueError("UNTIL must be an ISO or RFC 5545 date/datetime")
        if (until.tzinfo is None) != (start.tzinfo is None):
            raise ValueError("UNTIL and start must use matching timezone awareness")
    weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}
    byday = [weekdays[item] for item in rule.get("BYDAY", "").split(",") if item in weekdays]
    occurrences: list[str] = []
    current = start
    desired_day = start.day
    desired_month = start.month
    stopped_by_until = False
    while len(occurrences) < count:
        if until is not None and current > until:
            stopped_by_until = True
            break
        week_index = (current.date() - start.date()).days // 7
        include = not byday or (
            current.weekday() in byday and (frequency != "WEEKLY" or week_index % interval == 0)
        )
        if include:
            occurrences.append(current.isoformat())
        if frequency == "DAILY" or (frequency == "WEEKLY" and byday):
            current += timedelta(days=1 if frequency == "WEEKLY" else interval)
        elif frequency == "WEEKLY":
            current += timedelta(weeks=interval)
        elif frequency == "MONTHLY":
            month = current.month - 1 + interval
            current = current.replace(
                year=current.year + month // 12,
                month=month % 12 + 1,
                day=min(
                    desired_day,
                    calendar.monthrange(current.year + month // 12, month % 12 + 1)[1],
                ),
            )
        else:
            year = current.year + interval
            current = current.replace(
                year=year,
                month=desired_month,
                day=min(desired_day, calendar.monthrange(year, desired_month)[1]),
            )
    phrase = f"Every {(interval if interval > 1 else '')} {frequency.lower().rstrip('ly')}".replace(
        "  ", " "
    )
    if byday:
        phrase += " on " + ", ".join((name for name, number in weekdays.items() if number in byday))
    if until is not None:
        phrase += f" until {until.isoformat()}"
    return {
        "rule": rule,
        "explanation": phrase + ".",
        "occurrences": occurrences,
        "stopped_by_until": stopped_by_until,
        "limitations": [
            "Preview uses local wall-clock datetimes and does not model timezone daylight-saving transitions."
        ],
    }


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    return {"version": 1, "project": PROJECT, **_recurrence(data)}


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# {report['project'].replace('-', ' ').title()} report", ""]
    for key, value in report.items():
        if key not in {"version", "project"}:
            lines.extend(
                [
                    f"## {key.replace('_', ' ').title()}",
                    "",
                    f"```json\n{json.dumps(value, indent=2, ensure_ascii=False, default=str)}\n```",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"
