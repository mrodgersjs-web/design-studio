#!/usr/bin/env bash
# End-to-end smoke for design-studio:
# 1. install the package + dev extras from a clean state
# 2. lint
# 3. test (including --cov)
# 4. exercise the tokens-toolkit CLI on the real tokens/base.json
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

test -f README.md
test -f docs/public-boundary.md
test -d assets
test -f tokens/base.json

PY="${PYTHON:-${GHUP_PY:-python3}}"
if [ "${SKIP_INSTALL:-0}" != "1" ]; then
  "$PY" -m pip install -q -e ".[dev]"
fi

export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

"$PY" -m ruff check .
"$PY" -m pytest -q
"$PY" -m pytest -q --cov=tokens_toolkit --cov-report=term

# Exercise the CLI on the real tokens/base.json
"$PY" -m tokens_toolkit.cli validate tokens/base.json > /tmp/smoke-validate.json
grep -q '"ok": true' /tmp/smoke-validate.json

echo "design-studio smoke PASS"
