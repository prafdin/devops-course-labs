#!/bin/bash
set -e

COMMIT_SHA=$1  # ← принимаем SHA из webhook

APP_DIR="/home/pyshisha/devops-lab/catty-reminders-app"
VENV="/home/pyshisha/devops-lab/venv"
LOG="/home/pyshisha/devops-lab/deploy.log"

cd $APP_DIR
git fetch origin
git reset --hard "$COMMIT_SHA"  # ← переключаемся на точный коммит

source $VENV/bin/activate
pip install -r requirements.txt >> $LOG 2>&1

COMMIT=$(git rev-parse HEAD | cut -c1-8)
DEPLOY_FILE="$APP_DIR/templates/pages/login.html"
sed -i "s/deployref\" content=\"[^\"]*/deployref\" content=\"$COMMIT/" $DEPLOY_FILE

sudo systemctl restart catty-app

echo "[$(date)] === DEPLOY OK (commit: $COMMIT) ===" >> $LOG
