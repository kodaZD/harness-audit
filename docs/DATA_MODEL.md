# Data model

The collector derives session-level records from `session`, `message`, and
`part` tables. Tool lifecycle parts are deduplicated by `callID` when available.

## Skill attribution

The `skill` tool input is counted by the requested skill name. The report then
groups the enclosing session's mutation, validation, error, and outcome signals.
This is observational attribution: it does not prove the skill caused the
outcome.

## MCP attribution

Known tool prefixes are grouped into server families:

- `basic-memory_*` → `basic-memory`
- `gitnexus_*` → `gitnexus`
- `playwright_*` → `playwright`
- `t3-code_*` → `t3-code`

Unknown MCP tools remain in `mcp:other` only when they use the configured MCP
prefix set. Extend the mapping for a deployment rather than guessing from a
tool name in a report.

## Outcome signals

- `investigation_or_advice`: tools were used without a detected mutation.
- `changed_with_validation_signal`: mutation plus a known validation signal.
- `changed_without_validation_signal`: mutation without a known validation signal.
- `unknown`: no reliable outcome classification.

These are triage labels, not quality scores.
