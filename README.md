# harness-audit

Local, privacy-first auditing for coding-agent sessions, skills, MCP tools, and
user collaboration patterns.

## What it measures

- Session and tool volume, errors, token/cost signals, and delegation.
- Previously invoked skills and their surrounding session outcomes.
- MCP tool usage grouped by server and tool name.
- Validation and mutation signals as observational outcome indicators.
- On-demand user collaboration suggestions.

It does not claim that a skill or MCP caused an outcome. It produces evidence
for later cohort comparisons and approved experiments.

## Commands

```bash
harness-audit report --since 7d
harness-audit skills --since 30d
harness-audit mcp --since 30d
harness-audit user-report --since 14d
harness-audit inspect <session-id> --since 90d
harness-audit experiment-open --title "..." --hypothesis "..."
```

## Current policy

- User audit is on-demand.
- Candidate experiments open in `open` state and are never auto-adopted.
- Routed remains catalog-only and English-only.
- The curated route policy excludes orchestration/meta skills such as
  `gitnexus-plan`, `gitnexus-work`, and `gitnexus-lfg` from ambient routing.

See [`docs/REPLICATION.md`](docs/REPLICATION.md) for setup and privacy rules.

## Tests

The test suite uses Python's standard-library `unittest` so a clean Python
installation is enough:

```bash
./scripts/test.sh
```
