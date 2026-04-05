#!/bin/bash

set -e

REPO_DIR="/home/vboxuser/catty-reminders-app"
COMMIT_SHA=$1

echo "> Deploying commit $COMMIT_SHA"

cd "$REPO_DIR"
echo "> Directory changed to $REPO_DIR"

git fetch origin

git reset --hard "$COMMIT_SHA"
echo "> Switched to commit $COMMIT_SHA"

DEPLOY_REF=$(git rev-parse HEAD)
echo "DEPLOY_REF=$DEPLOY_REF" > "$REPO_DIR/.env"
echo "> Deploy ref: $DEPLOY_REF"

if [ ! -d ".venv" ]; then
    echo "> Virtual environment not found, creating..."
    python3 -m venv .venv/
fi

source .venv/bin/activate
echo "> Virtual environment activated"

if [ -f "requirements.txt" ]; then
    echo "> Installing/Updating requirements"
    pip install -r requirements.txt
fi

echo "> Deploy ref updated in .env: $DEPLOY_REF"

sudo chown vboxuser:vboxuser "$REPO_DIR/.env"
chmod 644 "$REPO_DIR/.env"

echo "> Restarting app..."
sudo systemctl daemon-reload 
sudo systemctl restart app.service

echo "> Done"
