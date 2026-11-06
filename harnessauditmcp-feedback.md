# Feedback for harness-audit MCP

## Context

The current audit was run to understand how the AOS is being used across
ZaloAIChallenge and VerQuantumCir. The audit is useful as a privacy-first,
observational layer, but the current output is not yet sufficient to evaluate a
long-lived autonomous AOS loop or to distinguish healthy autonomy from
unbounded orchestration.

Observed aggregate signals in the recent audit window included high volumes of
tool calls, delegation, input tokens, and tool errors. The most useful recurring
signals were:

- delegation and timeout volume;
- stale `apply_patch` failures;
- missing-path/read failures;
- GitNexus readiness failures;
- session outcomes such as `changed_with_validation_signal` and
  `investigation_or_advice`.

The current report is valuable for discovery, but repository attribution and
loop-level analysis need to be stronger.

## Requested improvements

### 1. First-class project/repository attribution

Add stable fields for:

```yaml
project_id:
repository_root:
repository_remote:
branch:
worktree:
task_id:
mission_id:
experiment_id:
```

The current `--name` behavior does not provide a reliable repository-scoped
report when sessions touch multiple repositories or when repository identity
appears only in file paths and titles.

Suggested commands:

```bash
harness-audit report --repo ZaloAIChallenge
harness-audit report --repo VerQuantumCir
harness-audit loops --mission <id>
```

### 2. Mission/loop telemetry

Add a loop-oriented report with:

- mission duration;
- iteration count;
- active and completed child tasks;
- tool calls per iteration;
- delegation fan-out and depth;
- retries by diagnostic class;
- checkpoints created;
- escalations;
- human interventions;
- final outcome;
- cost and token usage per phase.

The report should distinguish a healthy long loop from a runaway session.

### 3. Delegation graph and budget telemetry

Expose:

- parent task and child task IDs;
- delegation depth;
- parallel worker count;
- max and actual delegation budget;
- child timeout versus child completion;
- duplicate work after timeout;
- cancelled, superseded, and orphaned children.

This is essential for diagnosing the current pattern of large sessions with
many delegations and timeout-related uncertainty.

### 4. Error taxonomy instead of only error signatures

Normalize errors into categories:

```text
stale_source
missing_path
tool_unavailable
timeout
invalid_arguments
patch_conflict
environment_failure
schema_failure
permission_or_ownership_conflict
```

Retain the raw signature, but make trends queryable by category.

### 5. State-transition and checkpoint telemetry

If the AOS emits task events, audit should count transitions such as:

```text
planned -> approved -> executing -> validating -> review_pending -> integrated
```

Also report:

- checkpoint frequency;
- resume success rate;
- stale checkpoint rate;
- tasks resumed from thread history instead of a durable checkpoint;
- state regressions;
- tasks completed with unreleased ownership.

### 6. Evidence quality metrics

Distinguish:

- narrative completion;
- focused validation;
- official verification;
- remote/deployment evidence;
- promotion evidence.

Report whether a changed session produced durable evidence and whether the
evidence was later consumed by review or integration.

### 7. Human-intervention and teacher-value metrics

For a loop-centric AOS, measure whether human attention is actually shifting
to teaching. Add fields such as:

- teacher sessions per mission;
- execution sessions per teacher session;
- human interventions per 10 loop iterations;
- escalation acceptance/rejection rate;
- teacher summary usefulness feedback;
- repeated explanation requests;
- decisions made from a teacher summary versus raw execution transcript.

### 8. Capability readiness and fallback telemetry

Record whether a capability was ready before use:

```yaml
capability: gitnexus
status: ready | degraded | unavailable
fallback_used: true
fallback_kind: text_search
```

This would make repeated calls to unavailable tools visible as a readiness
problem instead of merely a tool-error count.

### 9. Cost and context-efficiency reports

Add:

- input/output tokens per successful artifact;
- context refresh count;
- repeated reads of the same file;
- tool calls after a known stale state;
- cost per validated hypothesis;
- cost per promoted change;
- cost per useful teacher lesson.

Raw token volume alone does not tell whether a long mission was productive.

### 10. Privacy-preserving cohort comparison

Keep aggregate-only defaults, but support opt-in cohort labels:

```yaml
workflow_profile: bounded_task | autonomous_mission | research_experiment
project_type: software | benchmark | research | deployment
```

This would allow comparing workflow profiles without exposing prompt contents or
secrets.

## Suggested priority

1. Reliable repository/task/mission attribution.
2. Error taxonomy and capability readiness.
3. Delegation graph and timeout/duplicate-work detection.
4. Checkpoint/resume and evidence metrics.
5. Teacher-value and cost-per-outcome metrics.

## Desired outcome

The audit should answer:

> Is this autonomous loop progressing toward a project outcome with bounded
> cost and increasing understanding, or is it accumulating activity, retries,
> and context without durable progress?
