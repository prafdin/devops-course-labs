#!/usr/bin/env bash
set -euo pipefail

echo "🧪 Running Catty tests..."

test -f requirements.txt
test -f app/main.py
test -d templates
test -d static

echo "✅ Basic file checks passed"

.venv/bin/python -m pytest -q

echo "🎉 Catty tests finished"
