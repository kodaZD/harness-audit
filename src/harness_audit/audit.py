from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SENSITIVE = re.compile(r"(?i)(api[_-]?key|authorization|bearer\s+|token|password|secret|private[_-]?key)")
MCP_PREFIXES = ("basic-memory_", "gitnexus_", "playwright_", "t3-code_", "searchapi_", "list_mcp_", "read_mcp_")


def now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def timestamp(value: int | None) -> str | None:
    return dt.datetime.fromtimestamp(value / 1000, tz=dt.timezone.utc).isoformat() if value else None


def parse_since(value: str) -> int:
    match = re.fullmatch(r"(\d+)([dhw])", value)
    if not match:
        raise ValueError("--since must use Nd, Nh, or Nw, for example 30d")
    return int((now() - dt.timedelta(**{"hours": int(match[1]) * {"h": 1, "d": 24, "w": 168}[match[2]]})).timestamp() * 1000)


def decode(value: str) -> dict[str, Any]:
    try:
        result = json.loads(value)
        return result if isinstance(result, dict) else {}
    except (TypeError, json.JSONDecodeError):
        return {}


def excerpt(value: str, limit: int = 180) -> str:
    value = " ".join(str(value).split())
    if SENSITIVE.search(value):
        return "[redacted: sensitive-looking content]"
    return value[:limit] + ("..." if len(value) > limit else "")


def fingerprint_path(path: Path) -> str:
    digest = hashlib.sha256()
    if not path.exists():
        return "missing"
    files = [path] if path.is_file() else sorted(path.rglob("*"))
    for file in files:
        if not file.is_file() or "__pycache__" in file.parts:
            continue
        digest.update(str(file.relative_to(path) if path.is_dir() else file.name).encode())
        digest.update(b"\0")
        digest.update(file.read_bytes())
    return digest.hexdigest()[:16]


def harness_fingerprint(home: Path | None = None) -> dict[str, str]:
    home = home or Path.home()
    roots = {
        "config": home / ".config/opencode/opencode.jsonc",
        "agents": home / ".config/opencode/agent",
        "commands": home / ".config/opencode/command",
        "local_skills": home / ".config/opencode/skill",
        "extended_skills": home / ".config/opencode/skills",
        "external_skills": home / ".agents/skills",
    }
    parts = {key: fingerprint_path(value) for key, value in roots.items()}
    parts["fingerprint"] = hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:16]
    return parts


def tool_category(name: str) -> str:
    if name == "skill":
        return "skill"
    if name in {"task", "t3-code_delegate_task", "t3-code_task_status", "t3-code_t3_thread_wait"}:
        return "delegation"
    if name in {"apply_patch", "edit", "write"}:
        return "mutation"
    if name in {"bash", "read", "grep", "glob"}:
        return "investigation"
    if name.startswith("gitnexus_"):
        return "mcp:gitnexus"
    if name.startswith("basic-memory_"):
        return "mcp:basic-memory"
    if name.startswith("playwright_"):
        return "mcp:playwright"
    if name.startswith("t3-code_"):
        return "mcp:t3-code"
    if name.startswith(("searchapi_", "list_mcp_", "read_mcp_")):
        return "mcp:other"
    return "other"


def mcp_server(name: str) -> str | None:
    category = tool_category(name)
    return category.removeprefix("mcp:") if category.startswith("mcp:") else None


