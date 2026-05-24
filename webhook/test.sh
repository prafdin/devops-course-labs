#!/bin/bash
set -e

BRANCH=$1
APP_DIR="/home/ubuntu/devops/catty-reminders-app"

if [ -z "$BRANCH" ]; then
    echo "❌ No branch specified"
    exit 1
fi

echo "=== Запуск тестов ветки $BRANCH ==="

cd "$APP_DIR"

git fetch --all
git checkout -B "$BRANCH" "origin/$BRANCH" 2>/dev/null || git checkout "$BRANCH"
git pull origin "$BRANCH"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

pip install -q -r requirements.txt

python3 -m pytest -v --tb=short
