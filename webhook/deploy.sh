#!/bin/bash
set -e
REPO_DIR="/home/qzm/Desktop/catty-reminders-app"
BRANCH=$1

cd "$REPO_DIR"
git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH"
git pull origin "$BRANCH"

source .venv/bin/activate
pip install -r requirements.txt -q

DEPLOY_REF=$(git rev-parse HEAD)
echo "DEPLOY_REF=$DEPLOY_REF" > "$REPO_DIR/.env.deploy"

echo "[DEPLOY] Перезапуск приложения через systemd..."
sudo systemctl restart devops-app.service
