from __future__ import annotations

from wpilib_agent_tools.cli import build_parser


def test_sim_parser_defaults_to_concise_mode() -> None:
    parser = build_parser()
    args = parser.parse_args(["sim", "--direct-workspace"])
    assert args.command == "sim"
    assert args.verbose is False
    assert args.max_lines == 120
    assert args.tail is True


def test_sim_parser_accepts_assertions() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "sim",
            "--direct-workspace",
            "--assert-key",
            "Shooter/turretUsedUnwindFallback",
            "--assert-range",
            "Shooter/turretResolvedSetpointDeg",
            "-450",
            "630",
        ]
    )
    assert args.assert_key == ["Shooter/turretUsedUnwindFallback"]
    assert args.assert_range == [["Shooter/turretResolvedSetpointDeg", "-450", "630"]]


def test_sandbox_run_parser_accepts_output_controls() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "sandbox",
            "run",
            "--name",
            "test",
            "--max-lines",
            "10",
            "--no-tail",
            "--include",
            "WARN|ERROR",
            "--",
            "sim",
            "--duration",
            "5",
        ]
    )
    assert args.sandbox_command == "run"
    assert args.command == ["--", "sim", "--duration", "5"]
    assert args.max_lines == 10
    assert args.tail is False
    assert args.include == "WARN|ERROR"
