#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PY="${PY:-python3}"
if [ -x .venv/bin/python ]; then PY=.venv/bin/python; fi

echo "== 1/4 secret scan =="
if grep -rInE '(password|secret|token|api[_-]?key)\s*=\s*["'\''][^"'\'']{8,}' \
     --include='*.py' --include='*.js' --include='*.sh' backend scripts tests frontend 2>/dev/null; then
  echo "SECRET SCAN: FAIL"; exit 1
fi
echo "secret scan: ok"

echo "== 2/4 syntax =="
$PY -m compileall -q backend scripts >/dev/null && echo "python: ok"

echo "== 3/4 test suite =="
$PY -m pytest -q

echo "== 4/4 drift gate =="
bash scripts/drift-gate.sh

echo "LOCAL CI: ALL GREEN"
