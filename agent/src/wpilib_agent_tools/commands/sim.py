"""Simulation command."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

from wpilib_agent_tools.lib.log_reader import LogReader


def _runtime_dir() -> Path:
    path = Path.home() / ".wpilib-agent-tools" / "runtime"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _sim_pid_file() -> Path:
    return _runtime_dir() / "sim.pid"


def _is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _kill_prior_instance() -> dict[str, Any]:
    """Kill previous sim instance to enforce single active run."""
    pid_file = _sim_pid_file()
    if not pid_file.exists():
        return {"killed": False}
    try:
        pid = int(pid_file.read_text(encoding="utf-8").strip())
    except Exception:
        pid_file.unlink(missing_ok=True)
        return {"killed": False}

    if not _is_running(pid):
        pid_file.unlink(missing_ok=True)
        return {"killed": False}

    try:
        pgid = os.getpgid(pid)
        os.killpg(pgid, signal.SIGTERM)
        deadline = time.time() + 5.0
        while time.time() < deadline and _is_running(pid):
            time.sleep(0.1)
        if _is_running(pid):
            os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    pid_file.unlink(missing_ok=True)
    return {"killed": True, "pid": pid}


def register_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "sim",
        help="Run headless simulation for a fixed duration.",
    )
    parser.add_argument("--duration", type=float, default=15.0, help="Simulation duration in seconds.")
    parser.add_argument("--gradle-task", default="simulateJava", help="Gradle task to invoke.")
    parser.add_argument("--no-analyze", action="store_true", help="Skip log summary after simulation.")
    parser.add_argument(
        "--direct-workspace",
        action="store_true",
        help="Allow running outside sandbox (disabled by default).",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.set_defaults(handler=handle_sim)


def _emit(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        import json

        print(json.dumps(payload, indent=2))
        return
    if payload.get("killed_previous"):
        print(f"Stopped previous sim instance (pid={payload.get('previous_pid')}).")
    print(f"Started sim pid={payload['pid']} for {payload['duration_sec']}s")
    print(f"Exit code: {payload['exit_code']}")
    summary = payload.get("log_summary")
    if summary:
        print(
            "Latest log: "
            f"{summary['path']} (keys={summary['key_count']}, duration={summary['duration_sec']})"
        )


def handle_sim(args: argparse.Namespace) -> int:
    inside_sandbox = os.environ.get("WPILIB_AGENT_TOOLS_SANDBOX") == "1"
    if not inside_sandbox and not args.direct_workspace:
        print(
            "Refusing to run sim directly in workspace. "
            "Use `wpilib-agent-tools sandbox run --name <sandbox> -- sim ...` "
            "or pass --direct-workspace."
        )
        return 2

    kill_result = _kill_prior_instance()
    command = ["./gradlew", args.gradle_task]
    process = subprocess.Popen(command, preexec_fn=os.setsid)
    _sim_pid_file().write_text(str(process.pid), encoding="utf-8")

    start = time.monotonic()
    interrupted = False
    try:
        while True:
            elapsed = time.monotonic() - start
            if process.poll() is not None:
                break
            if elapsed >= args.duration:
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        interrupted = True
    finally:
        if process.poll() is None:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait(timeout=5.0)
        _sim_pid_file().unlink(missing_ok=True)

    exit_code = process.returncode if process.returncode is not None else 0
    payload: dict[str, Any] = {
        "pid": process.pid,
        "duration_sec": args.duration,
        "interrupted": interrupted,
        "exit_code": exit_code,
        "killed_previous": bool(kill_result.get("killed")),
        "previous_pid": kill_result.get("pid"),
    }

    if not args.no_analyze:
        latest = LogReader.get_latest_log("agent/logs")
        if latest is not None:
            summary = LogReader(latest).get_summary()
            payload["log_summary"] = {
                "path": summary.path,
                "format": summary.format,
                "duration_sec": summary.duration_sec,
                "key_count": summary.key_count,
                "sample_count": summary.sample_count,
            }

    _emit(payload, args.json)
    return 0 if exit_code == 0 else exit_code
