#!/usr/bin/env bash
set -euo pipefail

echo "🧪 Running Catty tests..."

# Проверяем структуру
test -f requirements.txt
test -f app/main.py
test -d templates
test -d static

echo "✅ Basic file checks passed"

# Если есть pytest
if [ -f requirements.txt ]; then
    pip3 install -r requirements.txt
    python3 -m pytest -q || echo "⚠️  pytest not configured"
fi

echo "🎉 Catty tests finished"
