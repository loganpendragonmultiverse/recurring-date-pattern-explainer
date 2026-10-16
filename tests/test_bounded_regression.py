import json

import pytest

from recurrence_explainer.cli import main
from recurrence_explainer.core import analyze


@pytest.mark.parametrize(
    "rule",
    [
        "FREQ=DAILY;BYMONTH=2",
        "FREQ=DAILY;FREQ=WEEKLY",
        "FREQ=DAILY;COUNT=1;count=2",
        "FREQ=DAILY;BROKEN",
        "FREQ=DAILY;",
        ";FREQ=DAILY",
        "FREQ=DAILY;;COUNT=2",
        "FREQ=DAILY;=x",
        "FREQ=DAILY;COUNT=",
        "FREQ=DAILY;COUNT=1=2",
        "FREQ=WEEKLY;BYDAY=XX",
        "FREQ=WEEKLY;BYDAY=MO,XX",
        "FREQ=WEEKLY;BYDAY=1MO",
        "FREQ=WEEKLY;BYDAY=-1FR",
        "FREQ=WEEKLY;BYDAY=MO,",
        "FREQ=WEEKLY;BYDAY=,MO",
        "FREQ=WEEKLY;BYDAY=",
        "FREQ=DAILY;INTERVAL=1.5",
    ],
)
def test_invalid_rule_fails_before_iteration_or_output(rule, tmp_path, capsys):
    data = {"rrule": rule, "start": "2026-08-03T09:00:00"}
    with pytest.raises(ValueError):
        analyze(data)
    source, output = tmp_path / "input.json", tmp_path / "report.json"
    source.write_text(json.dumps(data))
    assert main([str(source), "--output", str(output)]) == 2
    captured = capsys.readouterr()
    assert not captured.out and "error:" in captured.err
    assert not output.exists()


@pytest.mark.parametrize("interval", [7, 14, 21])
def test_unreachable_daily_weekday_fails_before_iteration(interval):
    with pytest.raises(ValueError, match="BYDAY.*unreachable"):
        analyze(
            {"rrule": f"FREQ=DAILY;INTERVAL={interval};BYDAY=TU", "start": "2026-10-19T09:00:00"}
        )


def test_reachable_daily_weekdays_and_until_behavior_are_preserved():
    result = analyze(
        {"rrule": "FREQ=DAILY;INTERVAL=7;BYDAY=MO;COUNT=2", "start": "2026-10-19T09:00:00"}
    )
    assert result["occurrences"] == ["2026-10-19T09:00:00", "2026-10-26T09:00:00"]
    limited = analyze(
        {"rrule": "FREQ=DAILY;INTERVAL=7;BYDAY=TU;UNTIL=2026-11-01", "start": "2026-10-19"}
    )
    assert limited["occurrences"] == [] and limited["stopped_by_until"]
