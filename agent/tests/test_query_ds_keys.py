from __future__ import annotations

import argparse
import json
from pathlib import Path

from wpilib_agent_tools.commands.query import _run_single_query
from wpilib_agent_tools.lib.log_reader import LogReader


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


def _ds_args(start: float | None = None) -> argparse.Namespace:
    return argparse.Namespace(
        file=None,
        key=None,
        mode="ds",
        start=start,
        end=None,
        limit=None,
        json=True,
    )


def test_ds_mode_resolves_prefixed_and_slash_keys(tmp_path: Path) -> None:
    log_path = _write_log(
        tmp_path / "prefixed.json",
        {
            "/DriverStation/Enabled": {"type": "boolean", "data": [[0.0, False], [1.0, True]]},
            "/AdvantageKit/DriverStation/Autonomous": {"type": "boolean", "data": [[0.0, True]]},
            "/AdvantageKit/DriverStation/Test": {"type": "boolean", "data": [[0.0, False]]},
            "/DriverStation/AllianceStation": {"type": "string", "data": [[0.0, "Blue1"]]},
            "/AdvantageKit/DriverStation/MatchTime": {"type": "double", "data": [[0.0, 15.0], [1.0, 14.0]]},
        },
    )

    result = _run_single_query(LogReader(log_path), _ds_args(start=1.0))

    assert result["state"]["DriverStation/Enabled"] is True
    assert result["state"]["DriverStation/Autonomous"] is True
    assert result["state"]["DriverStation/Test"] is False
    assert result["state"]["DriverStation/AllianceStation"] == "Blue1"
    assert result["state"]["DriverStation/MatchTime"] == 14.0
    assert result["resolved_keys"]["DriverStation/Autonomous"] == "/AdvantageKit/DriverStation/Autonomous"


def test_ds_mode_keeps_bare_driverstation_keys(tmp_path: Path) -> None:
    log_path = _write_log(
        tmp_path / "bare.json",
        {
            "DriverStation/Enabled": {"type": "boolean", "data": [[0.0, True]]},
            "DriverStation/Autonomous": {"type": "boolean", "data": [[0.0, False]]},
            "DriverStation/Test": {"type": "boolean", "data": [[0.0, False]]},
            "DriverStation/AllianceStation": {"type": "string", "data": [[0.0, "Red2"]]},
            "DriverStation/MatchTime": {"type": "double", "data": [[0.0, 12.5]]},
        },
    )

    result = _run_single_query(LogReader(log_path), _ds_args())

    assert result["state"]["DriverStation/Enabled"] is True
    assert result["state"]["DriverStation/Autonomous"] is False
    assert result["state"]["DriverStation/Test"] is False
    assert result["state"]["DriverStation/AllianceStation"] == "Red2"
    assert result["state"]["DriverStation/MatchTime"] == 12.5
    assert result["resolved_keys"]["DriverStation/Enabled"] == "DriverStation/Enabled"
