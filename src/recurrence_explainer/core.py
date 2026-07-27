from __future__ import annotations

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
    count = min(
        int(rule.get("COUNT", data.get("preview_count", 10))), int(data.get("preview_count", 10))
    )
    weekdays = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}
    byday = [weekdays[item] for item in rule.get("BYDAY", "").split(",") if item in weekdays]
    occurrences: list[str] = []
    current = start
    while len(occurrences) < count:
        include = not byday or current.weekday() in byday
        if include:
            occurrences.append(current.isoformat())
        if frequency == "DAILY" or (frequency == "WEEKLY" and byday):
            current += timedelta(days=1 if frequency == "WEEKLY" else interval)
        elif frequency == "WEEKLY":
            current += timedelta(weeks=interval)
        elif frequency == "MONTHLY":
            month = current.month - 1 + interval
            current = current.replace(
                year=current.year + month // 12, month=month % 12 + 1, day=min(current.day, 28)
            )
        else:
            current = current.replace(year=current.year + interval)
    phrase = f"Every {(interval if interval > 1 else '')} {frequency.lower().rstrip('ly')}".replace(
        "  ", " "
    )
    if byday:
        phrase += " on " + ", ".join((name for name, number in weekdays.items() if number in byday))
    return {
        "rule": rule,
        "explanation": phrase + ".",
        "occurrences": occurrences,
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
