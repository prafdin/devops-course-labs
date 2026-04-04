#!/bin/bash

set -e

REPO_DIR="/home/ct/catty-reminders-app"
BRANCH=$1

cd "$REPO_DIR"

git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH"
git pull origin "$BRANCH"

DEPLOY_REF=$(git rev-parse HEAD)
echo "DEPLOY_REF=$DEPLOY_REF" > /home/ct/catty-reminders-app/.env.deploy

if [ ! -d ".venv" ]; then
    python3 -m venv .venv/
fi

source .venv/bin/activate

pip install -r requirements.txt

sudo systemctl restart app.service
