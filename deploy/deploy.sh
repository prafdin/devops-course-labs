#!/bin/bash
set -e
REPO_DIR="/mnt/c/Users/Sergo/Documents/prog/university/catty-reminders-app"
BRANCH=$1
COMMIT_SHA=$2

cd "$REPO_DIR"

git fetch origin
git checkout -B "$BRANCH" "origin/$BRANCH"
git reset --hard "origin/$BRANCH"

CLEAN_REF=$(echo $COMMIT_SHA | tr -d '\r' | tr -d ' ')
echo "DEPLOY_REF=$CLEAN_REF" > "$REPO_DIR/.env.deploy"
chmod 644 "$REPO_DIR/.env.deploy"

sudo systemctl restart app.service
echo "Done! Ref: $CLEAN_REF"