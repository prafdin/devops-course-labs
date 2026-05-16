#!/bin/bash
set -x

REPO_DIR="/home/qzm/Desktop/catty-reminders-app"
TARGET_COMMIT=$1

echo "> Starting deploy for commit: $TARGET_COMMIT"
cd "$REPO_DIR"

echo "> Resetting local changes..."
sudo git reset --hard HEAD

echo "> Fetching from origin..."
sudo git fetch --all

echo "> Checking out commit $TARGET_COMMIT..."
if ! sudo git checkout -f "$TARGET_COMMIT"; then
    echo "ERROR: Failed to checkout commit $TARGET_COMMIT. Maybe it was not fetched?"
    exit 1
fi

echo "> Writing DEPLOY_REF..."
DEPLOY_REF=$(sudo git rev-parse HEAD)
echo "DEPLOY_REF=$DEPLOY_REF" | sudo tee "$REPO_DIR/.env.deploy"
sudo chmod 644 "$REPO_DIR/.env.deploy"
sudo chown qzm:qzm "$REPO_DIR/.env.deploy"

if [ -d ".venv" ]; then
    echo "> Updating python dependencies..."
    source .venv/bin/activate
    pip install -r requirements.txt || echo "Pip install warning, continuing..."
    deactivate
fi

echo "> Restarting systemd service..."
sudo systemctl daemon-reload
sudo systemctl restart app.service

echo "> Deployment finished successfully!"
