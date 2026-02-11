from __future__ import annotations

import json
from pathlib import Path

from wpilib_agent_tools.commands.sim import _parse_assert_ranges
from wpilib_agent_tools.lib.assertions import evaluate_assertions


def _write_log(path: Path, entries: dict[str, dict[str, object]]) -> Path:
    payload = {
        "source": "fixture",
        "address": "localhost",
        "start_time": "2026-02-10T00:00:00Z",
        "duration_sec": 2.0,
        "entries": entries,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_parse_assert_ranges_validates_input() -> None:
    parsed = _parse_assert_ranges([["Shooter/Angle", "-450", "630"]])
    assert parsed == [("Shooter/Angle", -450.0, 630.0)]

    try:
        _parse_assert_ranges([["Shooter/Angle", "abc", "630"]])
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Invalid --assert-range bounds" in str(exc)

    try:
        _parse_assert_ranges([["Shooter/Angle", "20", "10"]])
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "min must be <= max" in str(exc)


def test_evaluate_assertions_reports_pass_and_failure(tmp_path: Path) -> None:
    log_path = _write_log(
        tmp_path / "assertions.json",
        {
            "Shooter/turretResolvedSetpointDeg": {
                "type": "double",
                "data": [[0.0, -180.0], [1.0, 200.0], [2.0, 700.0]],
            },
            "Shooter/turretUsedUnwindFallback": {
                "type": "boolean",
                "data": [[0.0, False], [1.0, True]],
            },
        },
    )
    result = evaluate_assertions(
        log_path,
        assert_keys=["Shooter/turretUsedUnwindFallback"],
        assert_ranges=[("Shooter/turretResolvedSetpointDeg", -450.0, 630.0)],
    )
    assert result["passed"] is False
    assert result["summary"]["total"] == 2
    assert result["summary"]["failed"] == 1
    range_check = next(check for check in result["checks"] if check["type"] == "assert_range")
    assert range_check["passed"] is False
    assert range_check["reason"] == "range_violation"
    assert range_check["first_violation"]["value"] == 700.0


def test_evaluate_assertions_missing_key_fails(tmp_path: Path) -> None:
    log_path = _write_log(
        tmp_path / "missing.json",
        {
            "Shooter/Velocity": {
                "type": "double",
                "data": [[0.0, 1000.0], [1.0, 1200.0]],
            }
        },
    )
    result = evaluate_assertions(
        log_path,
        assert_keys=["Shooter/NotPresent"],
        assert_ranges=[("Shooter/NotPresent", 0.0, 1.0)],
    )
    assert result["passed"] is False
    assert result["summary"]["failed"] == 2
