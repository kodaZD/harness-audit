#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 -m pip install --user -e "$ROOT"
echo "Installed harness-audit from $ROOT"
echo "Configure the OpenCode skill/command from $ROOT/opencode/"
