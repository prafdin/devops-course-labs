#!/bin/bash
set -e

cd /home/ct/catty-reminders-app/devops/lab1/webhook || exit 1

git fetch origin
git reset --hard origin/main
source ../.venv/bin/activate
pip install -r requirements.txt

DEPLOY_REF=$(git rev-parse HEAD)
echo "DEPLOY_REF=$DEPLOY_REF" > ../.env

sudo systemctl daemon-reload
sudo systemctl restart app.service

echo "Deployment done. Current DEPLOY_REF: $DEPLOY_REF"
