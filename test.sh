#!/usr/bin/env bash
set -euo pipefail

echo "🧪 Running Catty tests..."

test -f requirements.txt
test -f app/main.py
test -d templates
test -d static

echo "✅ Basic file checks passed"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q

echo "🎉 Catty tests finished"
