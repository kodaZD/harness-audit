---
name: harness-audit
description: Use when auditing historical coding-agent sessions, skill usage, MCP usage, tool friction, validation signals, or user collaboration patterns. Reports are local, read-only, and evidence-oriented.
---

# Harness audit

Use the local `harness-audit` CLI to inspect OpenCode-compatible session data.

## Commands

```bash
harness-audit report --since 7d
harness-audit skills --since 30d
harness-audit mcp --since 30d
harness-audit inspect <session-id> --since 90d
harness-audit user-report --since 14d
```

## Interpretation rules

- Call counts show usage, not effectiveness.
- Error rates are leads; classify infrastructure errors separately from input or workflow errors.
- A validation signal does not prove that a change was correct.
- Skill/MCP effectiveness requires a comparable cohort or controlled experiment.
- User reports are collaboration coaching, never personality or productivity judgements.
- Never commit raw session databases, prompts, tool inputs, secrets, or generated reports.
