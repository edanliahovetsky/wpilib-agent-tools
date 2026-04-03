# Distribution Notes

This document explains the distribution strategy for the first public release of `wpilib-agent-tools`.

## Short version

For the first release, the project should be distributed as a **repo-first, GitHub-canonical** tool.

That means GitHub is the source of truth for:

- the code
- the docs
- the install scripts
- the supported setup flow
- releases / tags

## Why not center everything around `pipx` or PyPI?

Because this project is really two things:

1. a Python CLI
2. an agent setup / skill / workflow package

`pipx` and PyPI are good tools for distributing **Python CLIs**.
They do **not** automatically solve the full setup story for:

- Codex skills
- Cursor rules
- other agent harnesses
- repo-local workflow docs

So if the project were advertised mainly as a `pipx` or PyPI package right now, it would make the CLI feel cleaner while leaving the overall onboarding story fragmented.

## Distribution options

### 1. Repo-first / source-first

Users clone the repo and run:

```bash
./scripts/install_all.sh
```

### Pros

- lowest maintenance burden
- matches current project structure
- easiest to debug
- most honest for an experimental but useful tool

### Cons

- more friction than a one-line package install
- less polished for casual users

### 2. `pipx` from GitHub

Users install the CLI directly from the repo:

```bash
pipx install "git+https://github.com/edanliahovetsky/wpilib-agent-tools.git#subdirectory=agent"
```

### Pros

- clean CLI experience
- no PyPI publishing needed
- nice convenience path for power users

### Cons

- only solves the CLI cleanly
- still leaves skills/setup/docs elsewhere
- not ideal as the single headline onboarding story

### 3. PyPI

If the CLI is published to PyPI, users could install it with:

```bash
pipx install wpilib-agent-tools
```

### Pros

- best Python CLI UX
- familiar for many users
- good long-term path if the CLI becomes independently valuable

### Cons

- adds package publishing/release overhead
- still does not solve the skill/setup half by itself
- can over-signal polish if the rest of the workflow is still repo-driven

### 4. GitHub Releases

The repo can publish tagged releases with built artifacts.

### Pros

- versioned artifacts
- cleaner than “clone main”
- useful for release history and reproducibility

### Cons

- still needs repo docs to explain setup
- adds some release management overhead

### 5. Agent-specific installers

Longer term, the project could grow more polished per-platform integrations for:

- Codex
- Claude Code
- Cursor
- other MCP/plugin ecosystems

### Pros

- better UX per tool
- more “native” feeling installs

### Cons

- highest maintenance burden
- easy to fragment the docs
- not the best first-release investment

## Recommendation for this release

Use this structure:

### Primary

- GitHub repo
- `INSTALL.md`
- `./scripts/install_all.sh`

### Secondary

- `pipx` from GitHub for CLI-only users
- manual component install for advanced users

### Deferred

- PyPI
- polished multi-agent packaging
- more opinionated platform-specific installers

## Why this is the right tradeoff now

It matches the real state of the project:

- useful
- real
- worth trying
- not fully polished yet

It also keeps the public story honest:

- there is one recommended path
- alternate paths exist, but are not competing “official” stories
- future packaging improvements can happen after real user feedback
