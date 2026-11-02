# Experiment procedure

Experiments are intentionally separate from routine audit collection.

## Lifecycle

```text
open -> candidate prepared -> evaluated -> adopted | rejected | inconclusive
```

`experiment-open` only creates the first state. It never edits the active
OpenCode configuration, skill files, MCP configuration, or Routed weights.

## Required manifest fields

- hypothesis
- baseline harness/config fingerprint
- candidate change and exact files
- frozen task/prompt set
- model and tool/MCP configuration
- acceptance criteria
- observed cost, latency, errors, validation, and outcome
- rollback or expiry decision

## Causal caution

Historical sessions can identify candidates and correlations. A claim that a
skill or MCP improved outcomes needs a comparable cohort or controlled baseline
and candidate run.
