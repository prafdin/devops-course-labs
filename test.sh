#!/usr/bin/env bash
set -euo pipefail

echo "🧪 Running Catty tests..."

# Basic file checks
test -f requirements.txt
test -f app/main.py
test -d templates
test -d static
echo "✅ Basic file checks passed"

# Setup venv if needed
if [ ! -d venv ]; then
    python3 -m venv venv
fi

# Install dependencies
venv/bin/pip install -r requirements.txt -q

# Install Playwright browsers if pytest-playwright is in requirements
if grep -q "pytest-playwright" requirements.txt; then
    echo "🌐 Installing Playwright browsers..."
    venv/bin/playwright install chromium --with-deps -q 2>&1 | head -20 || true
fi

# Run tests
echo "🔬 Running tests..."
venv/bin/python -m pytest -q -v 2>&1 | head -100

echo "🎉 Catty tests finished"
