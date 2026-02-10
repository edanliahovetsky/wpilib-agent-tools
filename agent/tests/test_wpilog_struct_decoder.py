from __future__ import annotations

import struct

from wpilib_agent_tools.lib.wpilog_struct_decoder import decode_struct_value


def test_decode_chassis_speeds_and_pose2d() -> None:
    chassis_raw = struct.pack("<ddd", 1.5, -2.0, 3.25)
    chassis = decode_struct_value(chassis_raw, "struct:ChassisSpeeds")
    assert chassis is not None
    assert chassis["type"] == "ChassisSpeeds"
    assert chassis["vx_mps"] == 1.5
    assert chassis["vy_mps"] == -2.0
    assert chassis["omega_radps"] == 3.25

    pose_raw = struct.pack("<ddd", 2.2, -0.7, 1.0)
    pose = decode_struct_value(pose_raw, "struct:Pose2d")
    assert pose is not None
    assert pose["type"] == "Pose2d"
    assert pose["translation"]["x_meters"] == 2.2
    assert pose["translation"]["y_meters"] == -0.7
    assert pose["rotation"]["radians"] == 1.0


def test_decode_swerve_module_state_array() -> None:
    raw = struct.pack("<dddd", 4.1, 0.2, -1.0, -0.3)
    decoded = decode_struct_value(raw, "struct:SwerveModuleState[]")
    assert decoded is not None
    assert decoded["type"] == "SwerveModuleState[]"
    assert len(decoded["values"]) == 2
    assert decoded["values"][0]["speed_mps"] == 4.1
    assert decoded["values"][1]["angle"]["radians"] == -0.3


def test_decode_unknown_struct_returns_none() -> None:
    assert decode_struct_value(b"\x01\x02", "struct:UnknownType") is None
