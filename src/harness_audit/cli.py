from __future__ import annotations

import argparse
import json
import os
import sqlite3
from pathlib import Path

from .audit import aggregate, collect, harness_fingerprint, now, report_by_dimension


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Local, read-only coding-agent audit")
    root.add_argument("--db", type=Path, default=Path(os.environ.get("OPENCODE_DB", Path.home() / ".local/share/opencode/opencode.db")))
    sub = root.add_subparsers(dest="command", required=True)
    for name in ("report", "skills", "mcp", "user-report"):
        command = sub.add_parser(name)
        command.add_argument("--since", default="7d")
        command.add_argument("--limit", type=int)
        command.add_argument("--name")
        command.add_argument("--json", action="store_true")
        command.add_argument("--output-dir", type=Path)
    inspect = sub.add_parser("inspect")
    inspect.add_argument("session_id")
    inspect.add_argument("--since", default="90d")
    experiment = sub.add_parser("experiment-open")
    experiment.add_argument("--title", required=True)
    experiment.add_argument("--hypothesis", required=True)
    experiment.add_argument("--source-bundle")
    return root


def main() -> int:
    args = parser().parse_args()
    if args.command == "experiment-open":
        root = Path(os.environ.get("HARNESS_AUDIT_ROOT", Path.home() / ".local/share/harness-audit")) / "experiments"
        root.mkdir(parents=True, exist_ok=True)
        path = root / f"exp-{now().strftime('%Y%m%dT%H%M%SZ')}.json"
        path.write_text(json.dumps({"schema_version": 1, "status": "open", "title": args.title, "hypothesis": args.hypothesis, "source_bundle": args.source_bundle, "baseline_harness": harness_fingerprint(), "evaluation": {"outcome": "not_run"}}, indent=2) + "\n")
        print(path)
        return 0
    sessions = collect(args.db, args.since, args.limit)
    if args.command == "inspect":
        found = next((session for session in sessions if session["session_id"] == args.session_id), None)
        if not found:
            raise SystemExit(f"session not found in {args.since}: {args.session_id}")
        print(json.dumps(found, indent=2))
        return 0
    if args.command == "skills":
        data = report_by_dimension(sessions, "skills", args.name)
    elif args.command == "mcp":
        data = report_by_dimension(sessions, "mcp", args.name)
    elif args.command == "user-report":
        data = {"mode": "on-demand", "privacy": "aggregate signals only; not a personality or productivity assessment", "suggestions": []}
        for session in sessions:
            if session["metrics"]["tool_calls"] >= 400 and session["metrics"]["delegations"] >= 10:
                data["suggestions"].append({"session_id": session["session_id"], "pattern": "bounded-brief-and-delegation-budget", "evidence": session["metrics"], "recommendation": "State scope, allowed actions, validation target, workstreams, and expected integration artifact up front.", "confidence": "low"})
    else:
        data = {"schema_version": 1, "since": args.since, "created_at": now().isoformat(), "harness": harness_fingerprint(), "aggregate": aggregate(sessions), "sessions": sessions}
    if args.command == "report":
        output = args.output_dir or Path(os.environ.get("HARNESS_AUDIT_ROOT", Path.home() / ".local/share/harness-audit")) / "bundles"
        bundle = output / f"{now().strftime('%Y%m%dT%H%M%S%fZ')}-{args.since}"
        bundle.mkdir(parents=True, exist_ok=False)
        (bundle / "report.json").write_text(json.dumps(data, indent=2) + "\n")
        store = output.parent / "store"
        store.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(store / "audit.sqlite")
        connection.execute("CREATE TABLE IF NOT EXISTS audit_runs (bundle_path TEXT PRIMARY KEY, created_at TEXT NOT NULL, since_window TEXT NOT NULL, harness_fingerprint TEXT NOT NULL, aggregate_json TEXT NOT NULL)")
        connection.execute("CREATE TABLE IF NOT EXISTS session_snapshots (bundle_path TEXT NOT NULL, session_id TEXT NOT NULL, updated_at TEXT, harness_fingerprint TEXT NOT NULL DEFAULT '', session_json TEXT NOT NULL, PRIMARY KEY (bundle_path, session_id))")
        connection.execute("INSERT OR REPLACE INTO audit_runs VALUES (?, ?, ?, ?, ?)", (str(bundle), data["created_at"], args.since, data["harness"]["fingerprint"], json.dumps(data["aggregate"])))
        columns = {row[1] for row in connection.execute("PRAGMA table_info(session_snapshots)")}
        if "harness_fingerprint" not in columns:
            connection.execute("ALTER TABLE session_snapshots ADD COLUMN harness_fingerprint TEXT NOT NULL DEFAULT ''")
        connection.executemany("INSERT OR REPLACE INTO session_snapshots (bundle_path, session_id, updated_at, harness_fingerprint, session_json) VALUES (?, ?, ?, ?, ?)", [(str(bundle), s["session_id"], s["updated_at"], data["harness"]["fingerprint"], json.dumps(s)) for s in sessions])
        connection.commit()
        connection.close()
        if not args.json:
            totals = data["aggregate"]["totals"]
            print("# Harness Audit\n")
            print(f"- Window: `{args.since}`\n- Sessions: `{data['aggregate']['session_count']}`")
            print(f"- Tool calls: {totals.get('tool_calls', 0):,}\n- Tool errors: {totals.get('tool_errors', 0):,}")
            print(f"- Evidence bundle: `{bundle}`")
            return 0
    print(json.dumps(data, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
