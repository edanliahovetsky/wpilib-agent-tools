"""Graph log values."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from wpilib_agent_tools.lib.analysis import calculate_derivative, calculate_integral
from wpilib_agent_tools.lib.log_reader import LogReader, ensure_log_file


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("graph", help="Generate graphs from log data.")
    parser.add_argument("--file", help="Path to log file (defaults to latest).")
    parser.add_argument(
        "--key",
        action="append",
        required=True,
        help="Key to graph. Repeat for multiple series.",
    )
    parser.add_argument(
        "--mode",
        choices=["values", "deriv", "integral"],
        default="values",
        help="Graph transformation mode.",
    )
    parser.add_argument("--output", default="graph.png", help="Output PNG filename.")
    parser.add_argument("--start", type=float, help="Start timestamp seconds.")
    parser.add_argument("--end", type=float, help="End timestamp seconds.")
    parser.add_argument("--title", help="Custom graph title.")
    parser.add_argument("--scatter", action="store_true", help="Use scatter plot.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.set_defaults(handler=handle_graph)


def _numeric_points(points: list[tuple[float, Any]]) -> list[tuple[float, float]]:
    output: list[tuple[float, float]] = []
    for timestamp, value in points:
        if isinstance(value, bool):
            output.append((timestamp, 1.0 if value else 0.0))
        elif isinstance(value, (int, float)):
            output.append((timestamp, float(value)))
        elif isinstance(value, list) and value and isinstance(value[0], (int, float)):
            output.append((timestamp, float(value[0])))
    return output


def handle_graph(args: argparse.Namespace) -> int:
    try:
        file_path = ensure_log_file(args.file)
    except FileNotFoundError as exc:
        print(str(exc))
        return 1

    reader = LogReader(file_path)
    plot_rows: list[dict[str, Any]] = []

    for key in args.key:
        points = _numeric_points(reader.read_key_points(key, start=args.start, end=args.end))
        if args.mode == "deriv":
            points = calculate_derivative(points)
        elif args.mode == "integral":
            points = calculate_integral(points)
        if not points:
            continue
        plot_rows.append({"key": key, "points": points})

    if not plot_rows:
        print("No graphable data found for requested keys.")
        return 1

    plt.figure(figsize=(12, 6))
    for row in plot_rows:
        xs = [point[0] for point in row["points"]]
        ys = [point[1] for point in row["points"]]
        label = row["key"] if args.mode == "values" else f"{args.mode}({row['key']})"
        if args.scatter:
            plt.scatter(xs, ys, s=8, label=label)
        else:
            plt.plot(xs, ys, label=label)

    title = args.title or f"WPILib Agent Tools Graph ({args.mode})"
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)

    output_dir = Path("agent/visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / Path(args.output).name
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    payload = {
        "file": file_path,
        "mode": args.mode,
        "output": str(output_path),
        "series_count": len(plot_rows),
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Graph saved to: {output_path}")
    return 0
