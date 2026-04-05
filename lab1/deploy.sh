#!/bin/bash
set -e

COMMIT_SHA=$1
APP_DIR="/home/pyshisha/devops-lab/catty-reminders-app"
VENV="/home/pyshisha/devops-lab/venv"
LOG="/home/pyshisha/devops-lab/deploy.log"

cd $APP_DIR
git fetch origin
git reset --hard "$COMMIT_SHA"

# Быстрая проверка изменений в requirements.txt
if git diff HEAD@{1} --name-only | grep -q "requirements.txt"; then
    echo "[$(date)] requirements.txt changed, installing..." >> $LOG
    source $VENV/bin/activate
    pip install -r requirements.txt >> $LOG 2>&1
else
    echo "[$(date)] requirements.txt unchanged" >> $LOG
    source $VENV/bin/activate
fi

COMMIT=$(git rev-parse HEAD)

DEPLOY_FILE="$APP_DIR/templates/pages/login.html"
sed -i "s/deployref\" content=\"[^\"]*/deployref\" content=\"$COMMIT/" $DEPLOY_FILE

sudo systemctl restart catty-app
echo "[$(date)] === DEPLOY OK (commit: $COMMIT) ===" >> $LOG
