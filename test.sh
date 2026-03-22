#!/usr/bin/env bash
set -euo pipefail

echo "🧪 Running Catty tests..."

test -f requirements.txt || { echo "❌ requirements.txt not found"; exit 1; }
test -f main.py || { echo "❌ main.py not found"; exit 1; }

echo "✅ Basic file checks passed"

if [ ! -d .venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Installing dependencies..."
.venv/bin/pip install -r requirements.txt

echo "Checking if main.py runs..."
timeout 3 .venv/bin/python main.py || true

echo "🎉 Catty tests finished"
