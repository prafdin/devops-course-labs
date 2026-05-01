#!/bin/bash

REPO_DIR="/home/nightainted/catty-reminders-app"
BRANCH=${1:-lab1}
ENV_FILE="$REPO_DIR/.env"

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting deployment for: $BRANCH"

cd "$REPO_DIR" || { echo "Error: Could not enter $REPO_DIR"; exit 1; }

echo "[deploy] Fetching changes..."
git fetch origin
git reset --hard "origin/$BRANCH"

COMMIT_HASH=$(git rev-parse HEAD)
echo "[deploy] Current commit hash: $COMMIT_HASH"

echo "[deploy] Updating $ENV_FILE"

if [ ! -f "$ENV_FILE" ]; then
    touch "$ENV_FILE"
fi

sed -i '/DEPLOY_REF/d' "$ENV_FILE"

echo "DEPLOY_REF=$COMMIT_HASH" >> "$ENV_FILE"

echo "[deploy] New entry in .env: $(grep "DEPLOY_REF" "$ENV_FILE")"

APP_SERVICE="catty-app.service"
echo "[deploy] Restarting $APP_SERVICE..."

if sudo systemctl restart "$APP_SERVICE"; then
    echo "[deploy] Service restarted successfully."
else
    echo "[deploy] ERROR: Failed to restart $APP_SERVICE"
    exit 1
fi

echo "[deploy] Deployment of $COMMIT_HASH finished successfully."
