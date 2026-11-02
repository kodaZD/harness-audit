---
name: past
description: Review historical OpenCode sessions with harness-audit
agent: general
---

Run `harness-audit report --since 7d` for a redacted aggregate report. Use
`harness-audit inspect <session-id> --since 90d` for one session, and use
`harness-audit skills` or `harness-audit mcp` when the question is about
effectiveness evidence. Do not query an old `event` table directly.
