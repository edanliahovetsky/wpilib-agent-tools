# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog and this project follows semantic versioning.

## [Unreleased]

### Added
- One-command installer `scripts/install_all.sh` for Codex + optional Cursor setup.
- Dedicated installers:
  - `scripts/install_cli.sh`
  - `scripts/install_cursor_rules.sh`
  - `scripts/install_harness_support.sh`
- Release readiness script `scripts/release_check.sh`.
- Make targets for install workflows and release checks.
- Tag-triggered GitHub release workflow at `.github/workflows/release.yml`.
- Top-level `LICENSE` for public repository sharing.
- Canonical install guide at `INSTALL.md`.
- Distribution notes at `docs/DISTRIBUTION.md`.
- Chief Delphi draft post at `docs/CHIEF_DELPHI_POST.md`.
- Shared `harness install` CLI support for Codex, Claude Code, and Cursor.

### Changed
- Root documentation now includes copy-paste onboarding for local dev, Codex users, and Cursor users.
- Root README now frames the project as a repo-first public release with one recommended install path and clearer maturity/distribution guidance.
- Install/docs now center a shared multi-harness installer path for Codex, Claude Code, and Cursor.

## [0.1.0] - 2026-02-19

### Added
- Initial `wpilib-agent-tools` CLI with sandbox-first sim/log/query workflows.
- Codex skill bundle at `skills/wpilib-agent-tools`.
- Validation and smoke tooling for local workflow verification.
