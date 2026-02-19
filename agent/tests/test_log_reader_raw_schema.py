from __future__ import annotations

import struct
from pathlib import Path

import pytest

from wpilib_agent_tools.lib.log_reader import LogReader

DataLogWriter = pytest.importorskip("wpiutil").DataLogWriter


def _write_raw_struct_log(path: Path) -> None:
    log = DataLogWriter(str(path))
    schema_entry = int(log.start("/AdvantageKit/.schema/struct:ChassisSpeeds", "raw"))
    value_entry = int(log.start("/AdvantageKit/RealOutputs/RobotState/fieldRelativeSpeeds", "raw"))
    log.appendRaw(schema_entry, b"schema", 10)
    log.appendRaw(value_entry, struct.pack("<ddd", 0.1, -0.2, 0.3), 1_000_000)
    log.appendRaw(value_entry, struct.pack("<ddd", 0.5, 1.0, -0.4), 3_000_000)
    log.flush()
    log.stop()


def test_log_reader_decodes_raw_chassis_speed_using_schema_hint(tmp_path: Path) -> None:
    log_path = tmp_path / "raw_struct.wpilog"
    _write_raw_struct_log(log_path)

    points = LogReader(log_path).read_key_points("/AdvantageKit/RealOutputs/RobotState/fieldRelativeSpeeds")
    assert len(points) == 2
    assert points[0][1]["type"] == "ChassisSpeeds"
    assert points[0][1]["vx_mps"] == pytest.approx(0.1)
    assert points[0][1]["vy_mps"] == pytest.approx(-0.2)
    assert points[0][1]["omega_radps"] == pytest.approx(0.3)


def test_log_summary_uses_data_sample_window(tmp_path: Path) -> None:
    log_path = tmp_path / "summary_window.wpilog"
    _write_raw_struct_log(log_path)

    summary = LogReader(log_path).get_summary()
    assert summary.sample_count == 3
    assert summary.duration_sec == pytest.approx(2.99999, abs=0.01)
