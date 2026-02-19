# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog and this project follows semantic versioning.

## [Unreleased]

### Added
- One-command installer `scripts/install_all.sh` for Codex + optional Cursor setup.
- Dedicated installers:
  - `scripts/install_cli.sh`
  - `scripts/install_cursor_rules.sh`
- Release readiness script `scripts/release_check.sh`.
- Make targets for install workflows and release checks.
- Tag-triggered GitHub release workflow at `.github/workflows/release.yml`.

### Changed
- Root documentation now includes copy-paste onboarding for local dev, Codex users, and Cursor users.

## [0.1.0] - 2026-02-19

### Added
- Initial `wpilib-agent-tools` CLI with sandbox-first sim/log/query workflows.
- Codex skill bundle at `skills/wpilib-agent-tools`.
- Validation and smoke tooling for local workflow verification.
