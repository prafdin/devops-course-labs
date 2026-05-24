#!/bin/bash
set -e

TARGET_DIR="/home/vboxuser/catty-reminders-app"

BRANCH=${1:-lab2}
COMMIT_SHA=$2

echo "cd to $TARGET_DIR..."
cd "$TARGET_DIR"

echo "fetch the latest version..."
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git reset --hard "origin/$BRANCH"

echo "wrighting hash into .env..."
if [ -z "$COMMIT_SHA" ] || [ "$COMMIT_SHA" == "unknown" ]; then
    COMMIT_SHA=$(git rev-parse HEAD)
fi
echo "DEPLOY_REF=$COMMIT_SHA" > "$TARGET_DIR/.env"

echo "update reqs..."
source .venv/bin/activate
pip install -r requirements.txt

echo "restarting app..."
sudo systemctl restart catty-app

echo "deployment ended up successful"
