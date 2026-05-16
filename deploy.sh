#!/bin/bash

set -e

REPO_DIR="/home/qzm/Desktop/catty-reminders-app"
TARGET_COMMIT=$1

echo "> Deploying commit $TARGET_COMMIT"

cd "$REPO_DIR"

sudo git reset --hard HEAD || true

sudo git fetch origin

sudo git checkout -f "$TARGET_COMMIT"

DEPLOY_REF=$(git rev-parse HEAD)
echo "DEPLOY_REF=$DEPLOY_REF" | sudo tee "$REPO_DIR/.env.deploy"
sudo chmod 644 "$REPO_DIR/.env.deploy"
sudo chown qzm:qzm "$REPO_DIR/.env.deploy"

echo "> Deploy ref updated to: $DEPLOY_REF"

if [ -d ".venv" ]; then
    source .venv/bin/activate
    if [ -f "requirements.txt" ]; then
        echo "> Updating requirements..."
        pip install --upgrade pip
        pip install -r requirements.txt
    fi
    deactivate
fi

echo "> Restarting app.service..."
sudo systemctl daemon-reload
sudo systemctl restart app.service
echo "> Done!"
