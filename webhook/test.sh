#!/bin/bash
set -e
REPO_DIR="/home/qzm/Desktop/catty-reminders-app"
BRANCH=$1

cd "$REPO_DIR"
git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH"
git pull origin "$BRANCH"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv/
fi

source .venv/bin/activate
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
fi

echo "[TEST] Запуск pytest..."
python3 -m pytest -v
