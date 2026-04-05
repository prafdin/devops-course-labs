#!/bin/bash
set -e

APP_DIR="/home/pyshisha/devops-lab/catty-reminders-app"
VENV="/home/pyshisha/devops-lab/venv"
LOG="/home/pyshisha/devops-lab/deploy.log"

cd $APP_DIR
BRANCH=$(git branch --show-current)

echo "[$(date)] === DEPLOY START (branch: $BRANCH) ===" >> $LOG

git fetch origin >> $LOG 2>&1
git reset --hard "origin/$BRANCH" >> $LOG 2>&1

source $VENV/bin/activate
pip install -r requirements.txt >> $LOG 2>&1

COMMIT=$(git rev-parse HEAD | cut -c1-8)

# ПРАВИЛЬНЫЙ ПУТЬ
DEPLOY_FILE="$APP_DIR/templates/pages/login.html"
if [ -f "$DEPLOY_FILE" ]; then
    sed -i "s/deployref\" content=\"[^\"]*/deployref\" content=\"$COMMIT/" $DEPLOY_FILE
    echo "Updated deployref in login.html to $COMMIT" >> $LOG
fi

sudo systemctl restart catty-app

echo "[$(date)] === DEPLOY OK (commit: $COMMIT, branch: $BRANCH) ===" >> $LOG
