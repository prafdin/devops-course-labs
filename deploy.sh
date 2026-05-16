#!/bin/bash
set -x

REPO_DIR="/home/qzm/Desktop/catty-reminders-app"
TARGET_COMMIT=$1

cd "$REPO_DIR"
sudo git reset --hard HEAD
sudo git fetch --all

if ! sudo git checkout -f "$TARGET_COMMIT"; then
    echo "ERROR: Failed to checkout commit $TARGET_COMMIT."
    exit 1
fi

DEPLOY_REF=$(sudo git rev-parse HEAD)
echo "DEPLOY_REF=$DEPLOY_REF" | sudo tee "$REPO_DIR/.env.deploy"
sudo chmod 644 "$REPO_DIR/.env.deploy"
sudo chown qzm:qzm "$REPO_DIR/.env.deploy"

if [ -d ".venv" ]; then
    source .venv/bin/activate
    pip install -r requirements.txt || echo "Warning..."
    deactivate
fi

sudo systemctl daemon-reload
sudo systemctl restart app.service
echo "> Done!"
