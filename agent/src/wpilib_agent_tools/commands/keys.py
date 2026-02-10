"""List keys in a log file."""

from __future__ import annotations

import argparse
import json

from wpilib_agent_tools.lib.log_reader import LogReader, ensure_log_file


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("keys", help="List keys in a WPILOG or recorder JSON file.")
    parser.add_argument("--file", help="Path to log file (defaults to latest).")
    parser.add_argument("--filter", help="Case-insensitive substring filter.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.set_defaults(handler=handle_keys)


def handle_keys(args: argparse.Namespace) -> int:
    try:
        path = ensure_log_file(args.file)
    except FileNotFoundError as exc:
        print(str(exc))
        return 1

    reader = LogReader(path)
    keys = reader.list_keys(args.filter)
    if args.json:
        print(json.dumps({"file": path, "count": len(keys), "keys": keys}, indent=2))
        return 0

    print(f"Reading keys from: {path}")
    print("-" * 40)
    for key in keys:
        print(key)
    return 0
