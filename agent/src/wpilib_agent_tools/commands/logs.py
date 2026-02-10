"""List available log files."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from wpilib_agent_tools.lib.log_reader import LogReader
from wpilib_agent_tools.lib.output import format_size_bytes


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("logs", help="List log files with metadata.")
    parser.add_argument("--dir", default="agent/logs", help="Directory containing logs.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.set_defaults(handler=handle_logs)


def handle_logs(args: argparse.Namespace) -> int:
    log_dir = Path(args.dir)
    files = LogReader.list_log_files(log_dir)
    rows = []
    for path in files:
        summary = LogReader(path).get_summary()
        rows.append(
            {
                "path": summary.path,
                "name": Path(summary.path).name,
                "format": summary.format,
                "size_bytes": summary.size_bytes,
                "size_human": format_size_bytes(summary.size_bytes),
                "modified_epoch": summary.modified_epoch,
                "modified_iso": datetime.fromtimestamp(summary.modified_epoch).isoformat(),
                "duration_sec": summary.duration_sec,
                "key_count": summary.key_count,
                "sample_count": summary.sample_count,
            }
        )

    if args.json:
        print(json.dumps({"directory": str(log_dir), "logs": rows}, indent=2))
        return 0

    if not rows:
        print(f"No logs found in {log_dir.resolve()}")
        return 0

    print(f"{'Modified':<22} {'Size':<10} {'Keys':<6} {'Duration':<10} {'File'}")
    print("-" * 96)
    for row in rows:
        duration = "-" if row["duration_sec"] is None else f"{row['duration_sec']:.3f}s"
        print(
            f"{row['modified_iso']:<22} {row['size_human']:<10} "
            f"{row['key_count']:<6} {duration:<10} {row['name']}"
        )
    return 0
