"""Decoders for common WPILib struct payloads in WPILOG entries."""

from __future__ import annotations

import struct
from typing import Any


def _decode_rotation2d(raw: bytes) -> dict[str, Any] | None:
    if len(raw) != 8:
        return None
    (radians,) = struct.unpack("<d", raw)
    return {
        "type": "Rotation2d",
        "radians": radians,
    }


def _decode_translation2d(raw: bytes) -> dict[str, Any] | None:
    if len(raw) != 16:
        return None
    x, y = struct.unpack("<dd", raw)
    return {
        "type": "Translation2d",
        "x_meters": x,
        "y_meters": y,
    }


def _decode_pose2d(raw: bytes) -> dict[str, Any] | None:
    if len(raw) != 24:
        return None
    x, y, radians = struct.unpack("<ddd", raw)
    return {
        "type": "Pose2d",
        "translation": {
            "type": "Translation2d",
            "x_meters": x,
            "y_meters": y,
        },
        "rotation": {
            "type": "Rotation2d",
            "radians": radians,
        },
    }


def _decode_chassis_speeds(raw: bytes) -> dict[str, Any] | None:
    if len(raw) != 24:
        return None
    vx, vy, omega = struct.unpack("<ddd", raw)
    return {
        "type": "ChassisSpeeds",
        "vx_mps": vx,
        "vy_mps": vy,
        "omega_radps": omega,
    }


def _decode_swerve_module_state(raw: bytes) -> dict[str, Any] | None:
    if len(raw) != 16:
        return None
    speed, angle_radians = struct.unpack("<dd", raw)
    return {
        "type": "SwerveModuleState",
        "speed_mps": speed,
        "angle": {
            "type": "Rotation2d",
            "radians": angle_radians,
        },
    }


def _decode_swerve_module_state_array(raw: bytes) -> dict[str, Any] | None:
    if not raw:
        return {
            "type": "SwerveModuleState[]",
            "values": [],
        }
    if len(raw) % 16 != 0:
        return None

    values: list[dict[str, Any]] = []
    for index in range(0, len(raw), 16):
        decoded = _decode_swerve_module_state(raw[index : index + 16])
        if decoded is None:
            return None
        values.append(decoded)

    return {
        "type": "SwerveModuleState[]",
        "values": values,
    }


DECODERS = {
    "struct:Rotation2d": _decode_rotation2d,
    "struct:Translation2d": _decode_translation2d,
    "struct:Pose2d": _decode_pose2d,
    "struct:ChassisSpeeds": _decode_chassis_speeds,
    "struct:SwerveModuleState": _decode_swerve_module_state,
    "struct:SwerveModuleState[]": _decode_swerve_module_state_array,
}


def decode_struct_value(raw: bytes, type_str: str) -> dict[str, Any] | None:
    """Decode known `struct:*` WPILOG payloads into readable dicts."""
    decoder = DECODERS.get(type_str)
    if decoder is None:
        return None
    return decoder(raw)
