from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from wpilib_agent_tools.cli import build_parser
from wpilib_agent_tools.commands import rules


def _args(**overrides: object) -> argparse.Namespace:
    base: dict[str, object] = {
        "mode": "core",
        "target": "custom",
        "output_dir": None,
        "force": False,
        "json": True,
    }
    base.update(overrides)
    return argparse.Namespace(**base)


def test_rules_cli_parser_registers_install_command() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "rules",
            "install",
            "--mode",
            "both",
            "--target",
            "custom",
            "--output-dir",
            "/tmp/rules",
        ]
    )
    assert args.command == "rules"
    assert args.rules_command == "install"
    assert args.mode == "both"


def test_rules_install_custom_target_installs_selected_templates(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output_dir = tmp_path / "rules"
    exit_code = rules.handle_install(_args(mode="both", output_dir=str(output_dir), json=True))

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    installed_names = sorted(Path(path).name for path in payload["installed"])
    assert installed_names == sorted(
        ["wpilib-agent-tools-core.mdc", "wpilib-agent-tools-scoped.mdc"]
    )
    assert payload["overwritten"] == []
    assert payload["skipped"] == []

    core_text = (output_dir / "wpilib-agent-tools-core.mdc").read_text(encoding="utf-8")
    scoped_text = (output_dir / "wpilib-agent-tools-scoped.mdc").read_text(encoding="utf-8")
    assert "WPILib Agent Tools Core Rule" in core_text
    assert "WPILib Agent Tools Scoped Rule" in scoped_text


def test_rules_install_skips_existing_without_force(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output_dir = tmp_path / "rules"
    output_dir.mkdir(parents=True, exist_ok=True)
    core_path = output_dir / "wpilib-agent-tools-core.mdc"
    core_path.write_text("manual-content", encoding="utf-8")

    exit_code = rules.handle_install(_args(mode="core", output_dir=str(output_dir), force=False, json=True))

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["installed"] == []
    assert payload["overwritten"] == []
    assert len(payload["skipped"]) == 1
    assert payload["skipped"][0]["path"] == str(core_path)
    assert "use --force to overwrite" in payload["skipped"][0]["reason"]
    assert core_path.read_text(encoding="utf-8") == "manual-content"


def test_rules_install_overwrites_existing_with_force(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output_dir = tmp_path / "rules"
    output_dir.mkdir(parents=True, exist_ok=True)
    core_path = output_dir / "wpilib-agent-tools-core.mdc"
    core_path.write_text("manual-content", encoding="utf-8")

    exit_code = rules.handle_install(_args(mode="core", output_dir=str(output_dir), force=True, json=True))

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["installed"] == []
    assert payload["skipped"] == []
    assert payload["overwritten"] == [str(core_path)]
    assert "WPILib Agent Tools Core Rule" in core_path.read_text(encoding="utf-8")


def test_rules_install_custom_target_requires_output_dir(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = rules.handle_install(_args(target="custom", output_dir=None, json=False))
    assert exit_code == 2
    assert "--output-dir is required when --target custom is used" in capsys.readouterr().out


def test_rule_templates_keep_critical_safety_guidance() -> None:
    core_text = rules._read_template(rules.CORE_TEMPLATE_FILE)
    scoped_text = rules._read_template(rules.SCOPED_TEMPLATE_FILE)

    assert "sandbox create --name <id> --source workspace" in core_text
    assert "Apply reviewed patch to workspace only after explicit approval." in core_text
    assert "--json" in core_text
    assert "Prefer concise/summary output and assertions over raw log dumps." in core_text
    assert "Define acceptance checks first" in core_text
    assert "Start with the minimum run set" in core_text
    assert "wpilib-agent-tools --help" in core_text
    assert "DriverStationSim.setAutonomous(true);" in core_text
    assert "DriverStationSim.setEnabled(true);" in core_text
    assert "DriverStationSim.notifyNewData();" in core_text

    assert "confirm how the repo switches between simulation and IRL modes" in scoped_text
    assert "prefer assertions and concise summaries over full raw logs" in scoped_text
    assert "Keep run count adaptive to acceptance criteria" in scoped_text
    assert "DriverStationSim.setAutonomous(true);" in scoped_text
    assert "DriverStationSim.setEnabled(true);" in scoped_text
    assert "DriverStationSim.notifyNewData();" in scoped_text
    assert "after explicit approval" in scoped_text
