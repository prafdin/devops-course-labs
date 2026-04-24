#!/bin/bash
set -e

BRANCH=$1
REPO_URL="git@github.com:mzpdqk/catty-reminders-app.git"
APP_DIR="/home/mzpdqk/devops/catty-reminders-app"

echo "=== deploy: $BRANCH ==="

if [ -z "$BRANCH" ]; then
    echo "branch not provided"
    exit 1
fi

if [ ! -d "$APP_DIR/.git" ]; then
    echo "clone repo"
    git clone $REPO_URL $APP_DIR
fi

cd $APP_DIR

git fetch origin
git checkout -B $BRANCH origin/$BRANCH
git reset --hard origin/$BRANCH

DEPLOY_REF="$(git rev-parse HEAD)"
echo "DEPLOY_REF=$DEPLOY_REF" > "$APP_DIR/.env"

if [ -f "requirements.txt" ]; then
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi

    source venv/bin/activate
    pip install -r requirements.txt
fi

sudo systemctl restart app.service

echo "deploy done"
