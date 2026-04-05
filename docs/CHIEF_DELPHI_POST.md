# Chief Delphi Draft

## Title ideas

- `wpilib-agent-tools: repo-first agent tooling for WPILib sim, NT4, and WPILOG workflows`
- `wpilib-agent-tools - useful agentic tooling for closed-loop sim validation and log workflows`
- `Sharing wpilib-agent-tools: a repo-first workflow for sim/log analysis with coding agents`

## Recommended final version

Hey all,

I wanted to share a side project I have been working on: **`wpilib-agent-tools`**.

It is basically a repo-first toolkit for agentic WPILib workflows — especially around **closed-loop sim validation**, bounded sim runs, NT4 recording, and WPILOG analysis. It now has a shared installer path for **Codex, Claude Code, and Cursor**. It is not a polished product, but it has already been genuinely useful for me and feels worth sharing in case it is useful to other teams too.

The repo currently bundles:

1. a Python CLI for sim / NT4 / WPILOG workflows
2. workspace support for Codex, Claude Code, and Cursor, plus a Codex skill/workflow bundle

This is **not MCP-based**. That was mostly a practicality decision for this project: I wanted the first version to stay simpler and more repo-first rather than spending more time building around MCP up front. I still think MCP is a really promising direction, and I also want to acknowledge some of the FRC projects exploring that path more directly:

- https://www.chiefdelphi.com/t/wip-model-context-protocol-for-frc-wpilog-and-nt4/517780
- https://www.chiefdelphi.com/t/advantagescope-and-elastic-dashboard-mcp-servers/515906
- https://www.chiefdelphi.com/t/first-agentic-csa-frc-ai-coding-enhancer-v2/508968

Current recommended setup flow:

```bash
git clone https://github.com/edanliahovetsky/wpilib-agent-tools.git
cd wpilib-agent-tools
./scripts/install_all.sh --workspace /path/to/robot-repo --harnesses all
```

I would describe it as:

- useful enough to be worth trying
- still experimental
- best with a stronger lead/orchestrator model
- something to use thoughtfully with token/subagent usage

If people try it and have feedback on the install story, workflow shape, or which parts are actually useful vs noisy, I would love to hear it.

GitHub repo: **https://github.com/edanliahovetsky/wpilib-agent-tools**

## Draft post

Hey all,

I wanted to share a side project I have been working on: **`wpilib-agent-tools`**.

This is not a polished product release so much as a **useful experiment that has already been giving me real value**, especially around **closed-loop sim validation**, bounded simulation runs, and log-driven iteration.

At a high level, the repo currently packages two things together:

1. a Python CLI for WPILib sim / NT4 / WPILOG workflows
2. workspace support for Codex, Claude Code, and Cursor, plus a Codex skill/workflow bundle

The rough goal is to make it easier to:

- run repeatable sandboxed experiments
- record or inspect NT4 / WPILOG data
- query and graph logs quickly
- give coding agents a better workflow surface around robot-code iteration

This is **not MCP-based**.

That was a conscious choice, not a statement against MCP. I looked at that direction, but for this project I wanted to keep the first version simpler and more repo-first. A CLI + workflow-doc/skill approach was easier to implement, easier to iterate on, and easier to keep honest for a first public release. There are definitely tradeoffs there, and I still think MCP is a really promising direction for a lot of FRC tooling.

I also want to explicitly acknowledge other community efforts in this space that are exploring the MCP side much more directly:

- **WIP Model Context Protocol for FRC (.wpilog and NT4)**  
  https://www.chiefdelphi.com/t/wip-model-context-protocol-for-frc-wpilog-and-nt4/517780
- **AdvantageScope and Elastic Dashboard MCP Servers**  
  https://www.chiefdelphi.com/t/advantagescope-and-elastic-dashboard-mcp-servers/515906
- **FIRST Agentic CSA - FRC AI Coding Enhancer v2** (including related docs-focused MCP work)  
  https://www.chiefdelphi.com/t/first-agentic-csa-frc-ai-coding-enhancer-v2/508968

Those projects are tackling adjacent problems from different angles, and I think that is good for the community.

For this repo specifically, the current recommendation is a **repo-first setup flow**:

```bash
git clone https://github.com/edanliahovetsky/wpilib-agent-tools.git
cd wpilib-agent-tools
./scripts/install_all.sh --workspace /path/to/robot-repo --harnesses all
```

Right now I would describe it as:

- **useful enough to be worth trying**
- **still experimental**
- best when used with a stronger lead/orchestrator model (for example Opus or GPT-5.4)
- better when high-thinking modes are enabled
- something to use thoughtfully, especially with token/subagent usage

So I am sharing this less as “here is the finished universal solution” and more as “here is something that is already helpful in practice and may be useful to other teams too.”

If people try it and have feedback on:

- the install story
- the workflow shape
- what parts are genuinely useful vs noisy
- how much value there is in the sim/log tooling vs the agent workflow layer

I would love to hear it.

GitHub repo: **https://github.com/edanliahovetsky/wpilib-agent-tools**

## Shorter version

Hey all,

I wanted to share a side project I have been working on: **`wpilib-agent-tools`**.

It is basically a repo-first toolkit for agentic WPILib workflows — especially around **closed-loop sim validation**, bounded sim runs, NT4 recording, and WPILOG analysis. It now has a shared installer path for **Codex, Claude Code, and Cursor**. It is not a polished product, but it has already been genuinely useful for me and feels worth sharing in case it is useful to other teams too.

The repo currently bundles:

1. a Python CLI for sim / NT4 / WPILOG workflows
2. workspace support for Codex, Claude Code, and Cursor, plus a Codex skill/workflow bundle

This is **not MCP-based**. That was mostly a practicality decision for this project: I wanted the first version to stay simpler and more repo-first rather than spending more time building around MCP up front. I still think MCP is a really promising direction, and I also want to acknowledge some of the FRC projects exploring that path more directly:

- https://www.chiefdelphi.com/t/wip-model-context-protocol-for-frc-wpilog-and-nt4/517780
- https://www.chiefdelphi.com/t/advantagescope-and-elastic-dashboard-mcp-servers/515906
- https://www.chiefdelphi.com/t/first-agentic-csa-frc-ai-coding-enhancer-v2/508968

Current recommended setup flow:

```bash
git clone https://github.com/edanliahovetsky/wpilib-agent-tools.git
cd wpilib-agent-tools
./scripts/install_all.sh --workspace /path/to/robot-repo --harnesses all
```

I would describe it as:

- useful enough to be worth trying
- still experimental
- best with a stronger lead/orchestrator model
- something to use thoughtfully with token/subagent usage

GitHub repo: **https://github.com/edanliahovetsky/wpilib-agent-tools**

## Notes before posting

- Replace the GitHub placeholder with the final public URL.
- Use the full draft if you want more context; use the shorter version if you want something faster to scan.
- Optionally add one concrete screenshot / example output if you want the post to land faster.
