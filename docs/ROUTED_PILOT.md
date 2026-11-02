# Routed pilot record

This repository keeps the routing policy and benchmark format, but not a
machine-specific skill catalog or generated local index.

## Approved pilot scope

- English-only prompts.
- Catalog-only operation.
- No OpenCode adapter installation.
- No MCP enablement.
- No automatic skill loading.
- Candidate experiments may be opened but are not auto-adopted.

## Baseline record

The initial isolated curated run used 32 cases and 15 skills:

| Metric | Result |
|---|---:|
| Top-1 accuracy | 84.4% |
| Top-3 recall | 84.4% |
| No-skill accuracy | 83.3% |
| False-accept rate | 16.7% |
| False-decline rate | 7.7% |
| Mean latency | 1.7ms |

The promotion gate remains unmet. Before enabling routing, expand the positive,
no-skill, adversarial, and independent holdout sets and reduce false accepts.

Known failure classes were generic edits, taint-specific language, knowledge
base search wording, negated review, and negated Docker inspection.
