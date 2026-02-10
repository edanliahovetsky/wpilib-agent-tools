"""Query/analyze log values."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from typing import Any

from wpilib_agent_tools.lib.analysis import (
    calculate_average,
    calculate_derivative,
    calculate_fft,
    calculate_integral,
    calculate_minmax,
    calculate_rms,
    calculate_settle_metrics,
    calculate_stats,
    detect_threshold_events,
    evaluate_expression_series,
    extract_expression_keys,
    reconstruct_driver_station_state,
    smooth_points,
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
        choices=[
            "timestamps",
            "values",
            "avg",
            "ds",
            "minmax",
            "deriv",
            "integral",
            "stats",
            "smooth",
            "threshold",
            "rms",
            "expr",
            "fft",
            "settle",
        ],
        help="Query mode.",
    )
    parser.add_argument("--start", type=float, help="Start timestamp seconds.")
    parser.add_argument("--end", type=float, help="End timestamp seconds.")
    parser.add_argument("--limit", type=int, help="Limit sample output for series-returning modes.")
    parser.add_argument("--window", type=int, default=5, help="Window size for smooth mode.")
    parser.add_argument("--expr", help="Expression with {Log/Key} placeholders for expr mode.")
    parser.add_argument("--above", type=float, help="Threshold for event detection above this value.")
    parser.add_argument("--below", type=float, help="Threshold for event detection below this value.")
    parser.add_argument(
        "--min-duration",
        type=float,
        default=0.0,
        help="Minimum threshold event duration in seconds.",
    )
    parser.add_argument("--top", type=int, default=5, help="Number of dominant FFT components.")
    parser.add_argument("--setpoint", type=float, help="Constant target setpoint for settle mode.")
    parser.add_argument("--setpoint-key", help="Setpoint log key for settle mode.")
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.02,
        help="Settling band as fraction (e.g. 0.02 for +/-2%%).",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.set_defaults(handler=handle_query)


def _limit_points(points: list[tuple[float, Any]], limit: int | None) -> list[tuple[float, Any]]:
    if limit is None or limit <= 0:
        return points
    return points[:limit]


def _json_safe(value: Any) -> Any:
    """Convert nested payload values into JSON-serializable forms."""
    if isinstance(value, bytes):
        return f"0x{value.hex()}"
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    return value


def _format_value_for_text(value: Any) -> str:
    """Render nested values in stable, human-readable text form."""
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(_json_safe(value), sort_keys=True)
    return str(value)


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

    if args.mode == "expr":
        if not args.expr:
            raise ValueError("--expr is required for mode 'expr'")
        keys = extract_expression_keys(args.expr)
        if not keys:
            raise ValueError("--expr must include at least one {Log/Key} placeholder")
        series = {
            key: reader.read_key_points(key, start=args.start, end=args.end)
            for key in keys
        }
        values = evaluate_expression_series(args.expr, series)
        payload["expr"] = args.expr
        payload["keys"] = keys
        payload["count"] = len(values)
        payload["values"] = _limit_points(values, args.limit)
        return payload

    requires_key_modes = {
        "timestamps",
        "values",
        "avg",
        "minmax",
        "deriv",
        "integral",
        "stats",
        "smooth",
        "threshold",
        "rms",
        "fft",
        "settle",
    }
    if args.mode in requires_key_modes and not args.key:
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

    if args.mode == "stats":
        stats = calculate_stats(points)
        payload["stats"] = asdict(stats) if stats is not None else None
        return payload

    if args.mode == "smooth":
        values = smooth_points(points, args.window)
        payload["window"] = args.window
        payload["values"] = _limit_points(values, args.limit)
        return payload

    if args.mode == "threshold":
        events = detect_threshold_events(
            points,
            above=args.above,
            below=args.below,
            min_duration=args.min_duration,
        )
        payload["above"] = args.above
        payload["below"] = args.below
        payload["min_duration"] = args.min_duration
        payload["events"] = [asdict(event) for event in events]
        return payload

    if args.mode == "rms":
        payload["rms"] = calculate_rms(points)
        return payload

    if args.mode == "fft":
        components = calculate_fft(points, top_n=args.top)
        payload["top"] = args.top
        payload["components"] = [asdict(component) for component in components]
        return payload

    if args.mode == "settle":
        setpoint_points = None
        if args.setpoint_key:
            setpoint_points = reader.read_key_points(args.setpoint_key, start=args.start, end=args.end)
        metrics = calculate_settle_metrics(
            points,
            tolerance=args.tolerance,
            setpoint=args.setpoint,
            setpoint_points=setpoint_points,
        )
        payload["tolerance"] = args.tolerance
        payload["setpoint"] = args.setpoint
        payload["setpoint_key"] = args.setpoint_key
        payload["settle"] = asdict(metrics) if metrics is not None else None
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
        payload = {"results": _json_safe(results)}
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
                print(f"  {timestamp:.6f}: {_format_value_for_text(value)}")
        elif item["mode"] == "avg":
            print(f"  Average: {item.get('average')}")
        elif item["mode"] == "minmax":
            print(f"  Min/Max: {item.get('minmax')}")
        elif item["mode"] in {"deriv", "integral"}:
            for timestamp, value in item.get("values", []):
                print(f"  {timestamp:.6f}: {_format_value_for_text(value)}")
        elif item["mode"] == "stats":
            print(f"  Stats: {item.get('stats')}")
        elif item["mode"] == "smooth":
            for timestamp, value in item.get("values", []):
                print(f"  {timestamp:.6f}: {_format_value_for_text(value)}")
        elif item["mode"] == "threshold":
            events = item.get("events", [])
            print(f"  Events: {len(events)}")
            for event in events:
                print(
                    "    "
                    f"start={event['start_time']:.6f} "
                    f"end={event['end_time']:.6f} "
                    f"duration={event['duration']:.6f} "
                    f"peak={event['peak_value']}"
                )
        elif item["mode"] == "rms":
            print(f"  RMS: {item.get('rms')}")
        elif item["mode"] == "expr":
            print(f"  Expression: {item.get('expr')}")
            for timestamp, value in item.get("values", []):
                print(f"  {timestamp:.6f}: {_format_value_for_text(value)}")
        elif item["mode"] == "fft":
            for component in item.get("components", []):
                print(
                    f"  {component['frequency_hz']:.6f} Hz: "
                    f"{component['magnitude']}"
                )
        elif item["mode"] == "settle":
            print(f"  Settle: {item.get('settle')}")
        elif item["mode"] == "ds":
            print("  State:")
            for key, value in item.get("state", {}).items():
                print(f"    {key}: {_format_value_for_text(value)}")
        print("")
    return 0
