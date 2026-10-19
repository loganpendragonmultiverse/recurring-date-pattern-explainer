import errno
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from recurrence_explainer.cli import main
from recurrence_explainer.core import analyze, render_markdown
from recurrence_explainer.output import write_report, write_stdout


@pytest.mark.parametrize("data", [None, [], 4, "x", True])
def test_invalid_roots_no_output(data, tmp_path, capsys):
    source = tmp_path / "input.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    before = source.read_bytes()
    output = tmp_path / "out.json"
    with pytest.raises(ValueError, match="JSON object"):
        analyze(data)
    assert main([str(source), "--output", str(output)]) == 2
    assert not output.exists() and source.read_bytes() == before
    captured = capsys.readouterr()
    assert not captured.out and "error:" in captured.err


@pytest.mark.parametrize("value", [None, True, False, 1.5, "2", [], {}, 0, 1001])
def test_strict_preview_counts(value, tmp_path, capsys):
    data = {"start": "2026-10-21", "rrule": "FREQ=DAILY", "preview_count": value}
    source = tmp_path / "input.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="preview_count"):
        analyze(data)
    assert main([str(source), "--output", str(tmp_path / "out")]) == 2
    assert not (tmp_path / "out").exists() and not capsys.readouterr().out


@pytest.mark.parametrize("start", [20261021, True, {}, ["2026-10-21"]])
def test_start_must_be_text(start):
    with pytest.raises(ValueError, match="start must"):
        analyze({"start": start, "rrule": "FREQ=DAILY"})


@pytest.mark.parametrize(
    "frequency,unit",
    [
        ("DAILY", "day"),
        ("WEEKLY", "week"),
        ("MONTHLY", "month"),
        ("YEARLY", "year"),
    ],
)
@pytest.mark.parametrize("interval", [1, 2])
def test_frequency_wording(frequency, unit, interval):
    report = analyze(
        {"start": "2026-10-21", "rrule": f"FREQ={frequency};INTERVAL={interval};COUNT=1"}
    )
    expected = f"Every {unit}." if interval == 1 else f"Every {interval} {unit}s."
    assert report["explanation"] == expected


@pytest.mark.parametrize("start", ["2026-10-21", "2026-10-25", "2026-10-26"])
@pytest.mark.parametrize("interval", [1, 2, 7])
@pytest.mark.parametrize("days", ["MO", "MO,WE,SU"])
def test_weekly_skip_matches_day_walking_reference(start, interval, days):
    beginning = datetime.fromisoformat(start)
    wanted = [{"MO": 0, "WE": 2, "SU": 6}[day] for day in days.split(",")]
    expected = []
    current = beginning
    while len(expected) < 8:
        if current.weekday() in wanted and ((current - beginning).days // 7) % interval == 0:
            expected.append(current.isoformat())
        current += timedelta(days=1)
    report = analyze(
        {"start": start, "rrule": f"FREQ=WEEKLY;INTERVAL={interval};BYDAY={days};COUNT=8"}
    )
    assert report["occurrences"] == expected


def test_huge_weekly_interval_is_bounded_and_until_is_respected(tmp_path):
    data = {"start": "2026-10-21", "rrule": "FREQ=WEEKLY;INTERVAL=999999999999999;BYDAY=MO;COUNT=2"}
    source = tmp_path / "input.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "recurrence_explainer", str(source)],
        check=False,
        capture_output=True,
        text=True,
        timeout=3,
    )
    assert result.returncode == 2 and "supported datetime range" in result.stderr
    assert not result.stdout
    data["rrule"] += ";UNTIL=2026-11-01"
    report = analyze(data)
    assert report["occurrences"] == ["2026-10-26T00:00:00"]
    assert report["stopped_by_until"] is True


@pytest.mark.parametrize(
    "rule,start,expected",
    [
        (
            "FREQ=MONTHLY;BYDAY=SU;UNTIL=2027-04-01",
            "2027-01-31",
            ["2027-01-31T00:00:00", "2027-02-28T00:00:00"],
        ),
        ("FREQ=YEARLY;BYDAY=FR;UNTIL=2026-03-01", "2024-02-29", ["2025-02-28T00:00:00"]),
    ],
)
def test_byday_filters_clipped_anchors(rule, start, expected):
    report = analyze({"start": start, "rrule": rule})
    assert report["occurrences"] == expected and report["stopped_by_until"]


def test_outputs_refuse_source_directory_and_dangling_symlink(tmp_path, capsys):
    source = tmp_path / "input.json"
    source.write_text('{"start":"2026-10-21","rrule":"FREQ=DAILY;COUNT=1"}', encoding="utf-8")
    before = source.read_bytes()
    for destination in [source, tmp_path]:
        assert main([str(source), "--output", str(destination)]) == 2
    assert source.read_bytes() == before
    link = tmp_path / "link"
    target = tmp_path / "missing"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation unavailable")
    assert main([str(source), "--output", str(link)]) == 2
    assert link.is_symlink() and not target.exists() and not capsys.readouterr().out


def test_racing_writer_is_preserved(tmp_path, monkeypatch):
    destination = tmp_path / "out"
    original = Path.open

    def racing_open(path, mode="r", *args, **kwargs):
        if path == destination and mode == "x":
            with original(path, "w", encoding="utf-8") as stream:
                stream.write("other writer")
        return original(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", racing_open)
    with pytest.raises(FileExistsError):
        write_report(destination, "new report")
    assert destination.read_text(encoding="utf-8") == "other writer"


def test_closed_pipe_has_controlled_status(tmp_path):
    source = tmp_path / "input.json"
    source.write_text('{"start":"2026-10-21","rrule":"FREQ=DAILY;COUNT=1"}', encoding="utf-8")
    reader, writer = os.pipe()
    os.close(reader)
    with os.fdopen(writer, "w") as stream:
        result = subprocess.run(
            [sys.executable, "-m", "recurrence_explainer", str(source)],
            check=False,
            stdout=stream,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3,
        )
    assert result.returncode == 2 and "error:" in result.stderr
    assert "Traceback" not in result.stderr and "Exception ignored" not in result.stderr


@pytest.mark.parametrize("number", [errno.EPIPE, errno.EINVAL])
def test_stdout_oserror_survives_unavailable_descriptor(monkeypatch, number):
    class FailedOutput:
        def write(self, text):
            raise OSError(number, "closed output")

        def fileno(self):
            raise ValueError("no descriptor")

    monkeypatch.setattr(sys, "stdout", FailedOutput())
    with pytest.raises(OSError):
        write_stdout("report")


def test_literal_markdown_fence():
    rendered = render_markdown({"project": "ignored", "explanation": "literal ```` <b>text</b>"})
    assert "\n```json\n" in rendered and "literal ```` <b>text</b>" in rendered
