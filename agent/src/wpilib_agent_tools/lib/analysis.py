"""Shared analysis helpers for log data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

Numeric = int | float
Point = tuple[float, Any]


@dataclass(frozen=True)
class MinMaxResult:
    """Min/Max values and their timestamps."""

    min_time: float
    min_value: float
    max_time: float
    max_value: float


def _as_numeric(value: Any) -> float | None:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return None


def calculate_derivative(points: Iterable[Point]) -> list[tuple[float, float]]:
    """Compute derivative using finite differences."""
    point_list = list(points)
    if len(point_list) < 2:
        return []
    output: list[tuple[float, float]] = []
    for index in range(1, len(point_list)):
        prev_time, prev_value = point_list[index - 1]
        cur_time, cur_value = point_list[index]
        prev_num = _as_numeric(prev_value)
        cur_num = _as_numeric(cur_value)
        if prev_num is None or cur_num is None:
            continue
        dt = cur_time - prev_time
        if dt == 0:
            continue
        output.append((cur_time, (cur_num - prev_num) / dt))
    return output


def calculate_integral(points: Iterable[Point]) -> list[tuple[float, float]]:
    """Compute cumulative trapezoidal integral."""
    point_list = list(points)
    if len(point_list) < 2:
        return []
    output: list[tuple[float, float]] = []
    running = 0.0
    for index in range(1, len(point_list)):
        prev_time, prev_value = point_list[index - 1]
        cur_time, cur_value = point_list[index]
        prev_num = _as_numeric(prev_value)
        cur_num = _as_numeric(cur_value)
        if prev_num is None or cur_num is None:
            continue
        dt = cur_time - prev_time
        if dt == 0:
            continue
        running += ((prev_num + cur_num) / 2.0) * dt
        output.append((cur_time, running))
    return output


def calculate_average(points: Iterable[Point]) -> float | list[float] | None:
    """Compute scalar average or element-wise vector average."""
    values = [value for _, value in points]
    if not values:
        return None

    numeric_values = [_as_numeric(value) for value in values]
    if all(value is not None for value in numeric_values):
        numeric_list = [value for value in numeric_values if value is not None]
        if not numeric_list:
            return None
        return sum(numeric_list) / len(numeric_list)

    first = values[0]
    if isinstance(first, list):
        width = len(first)
        if width == 0:
            return None
        total = [0.0] * width
        count = 0
        for value in values:
            if not isinstance(value, list) or len(value) != width:
                continue
            row = [_as_numeric(item) for item in value]
            if any(item is None for item in row):
                continue
            for idx, item in enumerate(row):
                total[idx] += float(item)
            count += 1
        if count == 0:
            return None
        return [element / count for element in total]
    return None


def calculate_minmax(points: Iterable[Point]) -> MinMaxResult | None:
    """Compute min and max for scalar values."""
    numeric_points: list[tuple[float, float]] = []
    for timestamp, value in points:
        numeric = _as_numeric(value)
        if numeric is None:
            continue
        numeric_points.append((timestamp, numeric))
    if not numeric_points:
        return None
    min_time, min_value = min(numeric_points, key=lambda pair: pair[1])
    max_time, max_value = max(numeric_points, key=lambda pair: pair[1])
    return MinMaxResult(
        min_time=min_time,
        min_value=min_value,
        max_time=max_time,
        max_value=max_value,
    )


def reconstruct_driver_station_state(
    ds_series: dict[str, list[Point]],
    target_time: float | None = None,
) -> dict[str, Any]:
    """Reconstruct latest known DS state up to target time (or end)."""
    state: dict[str, Any] = {
        "DriverStation/Enabled": None,
        "DriverStation/Autonomous": None,
        "DriverStation/Test": None,
        "DriverStation/AllianceStation": None,
        "DriverStation/MatchTime": None,
    }
    for key in state:
        points = ds_series.get(key, [])
        for timestamp, value in points:
            if target_time is not None and timestamp > target_time:
                break
            state[key] = value
    return state
