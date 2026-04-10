#!/bin/bash
set -e

REPO_DIR="/home/pyshisha/devops-lab/catty-reminders-app"
BRANCH=$1

echo "=== Running tests on branch: $BRANCH ==="

cd "$REPO_DIR"
git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH"
git pull origin "$BRANCH"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv/
fi

source .venv/bin/activate
pip install -r requirements.txt

python -m pytest -v

echo "All tests passed!"
