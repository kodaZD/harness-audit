# Replication guide

`harness-audit` is designed to run locally against an OpenCode-compatible SQLite
database. It is read-only against the source database and stores only derived
reports when the operator asks for them.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
./scripts/test.sh
```

## Run

```bash
harness-audit report --since 7d
harness-audit skills --since 30d
harness-audit mcp --since 30d
harness-audit inspect <session-id> --since 90d
harness-audit user-report --since 14d
```

Set `OPENCODE_DB` to use another database. The default is
`~/.local/share/opencode/opencode.db`.

## Privacy boundary

- Raw session databases never belong in this repository.
- Reports can contain sensitive excerpts and must stay in local ignored paths.
- Do not commit session IDs, prompt text, tool inputs, secrets, local home paths,
  audit bundles, or generated databases.
- Skill/MCP effectiveness metrics are observational correlations. They are not
  causal claims without a controlled comparison.

## Routed pilot

The `config/routed/` files are policy and benchmark templates only. They do not
install a Routed adapter, enable MCP, load skills, or auto-edit an OpenCode
configuration. Keep routing catalog-only until the promotion gate is met on a
representative English-only holdout.
