#!/usr/bin/env bash
set -Eeuo pipefail

BRANCH="${1:-lab2}"
REQUESTED_SHA="${2:-}"
APP_DIR="/home/kali/catty-reminders-app"
APP_SERVICE="catty-app.service"

echo "Deploying branch '$BRANCH' into '$APP_DIR'"

cd "$APP_DIR"
git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH"

if [[ -n "$REQUESTED_SHA" ]]; then
    git reset --hard "$REQUESTED_SHA"
    echo "DEPLOY_REF=$REQUESTED_SHA" > .env
    echo "DEPLOY_REF=$REQUESTED_SHA" > .env
fi

# Проверка venv
if [[ ! -d ".venv" ]]; then
    python3 -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

# Перезапуск
sudo systemctl restart "$APP_SERVICE"
echo "Deployment completed!"
