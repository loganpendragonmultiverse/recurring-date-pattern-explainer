import json
from pathlib import Path

import pytest

from recurrence_explainer.cli import main
from recurrence_explainer.core import PROJECT, analyze, render_json, render_markdown


def test_representative_sample_has_expected_result():
    data = json.loads(
        (Path(__file__).parents[1] / "examples" / "sample.json").read_text(encoding="utf-8")
    )
    report = analyze(data)
    assert report["version"] == 1 and report["project"] == PROJECT
    assert len(report["occurrences"]) == 4 and "MO, WE" in report["explanation"]
    assert f'"project": "{PROJECT}"' in render_json(report)
    assert PROJECT.replace("-", " ").title() in render_markdown(report)


def test_missing_required_input_is_rejected():
    with pytest.raises(ValueError):
        analyze({})


def test_cli_json_and_output_safety(tmp_path, capsys):
    source = Path(__file__).parents[1] / "examples" / "sample.json"
    assert main([str(source), "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["project"] == PROJECT
    output = tmp_path / "report.md"
    output.write_text("keep", encoding="utf-8")
    assert main([str(source), "--output", str(output)]) == 2


@pytest.mark.parametrize(
    ("rrule", "expected"),
    [
        ("FREQ=DAILY;INTERVAL=2;COUNT=2", "2026-08-05T09:00:00"),
        ("FREQ=WEEKLY;INTERVAL=2;COUNT=2", "2026-08-17T09:00:00"),
        ("FREQ=MONTHLY;COUNT=2", "2026-09-03T09:00:00"),
        ("FREQ=YEARLY;COUNT=2", "2027-08-03T09:00:00"),
    ],
)
def test_supported_frequency_previews(rrule, expected):
    report = analyze({"rrule": rrule, "start": "2026-08-03T09:00:00", "preview_count": 2})
    assert report["occurrences"][-1] == expected


def test_invalid_frequency_and_interval():
    with pytest.raises(ValueError, match="supported FREQ"):
        analyze({"rrule": "FREQ=HOURLY", "start": "2026-08-03T09:00:00"})
    with pytest.raises(ValueError, match="INTERVAL"):
        analyze({"rrule": "FREQ=DAILY;INTERVAL=0", "start": "2026-08-03T09:00:00"})
