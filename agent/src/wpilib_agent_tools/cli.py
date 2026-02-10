"""Command-line entry point for WPILib Agent Tools."""

from __future__ import annotations

import argparse
from typing import Any, Callable

from wpilib_agent_tools import __version__
from wpilib_agent_tools.commands import graph, keys, logs, query, record, sandbox, sim, view


CommandRegistrar = Callable[[Any], None]


def build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level CLI parser."""
    parser = argparse.ArgumentParser(
        prog="wpilib-agent-tools",
        description="Sandbox-first tooling for WPILib robot iteration and analysis.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    registrars: list[CommandRegistrar] = [
        sim.register_subparser,
        logs.register_subparser,
        keys.register_subparser,
        query.register_subparser,
        graph.register_subparser,
        record.register_subparser,
        view.register_subparser,
        sandbox.register_subparser,
    ]
    for registrar in registrars:
        registrar(subparsers)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Program entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 2
    return int(handler(args) or 0)
