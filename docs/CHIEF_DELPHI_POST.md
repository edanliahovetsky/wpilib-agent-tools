# Chief Delphi Draft

## Title ideas

- `wpilib-agent-tools: repo-first agent tooling for WPILib sim, NT4, and WPILOG workflows`
- `wpilib-agent-tools - useful agentic tooling for closed-loop sim validation and log workflows`
- `Sharing wpilib-agent-tools: a repo-first workflow for sim/log analysis with coding agents`

## Draft post

Hey all,

I wanted to share a side project I have been working on: **`wpilib-agent-tools`**.

This is not a polished product release so much as a **useful experiment that has already been giving me real value**, especially around **closed-loop sim validation**, bounded simulation runs, and log-driven iteration.

At a high level, the repo currently packages two things together:

1. a Python CLI for WPILib sim / NT4 / WPILOG workflows
2. a Codex-oriented skill/workflow bundle for agentic coding

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
./scripts/install_all.sh
```

Right now I would describe it as:

- **useful enough to be worth trying**
- **still experimental**
- best when used with a stronger lead/orchestrator model
- better when high-thinking modes are enabled
- something to use thoughtfully, especially with token/subagent usage

So I am sharing this less as “here is the finished universal solution” and more as “here is something that is already helpful in practice and may be useful to other teams too.”

If people try it and have feedback on:

- the install story
- the workflow shape
- what parts are genuinely useful vs noisy
- how much value there is in the sim/log tooling vs the agent workflow layer

I would love to hear it.

GitHub repo: **[add repo link here before posting]**

## Notes before posting

- Replace the GitHub placeholder with the final public URL.
- Optionally trim the MCP paragraph if you want a shorter post.
- Optionally add one concrete screenshot / example output if you want the post to land faster.
