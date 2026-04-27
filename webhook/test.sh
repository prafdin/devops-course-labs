#!/bin/bash
set -e

PROJECT_DIR="/home/vboxuser/devops-lab/catty-reminders-app"
BRANCH_NAME=$1

if [ -z "$BRANCH_NAME" ]; then
    echo "❌ No branch specified"
    exit 1
fi

echo "🧪 Running tests for branch: $BRANCH_NAME"

cd "$PROJECT_DIR"

git fetch --all
git checkout -B "$BRANCH_NAME" "origin/$BRANCH_NAME" 2>/dev/null || git checkout "$BRANCH_NAME"
git pull origin "$BRANCH_NAME"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

pip install -q -r requirements.txt

python3 -m pytest -v --tb=short
