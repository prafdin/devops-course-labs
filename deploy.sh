#!/bin/bash

REPO_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BRANCH=${1:-lab1}

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting deployment for branch: $BRANCH"
cd "$REPO_DIR" || { echo "Error: Could not enter $REPO_DIR"; exit 1; }

git fetch origin
git reset --hard "origin/$BRANCH"

COMMIT_HASH=$(git rev-parse --short HEAD)
echo "[deploy] Current commit hash: $COMMIT_HASH"

TARGET_FILE=$(grep -rEl "DEPLOY_REF\s*=" . --exclude-dir={venv,__pycache__,.git} | head -n 1)

if [ -n "$TARGET_FILE" ]; then
    echo "[deploy] Injecting hash into: $TARGET_FILE"
    sed -i "s/DEPLOY_REF\s*=.*/DEPLOY_REF = \"$COMMIT_HASH\"/" "$TARGET_FILE"
else
    echo "[deploy] WARNING: DEPLOY_REF variable not found in the codebase."
fi

APP_SERVICE="catty-app.service"
if systemctl list-unit-files | grep -q "$APP_SERVICE"; then
    echo "[deploy] Restarting $APP_SERVICE..."
    sudo systemctl restart "$APP_SERVICE"
else
    echo "[deploy] ERROR: Service $APP_SERVICE not found."
    exit 1
fi

echo "[deploy] Deployment of $COMMIT_HASH finished successfully."
