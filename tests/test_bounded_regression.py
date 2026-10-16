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
