#!/bin/bash
set -e

REPO_DIR="/home/ct/catty-reminders-app"
BRANCH=$1

cd "$REPO_DIR"

git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH"
git pull origin "$BRANCH"

DEPLOY_REF=$(git rev-parse HEAD)

sed -i '/^DEPLOY_REF=/d' .env 2>/dev/null || true
echo "DEPLOY_REF=$DEPLOY_REF" >> .env
echo "> Deploy ref updated: $DEPLOY_REF"

if [ ! -d ".venv" ]; then
    python3 -m venv .venv/
fi

source .venv/bin/activate

pip install -r requirements.txt


sudo systemctl restart app.service
echo "Deployment completed!"