def collect(db_path: Path, since: str, limit: int | None = None) -> list[dict[str, Any]]:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    query = "SELECT * FROM session WHERE time_updated >= ? ORDER BY time_updated DESC"
    params: list[Any] = [parse_since(since)]
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    result: list[dict[str, Any]] = []
    for session in connection.execute(query, params):
        events: dict[str, dict[str, Any]] = {}
        for part in connection.execute("SELECT id,data FROM part WHERE session_id=? ORDER BY time_created", (session["id"],)):
            data = decode(part["data"])
            if data.get("type") != "tool":
                continue
            events[str(data.get("callID") or part["id"])] = data
        tools: Counter[str] = Counter()
        errors: Counter[str] = Counter()
        skills: Counter[str] = Counter()
        mcp: Counter[str] = Counter()
        for event in events.values():
            name = str(event.get("tool") or event.get("toolName") or "unknown")
            tools[name] += 1
            server = mcp_server(name)
            if server:
                mcp[f"{server}:{name}"] += 1
            state = event.get("state") if isinstance(event.get("state"), dict) else {}
            if state.get("status") == "error" or state.get("error"):
                errors[f"{name}: {excerpt(state.get('error') or 'tool error', 240)}"] += 1
            if name == "skill":
                value = state.get("input") or {}
                skills[str(value.get("name") or "(unknown)")] += 1
        mutation = sum(tools[name] for name in ("apply_patch", "edit", "write"))
        validation = sum(tools[name] for name in ("bash", "gitnexus_detect_changes", "gitnexus_review"))
        outcome = "unknown"
        if mutation and validation:
            outcome = "changed_with_validation_signal"
        elif mutation:
            outcome = "changed_without_validation_signal"
        elif tools:
            outcome = "investigation_or_advice"
        result.append({
            "session_id": session["id"],
            "title": session["title"] or "(untitled)",
            "agent": session["agent"] or "unknown",
            "model": session["model"] or "unknown",
            "created_at": timestamp(session["time_created"]),
            "updated_at": timestamp(session["time_updated"]),
            "metrics": {
                "tool_calls": sum(tools.values()),
                "tool_errors": sum(errors.values()),
                "tokens_input": session["tokens_input"] or 0,
                "tokens_output": session["tokens_output"] or 0,
                "cost_usd": session["cost"] or 0,
                "delegations": sum(value for name, value in tools.items() if tool_category(name) == "delegation"),
            },
            "tool_counts": dict(tools),
            "error_signatures": dict(errors.most_common(10)),
            "skills": dict(skills),
            "mcp": dict(mcp),
            "outcome": outcome,
        })
    connection.close()
    return result


def aggregate(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    totals = Counter()
    tools: Counter[str] = Counter()
    errors: Counter[str] = Counter()
    skills: Counter[str] = Counter()
    mcp: Counter[str] = Counter()
    outcomes: Counter[str] = Counter()
    for session in sessions:
        totals.update(session["metrics"])
        tools.update(session["tool_counts"])
        errors.update(session["error_signatures"])
        skills.update(session["skills"])
        mcp.update(session["mcp"])
        outcomes[session["outcome"]] += 1
    return {
        "session_count": len(sessions),
        "totals": dict(totals),
        "top_tools": tools.most_common(30),
        "top_errors": errors.most_common(20),
        "skills": skills.most_common(),
        "mcp": mcp.most_common(),
        "outcomes": dict(outcomes),
    }


def report_by_dimension(sessions: list[dict[str, Any]], dimension: str, name: str | None = None) -> dict[str, Any]:
    rows: defaultdict[str, dict[str, Any]] = defaultdict(lambda: {"calls": 0, "sessions": set(), "errors": 0, "validation_sessions": 0, "changed_sessions": 0})
    for session in sessions:
        values = session[dimension]
        for key, calls in values.items():
            if name and name.lower() not in key.lower():
                continue
            row = rows[key]
            row["calls"] += calls
            row["sessions"].add(session["session_id"])
            row["errors"] += sum(count for signature, count in session["error_signatures"].items() if signature.startswith(key.split(":", 1)[-1] + ":"))
            if session["outcome"] == "changed_with_validation_signal":
                row["validation_sessions"] += 1
            if session["outcome"].startswith("changed_"):
                row["changed_sessions"] += 1
    output = []
    for key, row in sorted(rows.items(), key=lambda item: item[1]["calls"], reverse=True):
        row["sessions"] = len(row["sessions"])
        row["validation_rate"] = round(row["validation_sessions"] / row["sessions"], 4) if row["sessions"] else 0
        row["change_rate"] = round(row["changed_sessions"] / row["sessions"], 4) if row["sessions"] else 0
        output.append({"name": key, **row})
    return {"dimension": dimension, "filter": name, "rows": output}
