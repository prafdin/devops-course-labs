#!/bin/bash
set -e
REPO_DIR="/home/qzm/Desktop/catty-reminders-app"
BRANCH="lab1"

git reset --hard
git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH"
git pull origin "$BRANCH"

source .venv/bin/activate
pip install -r requirements.txt -q

DEPLOY_REF=$(git rev-parse --short HEAD)
if grep -q "DEPLOY_REF=" "$REPO_DIR/.env"; then
    sed -i "s/DEPLOY_REF=.*/DEPLOY_REF=$DEPLOY_REF/" "$REPO_DIR/.env"
else
    echo "DEPLOY_REF=$DEPLOY_REF" >> "$REPO_DIR/.env"
fi

echo "[DEPLOY] Перезапуск приложения через systemd..."
sudo fuser -k 8181/tcp || true
sudo systemctl restart devops-app.service
