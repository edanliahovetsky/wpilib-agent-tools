"""Query/analyze log values."""

from __future__ import annotations

import argparse
import json
from typing import Any

from wpilib_agent_tools.lib.analysis import (
    calculate_average,
    calculate_derivative,
    calculate_integral,
    calculate_minmax,
    reconstruct_driver_station_state,
)
from wpilib_agent_tools.lib.log_reader import LogReader, ensure_log_file, expand_log_glob


DS_KEYS = [
    "DriverStation/Enabled",
    "DriverStation/Autonomous",
    "DriverStation/Test",
    "DriverStation/AllianceStation",
    "DriverStation/MatchTime",
]


def _resolve_ds_keys(reader: LogReader) -> dict[str, str | None]:
    """Resolve canonical DriverStation keys to available log key names."""
    available_keys = reader.list_keys()
    resolved: dict[str, str | None] = {}

    for canonical in DS_KEYS:
        selected: str | None = None
        for candidate in (canonical, f"/{canonical}"):
            if candidate in available_keys:
                selected = candidate
                break

        if selected is None:
            suffix = f"/{canonical}"
            suffix_matches = [key for key in available_keys if key.endswith(suffix)]
            if suffix_matches:
                # Prefer shorter keys like '/DriverStation/Enabled' over deeply prefixed variants.
                selected = min(suffix_matches, key=len)

        resolved[canonical] = selected

    return resolved


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("query", help="Analyze key data in logs.")
    parser.add_argument("--file", help="Path or glob to log file (defaults to latest).")
    parser.add_argument("--key", help="Key to analyze.")
    parser.add_argument(
        "--mode",
        required=True,
        choices=["timestamps", "values", "avg", "ds", "minmax", "deriv", "integral"],
        help="Query mode.",
    )
    parser.add_argument("--start", type=float, help="Start timestamp seconds.")
    parser.add_argument("--end", type=float, help="End timestamp seconds.")
    parser.add_argument("--limit", type=int, help="Limit sample output (values/deriv/integral).")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.set_defaults(handler=handle_query)


def _limit_points(points: list[tuple[float, Any]], limit: int | None) -> list[tuple[float, Any]]:
    if limit is None or limit <= 0:
        return points
    return points[:limit]


def _run_single_query(reader: LogReader, args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {"file": str(reader.path), "mode": args.mode}

    if args.mode == "ds":
        key_mapping = _resolve_ds_keys(reader)
        actual_keys = [key for key in key_mapping.values() if key]
        # For DS reconstruction, we need the latest values up to target_time (start).
        # Do not trim by start here or we'd lose prior state transitions.
        raw_series = reader.read_multiple_keys(actual_keys, start=None, end=args.end)
        series = {
            canonical: raw_series.get(actual, []) if actual else []
            for canonical, actual in key_mapping.items()
        }
        state = reconstruct_driver_station_state(series, target_time=args.start)
        payload["state"] = state
        payload["series"] = series
        payload["resolved_keys"] = key_mapping
        return payload

    if not args.key:
        raise ValueError(f"--key is required for mode '{args.mode}'")

    points = reader.read_key_points(args.key, start=args.start, end=args.end)
    payload["key"] = args.key
    payload["count"] = len(points)

    if args.mode == "timestamps":
        if points:
            payload["start_time"] = points[0][0]
            payload["end_time"] = points[-1][0]
        else:
            payload["start_time"] = None
            payload["end_time"] = None
        return payload

    if args.mode == "values":
        payload["values"] = _limit_points(points, args.limit)
        return payload

    if args.mode == "avg":
        payload["average"] = calculate_average(points)
        return payload

    if args.mode == "minmax":
        minmax = calculate_minmax(points)
        payload["minmax"] = None
        if minmax is not None:
            payload["minmax"] = {
                "min_time": minmax.min_time,
                "min_value": minmax.min_value,
                "max_time": minmax.max_time,
                "max_value": minmax.max_value,
            }
        return payload

    if args.mode == "deriv":
        deriv = calculate_derivative(points)
        payload["values"] = _limit_points(deriv, args.limit)
        return payload

    if args.mode == "integral":
        integral = calculate_integral(points)
        payload["values"] = _limit_points(integral, args.limit)
        return payload

    raise ValueError(f"Unhandled query mode: {args.mode}")


def handle_query(args: argparse.Namespace) -> int:
    try:
        source = ensure_log_file(args.file)
    except FileNotFoundError as exc:
        print(str(exc))
        return 1

    files = [path for path in expand_log_glob(source) if path]
    if not files:
        print(f"No files matched: {source}")
        return 1

    try:
        results = [_run_single_query(LogReader(path), args) for path in files]
    except ValueError as exc:
        print(str(exc))
        return 2
    except RuntimeError as exc:
        print(str(exc))
        return 1

    if args.json:
        payload = {"results": results}
        print(json.dumps(payload, indent=2))
        return 0

    for item in results:
        print(f"File: {item['file']}")
        print(f"Mode: {item['mode']}")
        if item["mode"] == "timestamps":
            print(f"  Start: {item.get('start_time')}")
            print(f"  End:   {item.get('end_time')}")
            print(f"  Count: {item.get('count')}")
        elif item["mode"] == "values":
            for timestamp, value in item.get("values", []):
                print(f"  {timestamp:.6f}: {value}")
        elif item["mode"] == "avg":
            print(f"  Average: {item.get('average')}")
        elif item["mode"] == "minmax":
            print(f"  Min/Max: {item.get('minmax')}")
        elif item["mode"] in {"deriv", "integral"}:
            for timestamp, value in item.get("values", []):
                print(f"  {timestamp:.6f}: {value}")
        elif item["mode"] == "ds":
            print("  State:")
            for key, value in item.get("state", {}).items():
                print(f"    {key}: {value}")
        print("")
    return 0
