from __future__ import annotations

from wpilib_agent_tools.commands.graph import _expand_keys, _numeric_points


def test_numeric_points_reports_non_numeric_samples() -> None:
    points = [
        (0.0, 1.0),
        (1.0, {"type": "ChassisSpeeds", "vx_mps": 2.0}),
        (2.0, [3.0, 4.0]),
        (3.0, "not-graphable"),
        (4.0, True),
    ]
    numeric, skipped_non_numeric = _numeric_points(points)
    assert numeric == [(0.0, 1.0), (2.0, 3.0), (4.0, 1.0)]
    assert skipped_non_numeric == 2


def test_expand_keys_accepts_repeated_and_comma_separated_values() -> None:
    keys = _expand_keys(["Drive/Vx, Drive/Vy", "Shooter/RPM", "Arm/Pos,"])
    assert keys == ["Drive/Vx", "Drive/Vy", "Shooter/RPM", "Arm/Pos"]
