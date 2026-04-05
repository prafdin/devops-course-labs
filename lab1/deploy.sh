#!/bin/bash
set -e

APP_DIR="/home/pyshisha/devops-lab/catty-reminders-app"
VENV="/home/pyshisha/devops-lab/venv"
LOG="/home/pyshisha/devops-lab/deploy.log"

# Определяем текущую ветку автоматически
cd $APP_DIR
CURRENT_BRANCH=$(git branch --show-current)

echo "[$(date)] === DEPLOY START (branch: $CURRENT_BRANCH) ===" >> $LOG

git fetch origin >> $LOG 2>&1
git reset --hard "origin/$CURRENT_BRANCH" >> $LOG 2>&1

source $VENV/bin/activate
pip install -r requirements.txt >> $LOG 2>&1

COMMIT=$(git rev-parse HEAD | cut -c1-8)
mkdir -p $APP_DIR/static
echo "$COMMIT" > $APP_DIR/static/version.txt

sudo systemctl restart catty-app

echo "[$(date)] === DEPLOY OK (commit: $COMMIT, branch: $CURRENT_BRANCH) ===" >> $LOG
